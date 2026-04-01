import os
import pyreadr
import pandas as pd
from pathlib import Path

def migrate_rda_to_parquet(src_dir: str, dest_dir: str):
    """
    Migrates .rda files from src_dir to .parquet in dest_dir.
    """
    src_path = Path(src_dir)
    dest_path = Path(dest_dir)
    
    # Ensure destination exists
    dest_path.mkdir(parents=True, exist_ok=True)
    
    rda_files = list(src_path.glob("*.rda"))
    print(f"Found {len(rda_files)} .rda files in {src_dir}")
    
    for rda_file in rda_files:
        print(f"Migrating {rda_file.name}...")
        try:
            # Read RDA
            result = pyreadr.read_r(str(rda_file))
            
            # result is a dictionary-like object mapping object names to DataFrames
            for obj_name, df in result.items():
                if not isinstance(df, pd.DataFrame):
                    print(f"  Skipping non-DataFrame object '{obj_name}' in {rda_file.name}")
                    continue
                
                # If there's only one object, name the parquet file after the rda file
                # Otherwise, use the object name
                if len(result) == 1:
                    parquet_name = rda_file.stem + ".parquet"
                else:
                    parquet_name = f"{rda_file.stem}_{obj_name}.parquet"
                
                output_path = dest_path / parquet_name
                print(f"  Saving to {output_path}")
                df.to_parquet(output_path, index=False)
                
        except Exception as e:
            print(f"  Error migrating {rda_file.name}: {e}")

if __name__ == "__main__":
    src = "/Users/awhitworth/github_projects/synthACS/data"
    dest = "/Users/awhitworth/github_projects/pysynthACS/src/pysynthacs/data"
    migrate_rda_to_parquet(src, dest)
