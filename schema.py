from sqlalchemy import Column, VARCHAR, INT, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class ROAD_INFO(Base):
    __tablename__ = "road_info"
    idx = Column(INT, nullable=False, autoincrement=True, primary_key=True)
    road_name = Column(VARCHAR, nullable=False)
    road_type = Column(INT, nullable=False)
    region = Column(VARCHAR, nullable=False)
    speed_limit = Column(INT, nullable=True)


class CHILD_PROTECTION_ROAD(Base):
    __tablename__ = "child_protection_road"
    idx = Column(INT, nullable=False, autoincrement=True, primary_key=True)
    name = Column(VARCHAR, nullable=False)
    road_name = Column(VARCHAR, nullable=False)
    region = Column(VARCHAR, nullable=False)


class USER_INFO(Base):
    __tablename__ = "user_info"
    idx = Column(INT, nullable=False, autoincrement=True, primary_key=True)
    nick_name = Column(VARCHAR, nullable=False)
    wallet = Column(VARCHAR, nullable=False)
    balance = relationship("USER_BALANCE")
    session = relationship("USER_SESSION")


class USER_BALANCE(Base):
    __tablename__ = "user_balance"
    idx = Column(INT, nullable=False, autoincrement=True, primary_key=True)
    wallet = Column(VARCHAR,  ForeignKey("user_info.wallet"))
    sdt = Column(INT, nullable=False )
    smt = Column(INT, nullable=False)
    sol = Column(INT, nullable=False)
    usdc = Column(INT, nullable=False)




class USER_SESSION(Base):
    __tablename__ = "user_session"
    idx = Column(INT, nullable=False, autoincrement=True, primary_key=True)
    user = Column(VARCHAR, ForeignKey("user_info.wallet", onupdate="CASCADE", ondelete="CASCADE"))
    session = Column(VARCHAR, nullable = True)