"""
F1 Data Pipeline DAG - Medallion Architecture

This DAG orchestrates the extraction and processing of Formula 1 race data 
using FastF1 for building ML prediction datasets.

Architecture:
- Bronze Layer: Raw extracted data (race, practice, qualifying, sprint, weather, standings)
- Silver Layer: Transformed/joined data per event
- Gold Layer: Aggregated season data for ML

Schedule: Currently manual trigger for historical data  
"""
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List
import fastf1
import pandas as pd
import structlog
from airflow import DAG
from airflow.sdk import task
from airflow.providers.standard.operators.empty import EmptyOperator

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import extractors - auto-configures FastF1 cache
from extractors import (
    RaceExtractor,
    PracticeExtractor,
    QualifyingExtractor,
    SprintExtractor,
    WeatherExtractor,
    StandingsExtractor,
)

# Import utils for storage
from utils.storage_io import (
    get_bronze_path, 
    get_silver_path, 
    get_gold_path,
    write_parquet,
    read_parquet,
    read_parquet_safe
)

logger = structlog.get_logger()

#========================================================================================================================================

default_argments={
        "retries": 2,
        "retry_delay": timedelta(minutes=2),
    }

@dag(
    dag_id="f1_data_pipeline",
    description="Extract and process F1 race data for ML prediction (Medallion Architecture)",
    schedule=None,  # No schedule, manual trigger only
    start_date=datetime(2024, 1, 1),
    catchup=True,
    max_active_runs=1,
    default_args=default_argments,
    params={
        "seasons": [2024],
        "final_race_num": 23
    },
    tags=["f1", "data-pipeline", "ml", "medallion"],
)
def dag():
    
    @task(task_id="get_season_events")
    def get_season_events(season=dag.params.get("seasons"), final_race_num=dag.params.get("final_race_num")) -> List[Dict[str, Any]]:
        return EventsExtractor(start_season=season[0], end_season=season[-1], end_race_num=final_race_num).get_events()
