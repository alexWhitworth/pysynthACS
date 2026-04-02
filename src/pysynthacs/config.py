import os
from typing import Optional

# Global API Key storage
_CENSUS_API_KEY: Optional[str] = os.environ.get("CENSUS_API_KEY")

def set_api_key(key: str) -> None:
    """
    Sets the global Census API key for all pullers.
    """
    global _CENSUS_API_KEY
    _CENSUS_API_KEY = key

def get_api_key() -> Optional[str]:
    """
    Retrieves the current global Census API key.
    """
    return _CENSUS_API_KEY
