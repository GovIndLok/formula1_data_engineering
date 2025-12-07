from typing import Literal
from pydantic import BaseModel, Field

# Import components to compose the final model, but typically we flatten it for the final CSV/Parquet row
# We will redefine fields here to ensure a flat structure as per DataSchema.md

class RacePredictionRow(BaseModel):
    """
    Complete row for ML training - 26 columns matching DataSchema.md
    """
    # 1. Session identifiers (8 columns)
    race_id: int
    session_code: str
    target_session: Literal["Sprint", "Race"]
    is_sprint_weekend: bool
    season: int
    race_num: int
    track_id: str
    total_laps: int
    
    # 2. Driver/Team (2 columns)
    driver_tla: str
    team_name: str
    
    # 3. Practice (2 columns)
    fp_best_time: float | None
    fp_position: int | None
    
    # 4. Qualifying (3 columns)
    quali_pos: int
    quali_best_time: float
    quali_gap_pole: float
    
    # 5. Starting Grid (1 column)
    starting_grid: int
    
    # 6. Sprint Data (2 columns)
    sprint_result: int | None
    sprint_points: int | None
    
    # 7. Weather (4 columns)
    air_temp: float
    track_temp: float
    humidity: float
    rainfall: float
    
    # 8. Championship Context (2 columns)
    championship_pos: int = Field(alias="champ_pos") # Allow alias to match schema if needed
    championship_points: int = Field(alias="champ_points")
    
    # 9. Recent Form (1 column)
    last_3_avg_position: float = Field(alias="last_3_avg")
    
    # 10. Target (1 column)
    finishing_position: int
    
    class Config:
        populate_by_name = True
