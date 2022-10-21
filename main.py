from http.client import HTTPResponse
from typing import List
from loguru import logger
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from model import Result, Road, Balance
from user import query_user_balance
import fastapi
from logic import check_status, start_game, end_game

app = fastapi.FastAPI()

origins = [
    "*"
]

app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])


class Loc(BaseModel):
    locations: list
    user: str
    start_at: int


class Start(BaseModel):
    user: str


class Stop(BaseModel):
    user: str
    start_at: int


class User(BaseModel):
    user: str


@app.get("/")
def home():
    return {"message": "Welecom Home!"}


# 연결
@app.post("/connect")
def connect():
    return {"message": "connected"}


# 게임 시작
@app.post("/start")
def start(start: Start):
    start_time = start_game(start.user)
    return {"message": "game started", "user": start.user, "start_at": start_time}


# 진행 중
@app.post("/check", response_model=Road)
def check(loc: Loc):
    return check_status(loc.locations, loc.user, loc.start_at)


# 게임 종료
@app.post("/stop", response_model=Result)
def stop(stop: Stop):
    return end_game(stop.user, stop.start_at)

# 유저 잔고 조회


@app.post("/user/balance", response_model=Balance)
def get_balance(user: User):
    return query_user_balance(user.user)

