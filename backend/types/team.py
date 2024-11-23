from enum import Enum
from pydantic import BaseModel, Field, constr

class TeamType(str, Enum):
    """
    Enum for the type of team.
    """
    personal = "personal"
    organization = "organization"


class CreateTeamDto(BaseModel):
    name: str = Field(..., example="My Team")
    type: TeamType = Field(..., example=TeamType.personal)
    plan_id: int = Field(...)  # The ID of the associated plan
    owner_id: constr(min_length=1) = Field(...) # auth0_id of the owner


    class Config:
        extra = "forbid"  # Prevent extra fields during model creation
        schema_extra = {
            "example": {
                "name": "The Innovators",
                "type": "organization",
                "plan_id": 1,  # Example plan ID
                "owner_id": "auth0|user123",
            }
        }


