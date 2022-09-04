from sqlalchemy import Column, TEXT,VARCHAR, INT
from sqlalchemy.orm import declarative_base
import pymysql

Base = declarative_base()

class ROAD_INFO(Base):
    __tablename__="road_info"
    idx = Column(INT, nullable=False, autoincrement=True, primary_key=True)
    road_name = Column(VARCHAR, nullable=False)
    road_type = Column(INT, nullable=False)
    region = Column(VARCHAR, nullable=False)