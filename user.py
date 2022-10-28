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

from datetime import date
from datetime import datetime

# 중복된 이름이 존재하면 False  없으면 True
def check_nick_duplicate(_nick_name: str) -> bool:
    query = session.query(USER_INFO.nick_name).filter(
        USER_INFO.nick_name.like(_nick_name)).all()
    result = [i.nick_name for i in query]
    logger.debug("duplicates : " + str(len(result)))

    return False if len(result) > 0 else True

# 유저 생성
# Input: user input 닉네임, Phantom wallet 지갑주소
# Output: False if nick_name or wallet exist.  True if no redundant entry.
def create_user(_nick_name: str, _wallet: str) -> bool:
    #지갑주소 duplicate 체크
    redundant_wallet = session.query(USER_INFO).filter(
            USER_INFO.wallet == _wallet).all()
    if len(redundant_wallet) > 0:
        logger.debug("dupicate wallet {}".format(_wallet))
        return False
        #백엔드에서 검토. 동일한 지갑주소가 2개이상 등록되어 있음.

    redundant_nickname = session.query(USER_INFO).filter(
            USER_INFO.nick_name == _nick_name).all()
    if len(redundant_nickname) > 0:
        logger.debug("nick name duplicates {}".format(_nick_name))
        raise HTTPException(404, "USER nick_name exist")
        #프론트에서 처리. 닉네임 존재함을 팝업으로 알림.
        return False

    # No duplicate of wallet and nickname
    session.add(USER_INFO(nick_name=_nick_name, wallet=_wallet))
    session.commit()
    create_balances(_wallet)

    return True

    # #nick_name duplicate 발견시
    # if check_nick_duplicate(_nick_name):
    #     session.add(USER_INFO(nick_name=_nick_name, wallet=_wallet))
    #     session.commit()
    #     create_balances(_wallet)
    #     return True
    # else:
    #     logger.debug("nick name duplicates")
    #     raise HTTPException(404, "USER nick_name exist")
    #     #프론트에서 처리. 닉네임 존재함을 팝업으로 알림.
    # return False


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
# Input: wallet 주소 (user identity로도 쓰임)
# Output: model.Balance object
# Balance(wallet: str, sdt: int, smt: int, sol: int, usdc: int)
def query_user_balance(_wallet: str) -> Balance:
    # query input wallet주소와 일치하는 USER_BALANCE.wallet 을 리턴.
    try:
        r = session.query(USER_BALANCE).filter(
            USER_BALANCE.wallet == _wallet).one()
    except MultipleResultsFound, e:
        print e
        #백엔드에서 검토. 동일한 지갑주소가 2개이상 등록되어 있음.
    except NoResultFound, e:
        print e
        raise HTTPException(404, "NO USER FOUND")
        #사용자가 이미 앱에서 조회했는데 지갑주소 등록되어 있지 않기 떄문에, raise Exception. 
        #Exception은 프론트 엔드에서 처리. 첫 화면으로 forwarding해서 지갑 연결부터 유도.

    return Balance(wallet=r.wallet, sdt=r.sdt, smt=r.smt, sol=r.sol, usdc=r.usdc)

# Daily 채굴정보
# Input: wallet 주소 (user identity로도 쓰임)
# Output: model.Today object 
# Today(wallet : str, rewarded_distance (채굴거리) : float, reward (채굴량) : float, max_rewarded_distance (하루채굴거리Max cap) : float, max_reward (하루채굴량Max cap) : float, last_drive (마지막운전종료시간): datetime)
def get_today_user_status(_wallet: str) -> Today:
    current = get_unix_time_stamp()

    dt = date.today()
    print(datetime.combine(dt, datetime.min.time()))    
    # 오늘 00:00분
    midnight_behind = datetime.combine(dt, datetime.min.time())

    # query 마지막 운전 종료시간이 오늘 자정을 넘긴 DRIVE_HISTORY 모두 return
    result = session.query(DRIVE_HISTORY).filter(
        DRIVE_HISTORY.user == _wallet).filter(DRIVE_HISTORY.end_at > midnight_behind).all()

    # 오늘 운전기록 없으면 None return
    if len(result) == 0:
        # raise HTTPException(404, "NO DRIVE HISTORY")
        return None

    # DRIVE_HISTORY 룹 돌면서 mining_distance와 mining_tokens 를 합산
    for row in result:
        daily_mining_distance += row.mining_distance
        daily_mining_tokens += row.total_mining
        
    # Today object에 리턴.
    return Today(wallet=_wallet, rewarded_distance=daily_mining_distance, reward=daily_mining_tokens, max_rewarded_distance=20, max_reward=20, last_drive=result[len(result)-1].end_at)
