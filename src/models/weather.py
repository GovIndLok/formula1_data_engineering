from pydantic import BaseModel, Field

class WeatherData(BaseModel):
    """
    Weather conditions for a session.
    """
    air_temp: float = Field(description="Mean air temperature in Celsius")
    track_temp: float = Field(description="Mean track temperature in Celsius")
    humidity: float = Field(ge=0, le=100, description="Mean humidity percentage")
    rainfall: float = Field(ge=0, description="Total rainfall in mm")
