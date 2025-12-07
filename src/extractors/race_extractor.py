import fastf1
import pandas as pd
import structlog
from typing import Any, Dict, List

logger = structlog.get_logger()

class RaceExtractor:
    """
    Extracts race session results using FastF1.
    """
    def __init__(self, season: int, race_num: int):
        self.season = season
        self.race_num = race_num
        self.session = None

    def load_session(self):
        """Loads the race session from FastF1."""
        try:
            # Get session object
            self.session = fastf1.get_session(self.season, self.race_num, 'Race')
            
            # Load only results data to be efficient (no telemetry/laps needed for just results)
            # Weather might be needed later but this is just race_extractor
            self.session.load(weather=False, telemetry=False, laps=False)
            
            logger.info("Race session loaded", 
                       season=self.season, 
                       race_num=self.race_num, 
                       event=self.session.event['Location'])
                       
        except Exception as e:
            logger.error("Failed to load race session", 
                        season=self.season, 
                        race_num=self.race_num, 
                        error=str(e))
            raise

    def extract_results(self) -> List[Dict[str, Any]]:
        """
        Extracts race results and finishing positions for all drivers.
        
        Returns:
            List of dictionaries containing driver results. 
            Includes 'finishing_position' which is the target variable.
        """
        if not self.session:
            self.load_session()
        
        results = []
        
        # FastF1 results are in self.session.results (pandas DataFrame)
        if self.session.results is None or self.session.results.empty:
            logger.warning("No results found for session", season=self.season, race_num=self.race_num)
            return []

        # 1. Get Winner's Time (Position 1)
        winner_time = None
        try:
            # Filter for Position 1. Use 1.0 (float) as Position is float
            winner_mask = self.session.results['Position'] == 1.0
            if winner_mask.any():
                # Take the first one (should be only one)
                winner_time = self.session.results.loc[winner_mask, 'Time'].iloc[0]
        except Exception as e:
            logger.warning("Could not determine winner time", error=str(e))

        for _, row in self.session.results.iterrows():
            driver_tla = row['Abbreviation']
            pos = row['Position']
            
            # Skip if no position (DNS/WD)
            if pd.isna(pos):
                logger.warning("Skipping driver with no position (DNS/WD)", driver=driver_tla)
                continue
                
            # Handle Finishing Position
            status = row['Status']
            is_dnf = row['ClassifiedPosition'] in ['R', 'D', 'N', 'W']
            
            # --- Time Calculation Logic ---
            # User Feedback: "driver in the top position we their proper timing and then the subsequent position the time difference is shown as the time"
            # We need to convert gaps to total time.
            
            total_time_sec = None
            time_val = row['Time']
            
            if pd.notna(time_val):
                if pos == 1.0:
                    # Winner has absolute time
                    total_time_sec = time_val.total_seconds()
                elif winner_time is not None:
                    # For others, check if 'Time' is likely a gap (smaller than winner time)
                    # This heuristic handles cases where FastF1 returns gaps instead of absolute times
                    if time_val < winner_time:
                         # It's a gap, add to winner's time
                         total_time_sec = (winner_time + time_val).total_seconds()
                    else:
                         # It's already absolute (e.g. +1 Lap might be handled differently, but if it's a time > winner, it's absolute)
                         total_time_sec = time_val.total_seconds()
                else:
                    # Fallback if no winner time found
                    total_time_sec = time_val.total_seconds()

            result_data = {
                'driver_tla': driver_tla,
                'team_name': row['TeamName'],
                'finishing_position': int(pos),
                'starting_grid': int(row['GridPosition']),
                'points': float(row['Points']),
                'status': str(status),
                'is_dnf': is_dnf,
                'laps_completed': int(row['Laps']),
                'time_sec': total_time_sec
            }
            results.append(result_data)
            
        return results

    def get_session_info(self) -> Dict[str, Any]:
        """Returns metadata about the race session."""
        if not self.session:
            self.load_session()
            
        event = self.session.event
        return {
            'race_id': 0, # Placeholder, will be generated/mapped later
            'season': self.season,
            'race_num': self.race_num,
            'track_id': event['Location'],
            'session_code': f"{event['Location'][:3].upper()}{self.season}{self.race_num}_RACE", # Example format
            'total_laps': int(self.session.total_laps) if pd.notna(self.session.total_laps) else 0
        }
