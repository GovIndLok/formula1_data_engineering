from pydantic import BaseModel, Field

class DriverData(BaseModel):
    """
    Driver performance and standing data.
    """
    driver_tla: str = Field(min_length=3, max_length=3, description="Three-letter driver abbreviation (e.g., VER)")
    driver_id: str = Field(description="Unique driver identifier from FastF1")
    team_id: str = Field(description="Unique team/constructor identifier from FastF1")
    
    # Practice Data
    fp_best_time: float | None = Field(default=None, description="Best practice lap time in seconds")
    fp_position: int | None = Field(default=None, ge=1, le=20, description="Position in practice session")
    
    # Qualifying Data
    quali_pos: int = Field(ge=1, le=20, description="Qualifying position")
    quali_best_time: float = Field(description="Best qualifying lap time in seconds")
    quali_gap_pole: float = Field(ge=0, description="Time gap to pole position in seconds")
    
    # Grid & Sprint
    starting_grid: int = Field(ge=1, le=20, description="Actual starting grid position for the target session")
    sprint_result: int | None = Field(default=None, ge=1, le=20, description="Finishing position in Sprint (if applicable)")
    sprint_points: int | None = Field(default=None, ge=0, description="Points scored in Sprint")
    
    # Championship Context
    championship_pos: int = Field(ge=1, le=20, description="Driver championship position before race")
    championship_points: int = Field(ge=0, description="Driver championship points before race")
    
    # Form
    last_3_avg_position: float = Field(ge=1, le=20, description="Average finishing position in last 3 races")
