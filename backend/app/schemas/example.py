from pydantic import BaseModel, Field


class ExampleSchema(BaseModel):
    """Example schema for request validation."""

    name: str = Field(..., description="Full name of the person", examples=["Jane Doe"])
    age: int = Field(..., ge=0, description="Age in years", examples=[30])
