import fastf1
import pandas as pd
import structlog
from typing import Any, Dict, List

logger = structlog.get_logger()

class SprintExtractor:
    """
    Extracts sprint session results using FastF1.
    Only runs if the event is determined to be a Sprint weekend.
    """
    def __init__(self, season: int, race_num: int):
        self.season = season
        self.race_num = race_num
        self.session = None

    def _is_sprint_weekend(self) -> bool:
        """
        Checks if the event is a sprint weekend.
        User Logic: Check if 'EventFormat' (or similar) contains 'sprint'.
        """
        try:
            event = fastf1.get_event(self.season, self.race_num)
            # FastF1 Event object attributes: EventFormat
            if 'sprint' in str(event['EventFormat']).lower():
                return True
            return False
        except Exception as e:
            logger.warning("Could not determine event format", error=str(e))
            return False

    def load_sprint_race_session(self):
        """Loads the Sprint Race session from FastF1."""
        if not self._is_sprint_weekend():
            return

        try:
            self.session = fastf1.get_session(self.season, self.race_num, 'Sprint')
            self.session.load(weather=False, telemetry=False, laps=False)
            logger.info("Sprint Race session loaded")
        except Exception as e:
            logger.error("Failed to load sprint race session", error=str(e))
            raise

    def load_sprint_qualifying_session(self):
        """
        Loads the Sprint Qualifying (Shootout) session.
        Handles naming convention differences (Shootout vs Qualifying).
        """
        if not self._is_sprint_weekend():
            return

        # Determine session name based on season or try/except
        # 2023: Sprint Shootout
        # 2024+: Sprint Qualifying (likely)
        session_name = 'Sprint Shootout' if self.season == 2023 else 'Sprint Qualifying'
        
        try:
            self.sq_session = fastf1.get_session(self.season, self.race_num, session_name)
            # Need laps/results. Sprint Quali has SQ1/SQ2/SQ3
            self.sq_session.load(weather=False, telemetry=False, laps=True)
            logger.info(f"{session_name} loaded")
        except Exception:
            # Fallback to other name if first failed
            fallback = 'Sprint Qualifying' if session_name == 'Sprint Shootout' else 'Sprint Shootout'
            try:
                self.sq_session = fastf1.get_session(self.season, self.race_num, fallback)
                self.sq_session.load(weather=False, telemetry=False, laps=True)
                logger.info(f"{fallback} loaded (fallback)")
            except Exception as e:
                logger.error("Failed to load sprint qualifying session", error=str(e))
                # Don't raise, just log, as maybe some weekends differ
                self.sq_session = None

    def extract_sprint_race_results(self) -> List[Dict[str, Any]]:
        """
        Extracts sprint race results (Position, Points).
        """
        if not self._is_sprint_weekend():
            return []

        if not self.session:
            self.load_sprint_race_session()
        
        if self.session is None or self.session.results is None or self.session.results.empty:
             return []

        results = []
        for _, row in self.session.results.iterrows():
            if pd.isna(row['Position']): continue
            
            results.append({
                'driver_tla': row['Abbreviation'],
                'driver_id': str(row['DriverId']),
                'team_id': str(row['TeamId']),
                'sprint_result': int(row['Position']),
                'sprint_points': float(row['Points']) if pd.notna(row['Points']) else 0.0
            })
        return results

    def extract_sprint_qualifying_results(self) -> List[Dict[str, Any]]:
        """
        Extracts Sprint Qualifying results (Pos, Gap to Pole).
        Returns fields: quali_pos, quali_gap_pole (for Sprint target).
        """
        if not self._is_sprint_weekend():
            return []

        if not hasattr(self, 'sq_session') or not self.sq_session:
            self.load_sprint_qualifying_session()
            
        if self.sq_session is None or self.sq_session.results is None or self.sq_session.results.empty:
            return []

        # Logic matches QualifyingExtractor as data structure is similar (Q1/Q2/Q3)
        curr_cols = self.sq_session.results.columns
        # Priority order: Q3 > Q2 > Q1 (Latest session time counts)
        priority_cols = [c for c in ['Q3', 'Q2', 'Q1'] if c in curr_cols]

        def get_best_sq_time(row_data):
            """
            Returns the time from the most recent qualifying session participated in.
            Priority: Q3 -> Q2 -> Q1
            """
            for col in priority_cols:
                val = row_data[col]
                if pd.notna(val):
                    return val
            return None

        # Determine Sprint Pole Time
        pole_time = None
        try:
            pole_sitter = self.sq_session.results.loc[self.sq_session.results['Position'] == 1.0]
            if not pole_sitter.empty:
                pole_time = get_best_sq_time(pole_sitter.iloc[0])
        except Exception:
            pass

        results = []
        for _, row in self.sq_session.results.iterrows():
            pos = row['Position']
            if pd.isna(pos): continue

            # We need best time for Gap to Pole calculation
            best_lap_td = get_best_sq_time(row)
            
            gap_to_pole = None
            if pos == 1.0:
                gap_to_pole = 0.0
            elif best_lap_td is not None and pole_time is not None:
                gap_to_pole = (best_lap_td - pole_time).total_seconds()

            results.append({
                'driver_tla': row['Abbreviation'],
                'driver_id': str(row['DriverId']),
                'team_id': str(row['TeamId']),
                'quali_pos': int(pos),
                # 'quali_best_time': removed as not required
                'quali_gap_pole': gap_to_pole,
                'is_sprint_qualifying': True
            })
            
        return results
