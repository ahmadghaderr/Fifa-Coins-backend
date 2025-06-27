from pydantic import BaseModel, confloat

class RateModel(BaseModel):
    rate: confloat(gt=0)
