"""Request and response models."""

from datetime import datetime
from pydantic import BaseModel, field_validator, Field


class QueryInput(BaseModel):
    """QueryInput"""

    query: str = Field(
        example="Give me the average temperature and humidity for sensor 1 in the last week."
    )


class SensorMetric(BaseModel):
    """SensorMetric"""

    sensor: str = Field(example="sensor1")
    metric: str = Field(example="temperature")
    unit: str = Field(example="C")
    value: float = Field(example=10)


class QueryMeta(BaseModel):
    """QueryMeta"""

    sensor: list[str]
    metric: list[str]
    aggregation: str
    date: datetime | None


class SensorInput(SensorMetric):
    """SensorInput"""

    @field_validator("sensor", "metric")
    @classmethod
    def remove_all_spaces(cls, v: str) -> str:
        return v.replace(" ", "")


class SensorMetricResult(BaseModel):
    """SensorMetricResult"""

    data: list[SensorMetric]
    meta: QueryMeta
