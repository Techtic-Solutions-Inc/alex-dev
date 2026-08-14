import pytest
from app.schemas.example import ExampleSchema
from pydantic import ValidationError


def test_example_schema_validation() -> None:
    example = ExampleSchema(name="Jane Doe", age=30)
    assert example.name == "Jane Doe"
    assert example.age == 30


def test_example_schema_rejects_negative_age() -> None:
    with pytest.raises(ValidationError):
        ExampleSchema(name="Jane Doe", age=-1)
