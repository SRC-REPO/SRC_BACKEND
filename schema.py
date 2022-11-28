from sqlalchemy import Column, VARCHAR, INT, ForeignKey, BOOLEAN, FLOAT, BIGINT
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class SpeedLimit(Base):
    __tablename__ = 'speed_limit_osm'
    id = Column(INTEGER, primary_key=True, autoincrement=True)
    #road name
    road_name = Column(VARCHAR(50), nullable = True)
    #OSM navigation기능을 위한 road name. 약간 backup road name임. (미사용)
    destination = Column(VARCHAR(50), nullable = True)
    #OSM Relation id (app backend 에서 미사용)
    relation_id = Column(VARCHAR(20), nullable = False)
    #OSM Way id (app backend 에서 미사용)
    way_id = Column(VARCHAR(20), nullable = False)
    #OSM Node id. GPS 가까운 점 snap후 해당 위치에 제한속도 query시 시용 (사용)
    node_id = Column(VARCHAR(20), nullable = False, unique = True)
    #OSM 도로타입. 특이하게 tag 이름이 highway임.  _link (램프), residential(길단위 작은 길), trunk/motorway/primary (도로 단위)
    highway = Column(VARCHAR(50), nullable = True)
    #Node의 latitude 위도
    lat = Column(VARCHAR(20), nullable = False)
    #Node의 longitude 경도
    lon = Column(VARCHAR(20), nullable = False)
    #도로제한속도
    speed_limit = Column(INTEGER, nullable = False, default = 0)
    #DB에 생성한 timestamp
    created_at = Column(DateTime, default=datetime.now, nullable = True)
    updated_at = Column(DateTime, default=datetime.now, nullable = True)

class CHILD_PROTECTION_ROAD(Base):
    __tablename__ = "child_protection_road"
    idx = Column(INT, nullable=False, autoincrement=True, primary_key=True)
    name = Column(VARCHAR, nullable=False)
    road_name = Column(VARCHAR, nullable=False)
    region = Column(VARCHAR, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable = True)
    updated_at = Column(DateTime, default=datetime.now, nullable = True)


class USER_INFO(Base):
    __tablename__ = "user_info"
    idx = Column(INT, nullable=False, autoincrement=True, primary_key=True)
    #유저 닉네임.  베타 앱에서 지원.
    nick_name = Column(VARCHAR, nullable=False)
    #User connect 된 지갑주소
    wallet = Column(VARCHAR, nullable=False)
    balance = relationship("USER_BALANCE")
    session = relationship("USER_SESSION")
    nft_info = relationship("NFT_INFO")
    drive_record = relationship("DRIVE_RECORD")
    drive_history = relationship("DRIVE_HISTORY")
    created_at = Column(DateTime, default=datetime.now, nullable = True)
    updated_at = Column(DateTime, default=datetime.now, nullable = True)


class NFT_INFO(Base):
    __tablename__ = "nft_info"
    idx = Column(INT, nullable=False, autoincrement=True, primary_key=True)
    #NFT collection
    collection = Column(VARCHAR, nullable=False)
    #NFT unique id
    number = Column(INT, nullable=False)
    #NFT rarity
    rarity = Column(VARCHAR, nullable=False)
    #NFT holder wallet address 
    owner = Column(VARCHAR, ForeignKey("user_info.wallet"), nullable=True)
    #Tire max energy 100
    max_durability = Column(INT, nullable=False)
    #Tire current energy
    current_durability = Column(FLOAT, nullable=False)
    #NFT 채굴시도거리 수명
    lifetime_mining_distance = Column(INT, nullable=False)
    #NFT 남아있는 채굴시도거리 수명
    remaining_mining_distance = Column(FLOAT, nullable=False)
    #NFT user가 장착여부
    equip = Column(BOOLEAN, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable = True)
    updated_at = Column(DateTime, default=datetime.now, nullable = True)


class USER_BALANCE(Base):
    __tablename__ = "user_balance"
    idx = Column(INT, nullable=False, autoincrement=True, primary_key=True)
    #지갑주소
    wallet = Column(VARCHAR,  ForeignKey("user_info.wallet"))
    #SDT 
    sdt = Column(BIGINT, nullable=False )
    #SMT
    smt = Column(BIGINT, nullable=False)
    #SOL
    sol = Column(BIGINT, nullable=False)
    #USDC
    usdc = Column(BIGINT, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable = True)
    updated_at = Column(DateTime, default=datetime.now, nullable = True)


#List of finished DRIVE_RECORD
class DRIVE_HISTORY(Base):
    __tablename__ = "drive_history"
    idx = Column(INT, nullable=False, autoincrement=True, primary_key=True)
    #user = wallet address
    user = Column(VARCHAR, ForeignKey("user_info.wallet"), nullable=False)
    #Drive 누르면, timestamp
    start_at = Column(INT, nullable=False)
    #Finish 누르면, timestamp
    end_at = Column(INT, nullable=True)
    #start_at ~ end_at 사이에 이루어진
    #총 운전거리
    driving_distance = Column(FLOAT, nullable=False)
    #속도 위반 없는 운전거리
    safe_driving_distance = Column(FLOAT, nullable=False)
    #채굴시도거리
    mining_distance = Column(FLOAT, nullable=False)
    #보상성공거리
    valid_mining_distance = Column(FLOAT, nullable=False)    
    #채굴량
    total_mining = Column(FLOAT, nullable=False)
    #운전시간
    running_time = Column(INT, nullable=False)
    #장착한 nft number
    nft_number = Column(VARCHAR, nullable=False)
    #nft rarity
    nft_rarity = Column(VARCHAR, nullable=False)
    #에너지(타이어) 사용량
    nft_usage = Column(FLOAT, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable = True)
    updated_at = Column(DateTime, default=datetime.now, nullable = True)



class USER_SESSION(Base):
    __tablename__ = "user_session"
    idx = Column(INT, nullable=False, autoincrement=True, primary_key=True)
    user = Column(VARCHAR, ForeignKey("user_info.wallet"))
    session = Column(VARCHAR, nullable=True)
