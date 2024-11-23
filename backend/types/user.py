from pydantic import BaseModel, EmailStr, constr

class CreateUserDto(BaseModel):
    name: str
    email: EmailStr
    auth0_id: constr(min_length=1)  # Assuming auth0_id is a required string

    class Config:
        extra = "forbid" # Prevent extra fields during model creation
        schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "auth0_id": "auth0|user123",
            }
        }

