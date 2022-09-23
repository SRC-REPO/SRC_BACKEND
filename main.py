from http.client import HTTPResponse
from typing import List
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from model import Road
import fastapi

from logic import check_status, start_game, end_game

app = fastapi.FastAPI()

origins = [
    "*"
]

app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])


    
@app.get("/")
def home():
    return {"message": "Welecom Home!"}
    
@app.post("/check" ,response_model=Road)
def check(_locations: List, _user : str, _start_at : int):
    return check_status(_locations, _user, _start_at)

# 연결 
@app.post("/connect")
def connect():
    return {"message": "connected"}
# 게임 시작
@app.post("/start")
def start(_user : str):
    start_game(_user)
    return {"message" : "game started"}


# 게임 종료
@app.post("/stop")
def stop(_user : str, _start_at : int):
    end_game(_user, _start_at)
    return {"message" : "game stopped"}

