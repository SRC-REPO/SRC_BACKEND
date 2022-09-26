
from pydantic import BaseModel

class Road(BaseModel):
    location : str
    city : str
    speed : float
    speed_limit : float
    start_at : int
    driving_distance : float
    safe_driving_distance : float
    mining_distance : float
    total_mining: float
    total_nft_usage :float
    

class Result(BaseModel):
    user : str
    start_at : int
    end_at : int
    driving_distance : float
    safe_driving_distance : float
    mining_distance : float
    total_mining: float
    total_nft_usage : float
    running_time : int
    


class Balance(BaseModel):
    wallet : str
    sdt : int
    smt : int
    sol : int
    usdc : int
