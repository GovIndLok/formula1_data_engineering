import fastf1
import pandas as pd
import structlog
from typing import Any, Dict, List

logger = structlog.get_logger()

class QualifyingExtractor:
    """
    Extracts qualifying session results using FastF1.
    Calculates:
    - Qualifying Position
    - Best Qualifying Time (fastest of Q1/Q2/Q3)
    - Gap to Pole
    """
    def __init__(self, season: int, race_num: int):
        self.season = season
        self.race_num = race_num
        self.session = None

    def load_session(self):
        """Loads the qualifying session from FastF1."""
        try:
            self.session = fastf1.get_session(self.season, self.race_num, 'Qualifying')
            # Load laps to ensure best lap data is present if needed, but results usually sufficient
            self.session.load(weather=False, telemetry=False, laps=True)
            
            logger.info("Qualifying session loaded", 
                       season=self.season, 
                       race_num=self.race_num, 
                       location=self.session.event['Location'])
                       
        except Exception as e:
            logger.error("Failed to load qualifying session", 
                        season=self.season, 
                        race_num=self.race_num, 
                        error=str(e))
            raise

    def extract_results(self) -> List[Dict[str, Any]]:
        """
        Extracts qualifying results.
        """
        if not self.session:
            self.load_session()
        
        results = []
        
        if self.session.results is None or self.session.results.empty:
             logger.warning("No results found for qualifying session")
             return []

        # Identify Qualifying columns present in the dataframe
        # Usually ['Q1', 'Q2', 'Q3']
        curr_cols = self.session.results.columns
        # Priority order: Q3 > Q2 > Q1 (Latest session time counts)
        priority_cols = [c for c in ['Q3', 'Q2', 'Q1'] if c in curr_cols]
        
        def get_best_q_time(row_data):
            """
            Returns the time from the most recent qualifying session participated in.
            Priority: Q3 -> Q2 -> Q1
            """
            for col in priority_cols:
                val = row_data[col]
                if pd.notna(val):
                    return val
            return None

        # 1. Determine Pole Position Time (Benchmark)
        # We take the best time of the driver who got Position 1. 
        # (Technically usually Q3 time, but we use their best valid time for consistency if they went faster in Q2)
        pole_time = None
        try:
            pole_sitter = self.session.results.loc[self.session.results['Position'] == 1.0]
            if not pole_sitter.empty:
                pole_time = get_best_q_time(pole_sitter.iloc[0])
        except Exception as e:
            logger.warning("Could not determine pole time", error=str(e))

        for _, row in self.session.results.iterrows():
            driver_tla = row['Abbreviation']
            driver_id = str(row['DriverId'])
            team_id = str(row['TeamId'])
            pos = row['Position']
            
            # Skip if no position
            if pd.isna(pos):
                continue

            # Get Best Time from Q1/Q2/Q3
            best_lap_td = get_best_q_time(row)
            best_time_sec = best_lap_td.total_seconds() if best_lap_td else None
            
            # Calculate Gap to Pole
            gap_to_pole = None
            if pos == 1.0:
                gap_to_pole = 0.0
            elif best_lap_td is not None and pole_time is not None:
                # Absolute gap
                delta = best_lap_td - pole_time
                gap_to_pole = delta.total_seconds()
            
            result_data = {
                'driver_tla': driver_tla,
                'driver_id': driver_id,
                'team_id': team_id,
                'quali_pos': int(pos),
                'quali_best_time': best_time_sec,
                'quali_gap_pole': gap_to_pole
            }
            results.append(result_data)
            
        return results
