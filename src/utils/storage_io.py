"""
Storage I/O Utilities for Medallion Architecture

Provides consistent file path generation and parquet I/O for:
- Bronze Layer: Raw extracted data
- Silver Layer: Transformed/joined data  
- Gold Layer: Aggregated season data
"""
import os
from pathlib import Path
from typing import Optional, Union
import pandas as pd
import structlog

logger = structlog.get_logger()

# Base data path from environment or compute from module location
# This ensures the path works regardless of working directory
def _get_default_data_path() -> Path:
    """Get the default data path based on module location."""
    # This file is at: src/utils/storage_io.py
    # Project root is 2 levels up, data dir is project_root/data
    module_dir = Path(__file__).resolve().parent  # src/utils
    project_root = module_dir.parent.parent  # project root
    return project_root / "data"

# Check for env var first, fall back to computed path
_env_path = os.getenv("DATA_OUTPUT_PATH", "").strip()
DATA_OUTPUT_PATH = Path(_env_path) if _env_path else _get_default_data_path()


# =============================================================================
# Path Generators
# =============================================================================

def get_bronze_path(season: int, race_num: int, data_type: str) -> Path:
    """
    Get the bronze layer path for raw extracted data.
    
    Args:
        season: Race season year
        race_num: Race number in the season
        data_type: Type of data (race, practice, qualifying, sprint, weather, standings)
    
    Returns:
        Path to the bronze parquet file
    """
    return DATA_OUTPUT_PATH / "bronze" / f"season_{season}" / f"race_{race_num}" / f"{data_type}.parquet"


def get_silver_path(season: int, race_num: int) -> Path:
    """
    Get the silver layer path for transformed/joined event data.
    
    Args:
        season: Race season year
        race_num: Race number in the season
    
    Returns:
        Path to the silver parquet file
    """
    return DATA_OUTPUT_PATH / "silver" / f"season_{season}" / f"race_{race_num}" / "event_joined.parquet"


def get_gold_path(season: int) -> Path:
    """
    Get the gold layer path for final aggregated season data.
    
    Args:
        season: Race season year
    
    Returns:
        Path to the gold parquet file
    """
    return DATA_OUTPUT_PATH / "gold" / f"season_{season}" / "race_predictions.parquet"


# =============================================================================
# I/O Operations
# =============================================================================

def write_parquet(data: Union[Dict[str, Any], List[Dict[str, Any]]], path: Path) -> str:
    """
    Write a DataFrame to parquet format, creating parent directories if needed.
    
    Args:
        df: DataFrame to write
        path: Target path for the parquet file
    
    Returns:
        String path to the written file
    """
    # Ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert to DataFrame
    if isinstance(data, list):
        df = pd.DataFrame(data)
    elif isinstance(data, dict):
        df = pd.DataFrame([data])
    else:
        raise ValueError("Data must be a list or dictionary")

    # Write to parquet
    df.to_parquet(path, engine='pyarrow', index=False)
    
    logger.info("Wrote parquet file", path=str(path), rows=len(df), columns=len(df.columns))
    
    return str(path)


def read_parquet(path: Path | str) -> pd.DataFrame:
    """
    Read a parquet file into a DataFrame.
    
    Args:
        path: Path to the parquet file (string or Path object)
    
    Returns:
        DataFrame with the parquet contents
    
    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(f"Parquet file not found: {path}")
    
    df = pd.read_parquet(path, engine='pyarrow')
    
    logger.info("Read parquet file", path=str(path), rows=len(df), columns=len(df.columns))
    
    return df


def read_parquet_safe(path: Path | str) -> Optional[pd.DataFrame]:
    """
    Read a parquet file, returning None if it doesn't exist or is empty.
    
    Args:
        path: Path to the parquet file
    
    Returns:
        DataFrame or None if file doesn't exist
    """
    try:
        return read_parquet(path)
    except FileNotFoundError:
        logger.warning("Parquet file not found", path=str(path))
        return None
    except Exception as e:
        logger.error("Failed to read parquet file", path=str(path), error=str(e))
        return None
