from pydantic import BaseModel, confloat

class CalculationInput(BaseModel):
    player_name: str
    buy_price: confloat(gt=0)
    real_price: confloat(gt=0)
    