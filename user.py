from email.policy import HTTP
from loguru import logger
from db import engineconn
from model import Balance, Today
from schema import DRIVE_HISTORY, USER_INFO, USER_SESSION, USER_BALANCE, ROAD_INFO
from sqlalchemy.sql import text
from sqlalchemy import update
from logic import get_unix_time_stamp
from fastapi import HTTPException
engine = engineconn()
session = engine.session_maker()


# 중복된 이름이 존재하면 False  없으면 True
def check_nick_duplicate(_nick_name: str) -> bool:
    query = session.query(USER_INFO.nick_name).filter(
        USER_INFO.nick_name.like(_nick_name)).all()
    result = [i.nick_name for i in query]
    logger.debug("duplicates : " + str(len(result)))

    return False if len(result) > 0 else True


# 유저 생성
def create_user(_nick_name: str, _wallet: str) -> bool:
    if check_nick_duplicate(_nick_name):
        session.add(USER_INFO(nick_name=_nick_name, wallet=_wallet))
        session.commit()
        create_balances(_wallet)
        return True
    else:
        logger.debug("nick name duplicates")

    return False


# 잔고 초기화
def create_balances(_wallet: str) -> bool:
    session.add(USER_BALANCE(wallet=_wallet, sdt=0, smt=0, sol=0, usdc=0))
    session.commit()

    return True


# 세션 저장 / 나중에 sha3로 암호화
def create_session(_wallet: str, _session: str) -> bool:
    session.add(USER_SESSION(user=_wallet, session=_session))
    session.commit()
    return True


# 유저 잔고 조회
def query_user_balance(_wallet: str) -> Balance:
    result = session.query(USER_BALANCE).filter(
        USER_BALANCE.wallet == _wallet).all()
    if len(result) == 0:
        raise HTTPException(404, "NO USER FOUND")

    [r] = result
    balance = Balance(wallet=r.wallet, sdt=r.sdt,
                      smt=r.smt, sol=r.sol, usdc=r.usdc)

    return balance


def get_today_user_status(_wallet: str) -> Today:
    current = get_unix_time_stamp()
    before_24h = current - 86400

    result = session.query(DRIVE_HISTORY).filter(
        DRIVE_HISTORY.user == _wallet).filter(DRIVE_HISTORY.end_at > before_24h).all()

    if len(result) == 0:
        raise HTTPException(404, "NO DRIVE HISTORY")

    [r] = result

    return Today(wallet=_wallet, rewarded_distance=r.mining_distance, reward=r.total_mining, max_rewarded_distance=20, max_reward=20, last_drive=r.end_at)
