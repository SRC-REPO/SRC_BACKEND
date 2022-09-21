from loguru import logger
from db import engineconn
from model import Balance
from schema import SDT_BALANCES, USER_INFO, SMT_BALANCES, SOL_BALANCES, USDC_BALANCES, USER_SESSION
from sqlalchemy.sql import text
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
    session.add(SDT_BALANCES(wallet=_wallet, amount=0))
    session.commit()
    session.add(SMT_BALANCES(wallet=_wallet, amount=0))
    session.commit()
    session.add(SOL_BALANCES(wallet=_wallet, amount=0))
    session.commit()
    session.add(USDC_BALANCES(wallet=_wallet, amount=0))
    session.commit()

    return True


# 세션 저장 / 나중에 sha3로 암호화
def create_session(_wallet: str, _session: str) -> bool:
    session.add(USER_SESSION(user=_wallet, session=_session))
    session.commit()

    return True


# 유저 잔고 조회
def query_user_balance(_wallet: str) -> Balance:
    result = session.query(text("wallet"), text("sdt"), text("smt"), text("sol"), text("usdc")).from_statement(text(
        "select b.wallet, b.sdt, b.smt, b.sol, usdc.amount as usdc from (select a.wallet, a.sdt, a.smt, sol.amount as sol from (select sdt.wallet, sdt.amount as sdt, smt.amount as smt from sdt_balances as sdt inner join smt_balances as smt) as a inner join sol_balances as sol) as b inner join usdc_balances as usdc;")).all()

    return Balance(wallet=result[0][0], sdt=result[0][1], smt=result[0][2], sol=result[0][3], usdc=result[0][4])


# create_user("deankang", "BZqkHr5uwTUQpPqgLSr5erWDhx4VHz4DzN98fNsUVwwa")
# create_balances("BZqkHr5uwTUQpPqgLSr5erWDhx4VHz4DzN98fNsUVwwa")
balance = query_user_balance("BZqkHr5uwTUQpPqgLSr5erWDhx4VHz4DzN98fNsUVwwa")
print(balance)
