from sqlalchemy import Column, TEXT, INT
from sqlalchemy.orm import declarative_base
import pymysql

Base = declarative_base()

class ROAD_TYPE(Base):
    __tablename__="road_type"
    idx = Column(INT, nullable=False, autoincrement=True, primary_key=True)
    road_name = Column(TEXT, nullable=True)
    road_type = Column(INT, nullable=True)

