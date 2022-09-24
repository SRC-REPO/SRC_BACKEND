from sqlalchemy import Column, VARCHAR, INT, ForeignKey, BOOLEAN, FLOAT
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
    nft_info = relationship("NFT_INFO")
    drive_record = relationship("DRIVE_RECORD")
    drive_history= relationship("DRIVE_HISTORY")

class NFT_INFO(Base):
    __tablename__ = "nft_info"
    idx = Column(INT, nullable = False, autoincrement = True, primary_key = True)
    collection = Column(VARCHAR, nullable = False)
    number = Column(INT, nullable = False)
    rarity = Column(VARCHAR, nullable = False)
    owner = Column(VARCHAR, ForeignKey("user_info.wallet"), nullable = True)
    max_durability = Column(INT, nullable = False)
    current_durability = Column(FLOAT, nullable = False)
    equip = Column(BOOLEAN, nullable = True)


class USER_BALANCE(Base):
    __tablename__ = "user_balance"
    idx = Column(INT, nullable=False, autoincrement=True, primary_key=True)
    wallet = Column(VARCHAR,  ForeignKey("user_info.wallet"))
    sdt = Column(INT, nullable=False )
    smt = Column(INT, nullable=False)
    sol = Column(INT, nullable=False)
    usdc = Column(INT, nullable=False)

class DRIVE_RECORD(Base):
    __tablename__ = "drive_record"
    idx = Column(INT, nullable = False, autoincrement = True, primary_key = True)
    user = Column(VARCHAR, ForeignKey("user_info.wallet"), nullable = False)
    start_at = Column(INT, nullable = False)
    end_at = Column(INT, nullable = True)
    driving_distance  = Column(FLOAT, nullable = False)
    safe_driving_distance = Column(FLOAT, nullable = False)
    mining_distance = Column(FLOAT, nullable = False)
    total_mining = Column(FLOAT, nullable = False)
    running_time = Column(INT, nullable = False)
    nft_rarity = Column(VARCHAR,nullable = False)
    nft_usage = Column(FLOAT, nullable= False)


class DRIVE_HISTORY(Base):
    __tablename__ = "drive_history"
    idx = Column(INT, nullable = False, autoincrement = True, primary_key = True)
    user = Column(VARCHAR, ForeignKey("user_info.wallet"), nullable = False)
    start_at = Column(INT, nullable = False)
    end_at = Column(INT, nullable = True)
    driving_distance  = Column(FLOAT, nullable = False)
    safe_driving_distance = Column(FLOAT, nullable = False)
    mining_distance = Column(FLOAT, nullable = False)
    total_mining = Column(FLOAT, nullable = False)
    running_time = Column(INT, nullable = False)
    nft_rarity = Column(VARCHAR,nullable = False)
    nft_usage = Column(FLOAT, nullable= False)


class USER_SESSION(Base):
    __tablename__ = "user_session"
    idx = Column(INT, nullable=False, autoincrement=True, primary_key=True)
    user = Column(VARCHAR, ForeignKey("user_info.wallet"))
    session = Column(VARCHAR, nullable = True)