from sqlalchemy import *
from sqlalchemy.orm import sessionmaker


app = {
    'name': 'mysql+pymysql',
    'user': 'root',
    'password': '0aL2uYxT78Sw',
    'host': 'lhcsnelm.sldb.iwinv.net',
    'dbconn': 'src',
    'port': 3306
}


conn_string = f'{app["name"]}://{app["user"]}:{app["password"]}@{app["host"]}:{app["port"]}/{app["dbconn"]}'


class engineconn:

    def __init__(self) -> None:
        self.engine = create_engine(
            conn_string, pool_size=100, max_overflow=200, pool_recycle=500)

    def session_maker(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        return session

    def connection(self):
        conn = self.engine.connect()
        return conn
