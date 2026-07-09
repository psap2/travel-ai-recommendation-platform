from pydantic import BaseModel, Field


class Activity(BaseModel):
    time: str                                   # e.g. "Morning"
    title: str = Field(min_length=1)
    stay_id: str | None = None                  # must reference a real stay if set


class DayPlan(BaseModel):
    day: int = Field(ge=1)
    summary: str = Field(min_length=1)
    activities: list[Activity] = Field(min_length=1)


class Itinerary(BaseModel):
    city: str
    days: list[DayPlan] = Field(min_length=1)
