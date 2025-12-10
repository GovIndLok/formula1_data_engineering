"""
FastF1 Cache Configuration

Provides a centralized cache configuration for all extractors.
This ensures FastF1 caches data in the project's data/cache directory.
"""
import os
from pathlib import Path

import fastf1

# Cache path - use project's data/cache directory
def _get_cache_path() -> Path:
    """Get the cache path based on module location."""
    # This file is at: src/extractors/__init__.py
    # Project root is 2 levels up, cache dir is project_root/data/cache
    module_dir = Path(__file__).resolve().parent  # src/extractors
    project_root = module_dir.parent.parent  # project root
    return project_root / "data" / "cache"

# Check for env var first, fall back to computed path
_env_cache = os.getenv("FASTF1_CACHE_PATH", "").strip()
CACHE_PATH = Path(_env_cache) if _env_cache else _get_cache_path()

# Enable cache on module import
CACHE_PATH.mkdir(parents=True, exist_ok=True)
fastf1.Cache.enable_cache(str(CACHE_PATH))

# Export extractors for convenient importing
from .race_extractor import RaceExtractor
from .practice_extractor import PracticeExtractor
from .qualifying_extractor import QualifyingExtractor
from .sprint_extractor import SprintExtractor
from .weather_extractor import WeatherExtractor
from .standings_extractor import StandingsExtractor

__all__ = [
    'RaceExtractor',
    'PracticeExtractor', 
    'QualifyingExtractor',
    'SprintExtractor',
    'WeatherExtractor',
    'StandingsExtractor',
    'CACHE_PATH',
]
