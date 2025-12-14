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

    @task(task_id="split_events")
    def split_events(events: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        
        sprint_events = []
        race_events = []
        for event in events:
            if event["is_sprint_weekend"] == True:
                sprint_events.append(event)
            race_events.append(event)
        
        return [sprint_events, race_events]
    
    @task(task_id="extract_sprint_events")
    def extract_sprint_events(sprint_events: Dict[str, Any]) -> List[str]:
        sprint_events = SprintExtractor(sprint_events.season, sprint_events.race_num)
        # Sprint Qualifying
        sprint_quali = sprint_events.extract_sprint_qualifying_results()
        sprint_path = get_bronze_path(sprint_events.season, sprint_events.race_num, "sprint_quali")
        sprint_quali_path = write_parquet(sprint_quali, sprint_path)

        # Sprint Race
        sprint_race = sprint_events.extract_sprint_race_results()
        sprint_path = get_bronze_path(sprint_events.season, sprint_events.race_num, "sprint")
        sprint_path = write_parquet(sprint_race, sprint_path)
        
        # Sprint Session Info
        sprint_session_info = sprint_events.get_session_info()
        sprint_session_info_path = get_bronze_path(sprint_events.season, sprint_events.race_num, "sprint_session_info")
        sprint_session_info_path = write_parquet(sprint_session_info, sprint_session_info_path)

        return [sprint_quali_path, sprint_path, sprint_session_info_path]
    
    @task(task_id="extract_race_events")
    def extract_race_events(race_events: Dict[str, Any]) -> List[str]:
        race_events = RaceExtractor(race_events.season, race_events.race_num)
        quali_events = QualifyingExtractor(race_events.season, race_events.race_num)

        # Qualifying
        quali_results = quali_events.extract_results()
        quali_path = get_bronze_path(race_events.season, race_events.race_num, "quali")
        quali_path = write_parquet(quali_results, quali_path)

        # Race
        race_results = race_events.extract_results()
        race_path = get_bronze_path(race_events.season, race_events.race_num, "race")
        race_path = write_parquet(race_results, race_path)

        # Session Info
        session_info = race_events.get_session_info()
        session_info_path = get_bronze_path(race_events.season, race_events.race_num, "session_info")
        session_info_path = write_parquet(session_info, session_info_path)

        return [quali_path, race_path, session_info_path]
    
    @task(task_id="extract_pratice_events")
    def extract_pratice_events(pratice_events: Dict[str, Any]) -> List[str]:
        pratice_events = PracticeExtractor(pratice_events.season, pratice_events.race_num)
        pratice_events = pratice_events.extract_results()
        pratice_path = get_bronze_path(pratice_events.season, pratice_events.race_num, "practice")
        pratice_path = write_parquet(pratice_events, pratice_path)
        return [pratice_path]