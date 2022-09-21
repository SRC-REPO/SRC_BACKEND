
from pydantic import BaseModel

class Road(BaseModel):
    location : str
    city : str
    speed : float
    speed_limit : float


class Balance(BaseModel):
    wallet : str
    sdt : int
    smt : int
    sol : int
    usdc : int
    