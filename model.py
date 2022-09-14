
from pydantic import BaseModel

class Road(BaseModel):
    location : str
    city : str
    speed : float
    speed_limit : float
