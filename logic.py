from lzma import CHECK_ID_MAX
import math
import requests
from typing import List
from loguru import logger
import pandas as pd
from db import engineconn
from schema import ROAD_INFO
from sqlalchemy.sql import text

CHECK_INTERVAL = 5
# ROAD_RANK = {101: ("고속도로", 100), 102: ("도시고속화도로", 80), 103: ("일반국도", 50),
#              104: ("특별/광역시도", 50), 105: ("국가지원지방도", 50), 106: ("지방도", 50), 107: ("시군도", 50)}

engine = engineconn()
session = engine.session_maker()


def check_road(lat: float, lon: float) -> str:
    request_url = "http://49.247.33.61:5000/nearest/v1/driving/"
    param = str(lon)+","+str(lat)
    number = "?number="+str(3)
    response = requests.get(request_url+param+number).json()
    road_name = response['waypoints'][0]['name']
    return road_name


def on_road(locations: List) -> str:
    arr = dict()

    for location in locations:
        road = check_road(location[0], location[1])
        arr[road] = arr.get(road, 0) + 1

    def f1(x):
        return arr[x]
    mx = max(arr.keys(), key=f1)
    current_location = mx if arr[mx] > 1 else list(arr.keys())[-1]

    return current_location


def calcSpeed(before: List, after: List) -> float:

    distance = calcDistance(before, after)
    distance *= 3600 / CHECK_INTERVAL
    return round(distance, 1)


def calcDistance(before: List, after: List) -> float:
    theta = before[1] - after[1]
    dist = math.sin(deg2rad(before[0])) * math.sin(deg2rad(after[0])) + math.cos(
        deg2rad(before[0])) * math.cos(deg2rad(after[0])) * math.cos(deg2rad(theta))
    dist = rad2deg(math.acos(dist)) * 60 * 1.1515 * 1.609344
    return dist


def deg2rad(deg: float) -> float:
    return (deg * math.pi / 180.0)


def rad2deg(rad: float) -> float:
    return (rad * 180 / math.pi)


def check_status(locations: List) -> dict:
    location = on_road(locations)
    speed = calcSpeed(locations[-2], locations[-1])

    logger.debug("location : "+location+" speed : "+str(speed)+"km/h")
    return {"location": location, "speed": speed}


def read_csv():
    datasheet = pd.read_csv(
        "C:\\Users\\user\\Documents\\Maptest\\utils\\road_type.csv")
    df = datasheet.loc[:, ['도로등급', '도로명', '링크권역']]
    df = df.drop_duplicates()
    return df


# !!!!!! before running this function you should do truncate table you use !!!!!!
def migration_csv_to_sql():

    data = read_csv()
    print("total data length - " + str(len(data)))
    for i in range(1, len(data)):
        d = data.iloc[i]
        print(str(d['도로등급']) + str(d['도로명']) + str(d['링크권역']))
        session.add(
            ROAD_INFO(road_name=d['도로명'], road_type=d['도로등급'], region=d['링크권역']))
        session.commit()

# 중복되는 도로명 조회
# select road_name, count(road_name) from road_info group by road_name having count(road_name) > 1;


def query_road_type(road_name: str) -> int:
    query = session.query(ROAD_INFO).filter(
        ROAD_INFO.road_name.like(road_name))
    result = [i.road_type for i in query]

    return result


def query_duplicate():
    response = session.query(ROAD_INFO.road_name, text("duplicates")).from_statement(
        text("select road_name, count(road_name) as duplicates from road_info group by road_name having count(road_name) > 1")).all()
    result = [r[0] for r in response]

    return result


def check_duplicate():

    duplicates = query_duplicate()

    for name in duplicates:
        response = query_road_type(name)
        if 101 in response or 102 in response:
            s = [str(r) for r in response]
            print(name + " : " + ' '.join(s))



