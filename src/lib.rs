use numpy::{PyReadonlyArray1, PyReadonlyArray2};
use pyo3::prelude::*;
use rand::prelude::*;
use rand_pcg::Pcg64;

/// Result of the simulated annealing optimization.
#[pyclass]
pub struct AnnealingResult {
    /// Indices of individuals from the pool who form the best fit.
    #[pyo3(get)]
    pub best_indices: Vec<usize>,
    /// The final Total Absolute Error (TAE).
    #[pyo3(get)]
    pub final_tae: i32,
    /// Number of iterations actually performed.
    #[pyo3(get)]
    pub iterations: usize,
}

/// Optimizes a synthetic population using a Scale-Agnostic Modernized Hybrid algorithm.
/// 
/// This implementation uses pure fractional jump sizes that scale automatically 
/// from tiny census blocks (N=20) to massive counties (N=10M+).
#[pyfunction]
#[pyo3(signature = (pool_data, target_constraints, sample_size, max_iter=50000, p_accept=0.4, resample_size=None, tolerance=0, seed=42))]
pub fn optimize_population(
    pool_data: PyReadonlyArray2<i32>,           // Candidate pool (encoded as integers)
    target_constraints: Vec<PyReadonlyArray1<i32>>, // Target marginal counts
    sample_size: usize,
    max_iter: usize,
    p_accept: f64,
    resample_size: Option<usize>,
    tolerance: i32,
    seed: u64,
) -> PyResult<AnnealingResult> {
    let mut rng = Pcg64::seed_from_u64(seed);
    let n_pool = pool_data.shape()[0];
    let n_attr = pool_data.shape()[1];

    // 1. DYNAMIC JUMP CONSTANTS
    // Anchored to percentages so it scales across all population sizes.
    let initial_pct = 0.05; // 5% initial scrambling
    let target_pct = 0.01;  // 1% standard jump
    
    // The "base" jump size reached after initial cooling
    let base_jump = resample_size.unwrap_or(
        (sample_size as f64 * target_pct).max(1.0) as usize
    );
    
    // The "initial" jump size (always at least the base_jump and at least 1)
    let initial_jump = (sample_size as f64 * initial_pct)
        .max(base_jump as f64)
        .max(1.0) as usize;

    // 2. Initial Sample and State Setup
    let mut current_indices: Vec<usize> = (0..n_pool).choose_multiple(&mut rng, sample_size);
    let mut current_totals: Vec<Vec<i32>> = target_constraints
        .iter()
        .map(|tc| vec![0; tc.len()])
        .collect();

    let pool = pool_data.as_array();
    for &idx in &current_indices {
        for attr in 0..n_attr {
            let cat = pool[[idx, attr]] as usize;
            if cat < current_totals[attr].len() {
                current_totals[attr][cat] += 1;
            }
        }
    }

    let mut current_tae: i32 = 0;
    for (attr, target) in target_constraints.iter().enumerate() {
        let target_arr = target.as_array();
        for cat in 0..target_arr.len() {
            current_tae += (current_totals[attr][cat] - target_arr[cat]).abs();
        }
    }

    let mut iter = 0;

    // 3. Main Optimization Loop
    while iter < max_iter && current_tae > tolerance {
        // A. RE-ANNEALING (Temperature Spike every 1000 iterations)
        let spike_cycle = 1000;
        let progress_in_cycle = (iter % spike_cycle) as f64 / spike_cycle as f64;
        let current_temp = p_accept * (-3.0 * progress_in_cycle).exp(); 

        // B. FRACTIONAL DECAYING JUMP
        // Scales from initial_jump to base_jump over the first 10% of total iterations.
        let jump_size = if iter < (max_iter / 10) {
            let decay_prog = iter as f64 / (max_iter as f64 / 10.0).max(1.0);
            let current_size = initial_jump as f64 - (decay_prog * (initial_jump as f64 - base_jump as f64));
            current_size.max(1.0) as usize
        } else {
            base_jump
        };

        let mut new_tae = current_tae;
        let mut changes = Vec::with_capacity(jump_size);

        // C. PROPOSE BATCH SWAP
        for _ in 0..jump_size {
            let swap_pos = rng.gen_range(0..sample_size);
            let old_idx = current_indices[swap_pos];
            let new_idx = rng.gen_range(0..n_pool);
            if old_idx == new_idx { continue; }

            changes.push((swap_pos, old_idx, new_idx));

            // Delta-TAE logic
            for attr in 0..n_attr {
                let old_cat = pool[[old_idx, attr]] as usize;
                let new_cat = pool[[new_idx, attr]] as usize;
                if old_cat == new_cat { continue; }

                let target = target_constraints[attr].as_array();
                
                new_tae -= (current_totals[attr][old_cat] - target[old_cat]).abs();
                current_totals[attr][old_cat] -= 1;
                new_tae += (current_totals[attr][old_cat] - target[old_cat]).abs();

                new_tae -= (current_totals[attr][new_cat] - target[new_cat]).abs();
                current_totals[attr][new_cat] += 1;
                new_tae += (current_totals[attr][new_cat] - target[new_cat]).abs();
            }
        }

        // D. METROPOLIS ACCEPTANCE
        if new_tae < current_tae || rng.gen::<f64>() < current_temp {
            // ACCEPT
            for (pos, _, new_idx) in changes {
                current_indices[pos] = new_idx;
            }
            current_tae = new_tae;
        } else {
            // REJECT: Revert totals
            for (_, old_idx, new_idx) in changes {
                for attr in 0..n_attr {
                    let old_cat = pool[[old_idx, attr]] as usize;
                    let new_cat = pool[[new_idx, attr]] as usize;
                    if old_cat != new_cat {
                        current_totals[attr][old_cat] += 1;
                        current_totals[attr][new_cat] -= 1;
                    }
                }
            }
        }
        iter += 1;
    }

    Ok(AnnealingResult {
        best_indices: current_indices,
        final_tae: current_tae,
        iterations: iter,
    })
}

#[pymodule]
fn pysynthacs_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<AnnealingResult>()?;
    m.add_function(wrap_pyfunction!(optimize_population, m)?)?;
    Ok(())
}
