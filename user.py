from loguru import logger
from db import engineconn
from model import Balance
from schema import USER_INFO, USER_SESSION, USER_BALANCE, ROAD_INFO
from sqlalchemy.sql import text
from sqlalchemy import update
engine = engineconn()
session = engine.session_maker()


# 중복된 이름이 존재하면 False  없으면 True
def check_nick_duplicate(_nick_name: str) -> bool:
    query = session.query(USER_INFO.nick_name).filter(
        USER_INFO.nick_name.like(_nick_name))
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
    session.add(USER_BALANCE(wallet=_wallet, sdt = 0, smt = 0, sol = 0, usdc =0))
    session.commit()

    return True


# 세션 저장 / 나중에 sha3로 암호화
def create_session(_wallet: str, _session: str) -> bool:
    session.add(USER_SESSION(user=_wallet, session=_session))
    session.commit()
    return True


# 유저 잔고 조회
def query_user_balance(_wallet: str) -> Balance:
    result = session.query(USER_BALANCE).filter(USER_BALANCE.wallet == _wallet).all()
    result = [(r.wallet, r.sdt, r.smt, r.sol, r.usdc) for r in result][0]
    balance = Balance(wallet = result[0], sdt = result[1], smt = result[2], sol = result[3], usdc = result[4])

    return balance




# def update_speed_limit():
#     road_infos = session.query(ROAD_INFO).all()

#     for road in road_infos:
#         road_type = road.road_type
#         if road_type == 101:
#             road.speed_limit = 100
#         elif road_type == 102:
#             road.speed_limit = 80
#         else :
#             road.speed_limit = 50
#     session.commit()
# create_user("deankang", "BZqkHr5uwTUQpPqgLSr5erWDhx4VHz4DzN98fNsUVwwa")
# create_balances("BZqkHr5uwTUQpPqgLSr5erWDhx4VHz4DzN98fNsUVwwa")
# print(query_user_balance("BZqkHr5uwTUQpPqgLSr5erWDhx4VHz4DzN98fNsUVwwa"))

# update_speed_limit()