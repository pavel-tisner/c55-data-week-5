# Step 1 — Task 4: Pydantic Validation
# Define the WeatherReading model that every ingested record must pass.
# Both the API and CSV data flow through this model before reaching the database.
from pydantic import BaseModel, Field, field_validator


class WeatherReading(BaseModel):
    station: str = Field(..., min_length=1)
    timestamp: str = Field(..., min_length=1)
    temperature_c: float = Field(..., ge=-90, le=60)
    humidity_pct: int = Field(..., ge=0, le=100)

    @field_validator("station", mode="before")
    @classmethod
    def clean_station(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().title()
        return v
