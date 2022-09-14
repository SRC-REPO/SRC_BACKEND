from lzma import CHECK_ID_MAX
import math
import requests
from typing import List
from loguru import logger
from db import engineconn
from schema import ROAD_INFO
from sqlalchemy.sql import text
from model import Road

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

# 현재 도로 위치 반환 ex) 올림픽대로 
def on_road(locations: List) -> str:
    arr = dict()
    # 3점 각각의 도로 위치 
    for location in locations:
        road = check_road(location[0], location[1])
        arr[road] = arr.get(road, 0) + 1

    def f1(x):
        return arr[x]
    mx = max(arr.keys(), key=f1)
    current_location = mx if arr[mx] > 1 else list(arr.keys())[-1]
    return current_location

# 현재 속도 계산
def calcSpeed(before: List, after: List) -> float:

    distance = calcDistance(before, after)
    distance *= 3600 / CHECK_INTERVAL
    return round(distance, 1)

# 이전 위치에서 이동한 거리 계산 
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

# main function
def check_status(locations: List) -> dict:
    location = on_road(locations) # 현재 도로명
    speed = calcSpeed(locations[-2], locations[-1]) # 속도 
    _lat, _lon = locations[-1]
    city = check_city(_lat, _lon)
    city = city +"특별시" if city == "서울" else city
    road_types = query_road_type(location, city)
    speed_limit = check_speed_limit(road_types, location)
    logger.debug("location : "+location+" city : "+city+" speed : "+str(speed)+"km/h speed-limit : " +str(speed_limit))


    return Road(location= location, city= city, speed= speed, speed_limit= speed_limit)

def query_road_type(road_name: str, city : str) -> int:
    query = session.query(ROAD_INFO.road_type, ROAD_INFO.region).filter(
        ROAD_INFO.road_name.like(road_name)).filter(ROAD_INFO.region.like(city))
    result = [i.road_type for i in query]
    return result

def check_speed_limit(road_types : list, road_name : str) -> int:
    print(road_types)
    # 101 고속도로, 102 고속화도로 제외 전체 50km 일괄 적용
    for road_type in road_types:
        if road_type == 101 or road_type == 102 :
            logger.error("101, 102번 겹치는 도로 : "+ road_name)
    # 고속도로, 고속화 도로 구분 및 어린이 보호구역 구분 로직 추가 예정
    return 50 #default speed_limit

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


def check_city(lat : float, lon : float) -> str:
    request_url = "http://nominatim.openstreetmap.org/reverse?format=json&addressdetails=1&zoom=14&"
    url_param = "lon=" + str(lon) +"&lat="+str(lat)
    response = requests.get(request_url + url_param).json()
    return response['address']['city']
        


    


