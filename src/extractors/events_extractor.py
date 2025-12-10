import fastf1
import structlog

logger = structlog.get_logger()


class EventsExtractor:
    def __init__(self, start_season: int = 2024, end_season: int = 2024, end_race_num: int | None = None):
        self.start_season = start_season
        self.end_season = end_season
        self.end_race_num = end_race_num
        self.session = None
    
    def get_events(self) -> List[Dict[str, int | str | bool]]:
        """Loads the race schedule from FastF1."""

        logger.info("Loading race schedule", start_season=self.start_season, end_season=self.end_season)
        
        events = []
        for season in range(self.start_season, self.end_season + 1):
            season_events = fastf1.get_event_schedule(season)

            for idx, row in season_events.iterrows():
                if row['RoundNumber'] == 0:
                    continue

                if (self.end_race_num is not None) and (row['RoundNumber'] >= self.end_race_num) and (season >= self.end_season):
                    break

                is_sprint = 'sprint' in str(row.get('EventFormat', '')).lower()

                event = {
                    'season': season,
                    'race_num': int(row['RoundNumber']),
                    'location': row['Location'],
                    'country': row['Country'],
                    'event_name': row['EventName'],
                    'event_date': str(row['EventDate']),
                    'is_sprint_weekend': is_sprint,
                }
                events.append(event)
        
        logger.info("Race schedule loaded", start_season=self.start_season, end_season=self.end_season, num_events=len(events))
        return events