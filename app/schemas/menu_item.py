from pydantic import BaseModel, ConfigDict, Field, model_validator


class MenuItemCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    description: str
    price: float = Field(ge=0, allow_inf_nan=False)
    availability: bool = True


class MenuItemUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1)
    description: str | None = None
    price: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    availability: bool | None = None

    @model_validator(mode="after")
    def reject_explicit_null(self):
        if any(getattr(self, field) is None for field in self.model_fields_set):
            raise ValueError("Menu item fields cannot be null")
        return self


class MenuItem(BaseModel):
    id: str
    restaurant_id: str
    name: str
    description: str
    price: float = Field(ge=0, allow_inf_nan=False)
    availability: bool
