from pydantic import BaseModel, ConfigDict


class ToolInputBase(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)
