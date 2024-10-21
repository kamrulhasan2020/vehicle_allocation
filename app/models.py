from pydantic import BaseModel, ConfigDict, Field, BeforeValidator
from datetime import date, datetime
from typing import Optional, Annotated

PyObjectId = Annotated[str, BeforeValidator(str)]


class AllocationModel(BaseModel):
    employee_id: int
    vehicle_id: int
    driver_id: int
    allocation_date: date


class AllocationResponseModel(AllocationModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[PyObjectId] = Field(alias="_id", default=None)


class AllocationUpdateModel(BaseModel):
    allocation_date: Optional[date] = None


class FilterModel(BaseModel):
    employee_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    driver_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
