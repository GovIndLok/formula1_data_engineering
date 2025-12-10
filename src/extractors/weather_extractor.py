import fastf1
import pandas as pd
import structlog
from typing import Any, Dict

logger = structlog.get_logger()

class WeatherExtractor:
    """
    Extracts weather data from a FastF1 session.
    """
    def __init__(self, season: int, race_num: int, session_type: str = 'Race'):
        """
        Initialize the WeatherExtractor.
        
        Args:
            season: The F1 season year
            race_num: The race round number
            session_type: Type of session ('Race', 'Sprint', 'Qualifying', etc.)
        """
        self.season = season
        self.race_num = race_num
        self.session_type = session_type
        self.session = None

    def load_session(self):
        """Loads the session from FastF1 with weather data."""
        try:
            # Get session object
            self.session = fastf1.get_session(self.season, self.race_num, self.session_type)
            
            # Load weather data (no need for telemetry or laps for weather extraction)
            self.session.load(weather=True, telemetry=False, laps=False)
            
            logger.info("Session loaded for weather extraction", 
                       season=self.season, 
                       race_num=self.race_num,
                       session_type=self.session_type,
                       location=self.session.event['Location'])
                       
        except Exception as e:
            logger.error("Failed to load session for weather extraction", 
                        season=self.season, 
                        race_num=self.race_num,
                        session_type=self.session_type,
                        error=str(e))
            raise

    def extract_weather(self) -> Dict[str, Any]:
        """
        Extracts weather data from the session.
        
        Returns:
            Dictionary containing weather metrics:
            - air_temp: Mean air temperature in Celsius
            - track_temp: Mean track temperature in Celsius
            - humidity: Mean humidity percentage
            - rainfall: Total rainfall in mm
            
        Note: The 'pressure' field from the original predict.py is not included
        as it's not in the WeatherData model schema.
        """
        if not self.session:
            self.load_session()
        
        try:
            # Get weather data from the session
            weather = self.session.weather_data
            
            if weather is None or weather.empty:
                logger.warning("No weather data available for session",
                             season=self.season,
                             race_num=self.race_num,
                             session_type=self.session_type)
                return {
                    'air_temp': None,
                    'track_temp': None,
                    'humidity': None,
                    'rainfall': None
                }
            
            # Calculate weather metrics
            # Using mean for temperature and humidity
            # Using sum for rainfall (as most values might be 0)
            air_temp = weather['AirTemp'].mean() if 'AirTemp' in weather.columns else None
            track_temp = weather['TrackTemp'].mean() if 'TrackTemp' in weather.columns else None
            humidity = weather['Humidity'].mean() if 'Humidity' in weather.columns else None
            rainfall = weather['Rainfall'].sum() if 'Rainfall' in weather.columns else 0.0
            
            weather_data = {
                'air_temp': float(air_temp) if pd.notna(air_temp) else None,
                'track_temp': float(track_temp) if pd.notna(track_temp) else None,
                'humidity': float(humidity) if pd.notna(humidity) else None,
                'rainfall': float(rainfall) if pd.notna(rainfall) else 0.0
            }
            
            logger.info("Weather data extracted successfully",
                       season=self.season,
                       race_num=self.race_num,
                       session_type=self.session_type,
                       weather_data=weather_data)
            
            return weather_data
            
        except Exception as e:
            logger.error("Failed to extract weather data",
                        season=self.season,
                        race_num=self.race_num,
                        session_type=self.session_type,
                        error=str(e))
            raise

    def get_session_info(self) -> Dict[str, Any]:
        """Returns metadata about the session."""
        if not self.session:
            self.load_session()
            
        event = self.session.event
        return {
            'season': self.season,
            'race_num': self.race_num,
            'session_type': self.session_type,
            'track_id': event['Location'],
            'event_name': event['EventName'],
            'session_date': str(self.session.date) if hasattr(self.session, 'date') else None
        }
