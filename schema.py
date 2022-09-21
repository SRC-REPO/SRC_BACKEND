from sqlalchemy import Column, VARCHAR, INT, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class ROAD_INFO(Base):
    __tablename__ = "road_info"
    idx = Column(INT, nullable=False, autoincrement=True, primary_key=True)
    road_name = Column(VARCHAR, nullable=False)
    road_type = Column(INT, nullable=False)
    region = Column(VARCHAR, nullable=False)


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
    sdt = relationship("SDT_BALANCES")
    smt = relationship("SMT_BALANCES")
    sol = relationship("SOL_BALANCES")
    usdc = relationship("USDC_BALANCES")
    session = relationship("USER_SESSION")


class SDT_BALANCES(Base):
    __tablename__ = "sdt_balances"
    idx = Column(INT, nullable=False, autoincrement=True, primary_key=True)
    wallet = Column(VARCHAR,  ForeignKey("user_info.wallet"))
    amount = Column(INT, nullable=True)


class SMT_BALANCES(Base):
    __tablename__ = "smt_balances"
    idx = Column(INT, nullable=False, autoincrement=True, primary_key=True)
    wallet = Column(VARCHAR,  ForeignKey("user_info.wallet", onupdate="CASCADE", ondelete="CASCADE"))
    amount = Column(INT, nullable=True)


class SOL_BALANCES(Base):
    __tablename__ = "sol_balances"
    idx = Column(INT, nullable=False, autoincrement=True, primary_key=True)
    wallet = Column(VARCHAR,  ForeignKey("user_info.wallet",onupdate="CASCADE", ondelete="CASCADE"))
    amount = Column(INT, nullable=True)


class USDC_BALANCES(Base):
    __tablename__ = "usdc_balances"
    idx = Column(INT, nullable=False, autoincrement=True, primary_key=True)
    wallet = Column(VARCHAR,  ForeignKey("user_info.wallet", onupdate="CASCADE", ondelete="CASCADE"))
    amount = Column(INT, nullable=True)


class USER_SESSION(Base):
    __tablename__ = "user_session"
    idx = Column(INT, nullable=False, autoincrement=True, primary_key=True)
    user = Column(VARCHAR, ForeignKey("user_info.wallet", onupdate="CASCADE", ondelete="CASCADE"))
    session = Column(VARCHAR, nullable = True)