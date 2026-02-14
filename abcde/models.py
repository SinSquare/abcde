"""Request and response models."""

from datetime import datetime
from pydantic import BaseModel, field_validator


class QueryInput(BaseModel):
    """QueryInput"""

    query: str


class SensorMetric(BaseModel):
    """SensorMetric"""

    sensor: str
    metric: str
    unit: str
    value: float


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
