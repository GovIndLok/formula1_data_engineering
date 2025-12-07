import structlog
from typing import Any, Dict, List
from fastf1.ergast import Ergast

logger = structlog.get_logger()


class StandingsExtractor:
    """
    Extracts driver championship standings using FastF1's Ergast interface.
    """

    def __init__(self, season: int, race_num: int):
        """
        Initialize the StandingsExtractor.

        Args:
            season: The F1 season year
            race_num: The race round number (standings will be fetched for the round BEFORE this)
        """
        self.season = season
        self.race_num = race_num
        self.ergast = Ergast()

    def extract_standings(self) -> List[Dict[str, Any]]:
        """
        Extracts driver championship standings coming INTO this race.

        For Race N, this fetches standings after Race N-1.
        For Race 1, returns empty standings (everyone starts at 0).

        Returns:
            List of dictionaries containing driver standings:
            - driver_id: Driver code (e.g., 'VER', 'HAM')
            - championship_pos: Current championship position
            - championship_points: Total championship points
            - wins: Number of race wins

        Note: 'last_3_avg_position' is deferred to a future phase.
        """
        standings_list = []

        # For the first race, there are no prior standings
        if self.race_num <= 1:
            logger.info(
                "First race of season, no prior standings",
                season=self.season,
                race_num=self.race_num,
            )
            return []

        try:
            # Fetch standings after the previous round
            previous_round = self.race_num - 1
            response = self.ergast.get_driver_standings(
                season=self.season, round=previous_round
            )

            if response.content is None or len(response.content) == 0:
                logger.warning(
                    "No standings data returned from Ergast",
                    season=self.season,
                    round=previous_round,
                )
                return []

            # response.content[0] is a DataFrame with standings
            standings_df = response.content[0]

            for _, row in standings_df.iterrows():
                driver_data = {
                    "driver_id": row.get("driverCode", row.get("driverId", "")),
                    "championship_pos": int(row.get("position", 0)),
                    "championship_points": float(row.get("points", 0.0)),
                    "wins": int(row.get("wins", 0)),
                }
                standings_list.append(driver_data)

            logger.info(
                "Driver standings extracted successfully",
                season=self.season,
                race_num=self.race_num,
                standings_round=previous_round,
                num_drivers=len(standings_list),
            )

        except Exception as e:
            logger.error(
                "Failed to extract driver standings",
                season=self.season,
                race_num=self.race_num,
                error=str(e),
            )
            raise

        return standings_list

    def get_driver_standing(self, driver_id: str) -> Dict[str, Any] | None:
        """
        Get the standing for a specific driver.

        Args:
            driver_id: The driver code (e.g., 'VER', 'HAM')

        Returns:
            Dictionary with driver's standing data, or None if not found.
        """
        standings = self.extract_standings()

        for standing in standings:
            if standing["driver_id"] == driver_id:
                return standing

        logger.warning(
            "Driver not found in standings",
            driver_id=driver_id,
            season=self.season,
            race_num=self.race_num,
        )
        return None

    def get_session_info(self) -> Dict[str, Any]:
        """Returns metadata about the standings extraction context."""
        return {
            "season": self.season,
            "race_num": self.race_num,
            "standings_round": self.race_num - 1 if self.race_num > 1 else 0,
        }
