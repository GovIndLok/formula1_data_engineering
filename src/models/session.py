from typing import Literal
from pydantic import BaseModel, Field

class SessionIdentifier(BaseModel):
    """
    Uniquely identifies a specific session within a race weekend.
    """
    race_id: int = Field(description="Unique identifier for the race (e.g., 1654000)")
    session_code: str = Field(description="Human readable session code (e.g., 'MEX0103_SPRINT')")
    target_session: Literal["Sprint", "Race"] = Field(description="The session being predicted")
    is_sprint_weekend: bool = Field(description="Whether this is a sprint weekend structure")
    season: int = Field(ge=2018, description="Racing season year")
    race_num: int = Field(ge=1, le=30, description="Round number in the season")
    track_id: str = Field(description="Unique identifier for the track/circuit")
    total_laps: int = Field(gt=0, description="Total scheduled laps for the target session")
