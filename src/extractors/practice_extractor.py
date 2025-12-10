import fastf1
import pandas as pd
import structlog
from typing import Any, Dict, List

logger = structlog.get_logger()

class PracticeExtractor:
    """
    Extracts practice session data (FP1/FP3) using FastF1.
    Logic:
    - Sprint Weekend: Uses FP1 (only practice before competitive sessions start)
    - Standard Weekend: Uses FP3 (most representative session before Quali)
    """
    def __init__(self, season: int, race_num: int):
        self.season = season
        self.race_num = race_num
        self.session = None
        self.session_name = None

    def _determine_target_session(self) -> str:
        """Determines whether to use FP1 or FP3 based on event format."""
        try:
            event = fastf1.get_event(self.season, self.race_num)
            # Check event format for Sprint
            # fastf1 event object has 'EventFormat'
            if 'sprint' in event['EventFormat']:
                return 'Practice 1'
            else:
                return 'Practice 3'
        except Exception as e:
            logger.warning("Could not determine event format, defaulting to FP3", error=str(e))
            return 'Practice 3'

    def load_session(self):
        """Loads the target practice session."""
        target = self._determine_target_session()
        self.session_name = target
        
        try:
            self.session = fastf1.get_session(self.season, self.race_num, target)
            # Need laps=True to ensure best lap data is accurate if we need to calculate, 
            # but usually results has it. Let's load generic.
            self.session.load(weather=False, telemetry=False, laps=True)
            
            logger.info(f"{target} session loaded", 
                       season=self.season, 
                       race_num=self.race_num, 
                       location=self.session.event['Location'])
                       
        except Exception as e:
            logger.error(f"Failed to load {target}", 
                        season=self.season, 
                        race_num=self.race_num, 
                        error=str(e))
            raise

    def extract_results(self) -> List[Dict[str, Any]]:
        """
        Extracts practice results (Best Lap Time, Position).
        """
        if not self.session:
            self.load_session()
        
        results = []
        
        # ensure laps are loaded
        if self.session.laps is None or self.session.laps.empty:
             logger.warning("No laps found for practice session")
             return []

        # 1. Get Overall Fastest Lap (Benchmark)
        try:
            overall_fastest_lap = self.session.laps.pick_fastest()
            overall_best_time = overall_fastest_lap['LapTime']
        except Exception as e:
            logger.warning("Could not determine overall fastest lap", error=str(e))
            return []

        # Iterate through drivers from results to ensure we cover everyone
        for _, row in self.session.results.iterrows():
            # Basic info
            driver_tla = row['Abbreviation']
            driver_id = str(row['DriverId'])
            team_id = str(row['TeamId'])
            pos = row['Position']
            
            # Practice specific metrics: Gap to Best
            fp_delta_sec = None
            
            try:
                # Get driver's fastest lap manually
                driver_laps = self.session.laps.pick_drivers(driver_tla)
                if not driver_laps.empty:
                    driver_fastest = driver_laps.pick_fastest()
                    driver_time = driver_fastest['LapTime']
                    
                    if pd.notna(driver_time) and pd.notna(overall_best_time):
                        delta = driver_time - overall_best_time
                        fp_delta_sec = delta.total_seconds()
            except Exception as e:
                # Driver might not have set a time
                pass

            result_data = {
                'driver_tla': driver_tla,
                'driver_id': driver_id,
                'team_id': team_id,
                'fp_position': int(pos) if pd.notna(pos) else None,
                'fp_best_time': fp_delta_sec, # This is now the GAP/DELTA, not absolute time
                'session_used': self.session_name
            }
            results.append(result_data)
            
        return results
