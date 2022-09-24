from cmath import log
from lzma import CHECK_ID_MAX
import math
from operator import is_
from optparse import check_choice
import requests
from typing import List
from loguru import logger
from db import engineconn
from schema import ROAD_INFO, NFT_INFO, DRIVE_RECORD, USER_BALANCE, DRIVE_HISTORY
from sqlalchemy.sql import text
from model import Road
from fastapi import HTTPException
from enum import Enum
import time

CHECK_INTERVAL = 2
# ROAD_RANK = {101: ("고속도로", 100), 102: ("도시고속화도로", 80), 103: ("일반국도", 50),
#              104: ("특별/광역시도", 50), 105: ("국가지원지방도", 50), 106: ("지방도", 50), 107: ("시군도", 50)}

engine = engineconn()
session = engine.session_maker()


Rarity = {"common": 1, "rare": 1.3, "unique": 1.5, "legend": 1.7}


def check_road(lat: float, lon: float) -> str:
    request_url = "http://49.247.33.61:5000/nearest/v1/driving/"
    param = str(lon)+","+str(lat)
    number = "?number="+str(3)
    response = requests.get(request_url+param+number).json()
    road_name = response['waypoints'][0]['name']
    return road_name


# 현재 속도 계산
def calcSpeed(before: List, after: List) -> tuple:
    distance = calcDistance(before, after)
    speed = distance * 3600 / CHECK_INTERVAL
    return round(speed, 1), distance


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


# 시 단위 현재 위치 파악
def check_city(lat: float, lon: float) -> str:
    request_url = "http://nominatim.openstreetmap.org/reverse?format=json&addressdetails=1&zoom=14&"
    url_param = "lon=" + str(lon) + "&lat="+str(lat)
    response = requests.get(request_url + url_param).json()
    return response['address']['city']


# 현재 시 위치, 도로 명에 맞는 type 반
def query_road_type(road_name: str, city: str) -> list:
    query = session.query(ROAD_INFO.road_type, ROAD_INFO.region).filter(
        ROAD_INFO.road_name.like(road_name)).filter(ROAD_INFO.region.like(city))
    result = [i.road_type for i in query]
    return result


# 제한 속도 체크
def check_speed_limit(road_types: list, road_name: str) -> int:
    # 101 고속도로, 102 고속화도로 제외 전체 50km 일괄 적용
    # for road_type in road_types:
    #     if road_type == 101 or road_type == 102:
    #         logger.error("101, 102번 겹치는 도로 : " + road_name)
    # 고속도로, 고속화 도로 구분 및 어린이 보호구역 구분 로직 추가 예정
    return 80  # default speed_limit


# main function
def check_status(locations: List, _user: str, _start_at: int) -> dict:
    location = on_road(locations)  # 현재 도로명
    speed, distance = calcSpeed(locations[-2], locations[-1])  # 속도
    distance = round(distance, 3)
    _lat, _lon = locations[-1]
    city = check_city(_lat, _lon)
    city = city + "특별시" if city == "서울" else city
    road_types = query_road_type(location, city)
    speed_limit = check_speed_limit(road_types, location)

    adj, _ = get_equipped_nft_info(_user)
    safe_driving_distance, mining_distance, mining_amount, nft_usage = update_record(
        _user, speed, speed_limit, _start_at, distance, adj)

    # current_durability, decrease_amount = update_durability(
    #     _user, distance, adj)

    query = session.query(DRIVE_RECORD).filter(DRIVE_RECORD.user == _user).filter(DRIVE_RECORD.start_at == _start_at).all()
    [q] = query
    response = Road(location=location, city=city, speed=speed, speed_limit=speed_limit, start_at = _start_at, driving_distance = q.driving_distance, safe_driving_distance = q.safe_driving_distance, mining_distance = q.mining_distance, total_mining = q.total_mining, total_nft_usage = q.nft_usage)

    logger.debug("road : " + location + " city : " + city + " speed : " + str(speed) + "km/h limit : "+str(speed_limit) + " distance : " + str(distance) + "km" + " safe distance : " + str(
        safe_driving_distance) + "km mining distance : " + str(mining_distance) + "km mining_amount : " + str(mining_amount) + " nft_usage : " + str(nft_usage))

    return response


def get_unix_time_stamp() -> int:
    return round(time.time())


# 현재 진행 중인 게임이 있는지 확인
def check_running_game(_wallet: str) -> None:
    query = session.query(DRIVE_RECORD).filter(
        DRIVE_RECORD.user == _wallet).filter(DRIVE_RECORD.end_at == None).all()

    # 이미 진행 중인 게임이 존재하는지
    if len(query) > 0:
        raise HTTPException(status_code=405, detail="ALREADY RUNNING GAME")


# 게임 시작
def start_game(_wallet: str) -> int:
    check_running_game(_wallet)  # 게임 진행중인지 체크
    query = session.query(NFT_INFO).filter(NFT_INFO.owner == _wallet).filter(NFT_INFO.equip == True).all()
    if len(query) == 0 :
        raise HTTPException(405, "NO NFT EQUIPED")
    [q]  = query

    _start_at = get_unix_time_stamp()

    dr = DRIVE_RECORD(user=_wallet, start_at=_start_at, end_at=None, driving_distance=0,
                      safe_driving_distance=0, mining_distance=0, total_mining=0, running_time=0, nft_rarity = q.rarity, nft_usage = 0.0)
    session.add(dr)
    session.commit()

    return _start_at


# 게임이 진행 중 일 때 지속적으로 테이블 업데이트
def update_record(_wallet: str, _current_speed: float, _speed_limit: float, _start_at: int, _driving_distance: float, _adj : float) -> tuple:
    # 속도 위반 여부
    violation = is_violate(_current_speed, _speed_limit)

    # 게임 기록 
    query = session.query(DRIVE_RECORD).filter(DRIVE_RECORD.user == _wallet).filter(
        DRIVE_RECORD.start_at == _start_at).all()
    
    # 진행 중인 게임이 존재 하지 않을 경우 revert
    if len(query) == 0:
        raise HTTPException(status_code=404, detail="GAME NOT EXISTS")
    
    [q] = query
    valid_distance = _driving_distance if q.mining_distance + \
        _driving_distance < 20 else 20 - q.mining_distance

    safe_driving_distance = _driving_distance if violation == 1 else 0

    mining_amount = calc_mining(
        _wallet, valid_distance, _current_speed, _speed_limit)

    nft_usage = calc_decrease_amount(1, valid_distance, 0.2, _adj, 1)

    q.driving_distance += _driving_distance
    q.safe_driving_distance += safe_driving_distance
    q.mining_distance += valid_distance
    q.total_mining += mining_amount
    q.nft_usage += nft_usage
    session.commit()

    return safe_driving_distance, valid_distance, mining_amount, nft_usage


def calc_decrease_amount(_mining_rate : float, _distance : str, _damage_factor : float, _adj : float, _c : int) -> float :
    decrease_amount = round(((pow(_mining_rate * _distance, _c) * 1 * 1 / _adj) * _damage_factor), 3)
    logger.debug(str(_mining_rate) + " " + str(_distance) + " " + str(_damage_factor) + " " + str(_adj) + " " + str(_c))
    return decrease_amount

# 이동거리 만큼 nft 내구도 감소
def update_durability(_wallet: str, _distance: float, _adj: float) -> tuple:
    damage_factor = 0.15  # damage_factor
    mining_rate = 1  # per km
    c = 1
    decrease_amount = round((pow(mining_rate * _distance, c)
                       * 1 * 1 / _adj) * damage_factor, 3)

    query = session.query(NFT_INFO).filter(
        NFT_INFO.owner == _wallet).filter(NFT_INFO.equip == 1).all()

    if len(query) == 0 or len(query) > 1:
        raise HTTPException(status_code=405, detail="INVALID NFT INFORM")

    [q] = query
    current_durability = q.current_durability
    q.current_durability -= decrease_amount
    session.commit()

    return current_durability, decrease_amount


# return adj, duability
def get_equipped_nft_info(_wallet: str) -> tuple:
    query = session.query(NFT_INFO).filter(
        NFT_INFO.owner == _wallet).filter(NFT_INFO.equip == 1).all()
    result = [(q.rarity, q.max_durability, q.current_durability)for q in query]
    rr = Rarity[result[0][0]]
    mx = result[0][1]
    cr = result[0][2]
    if len(result) == 0:
        raise HTTPException(status_code=404, detail="NFT NOT FOUND")

    return (rr, cr / mx)


# 속도 위반 체크
def is_violate(_current_speed: float, _speed_limit: float) -> int:
    return 1 if _current_speed <= _speed_limit else 0


# calc mining amount
def calc_mining(_wallet: str, _distance: float, _current_speed: float, _speed_limit: float) -> float:
    mining_rate = 1  # per km
    c = 1
    adj, durability = get_equipped_nft_info(_wallet)  # td
    v = is_violate(_current_speed, _speed_limit)
    amount = pow((mining_rate * _distance), c) * durability * v * adj
    amount = round(amount, 3)
    return amount


def end_game(_wallet: str, _start_at: int):
    query = session.query(DRIVE_RECORD).filter(DRIVE_RECORD.start_at == _start_at).filter(DRIVE_RECORD.user == _wallet).all()
    if len(query) == 0:
        raise HTTPException(status_code=405, detail="GAME NOT EXISTS")
    [q] = query

    drive_user = q.user
    drive_start_at = _start_at
    drive_end_at = get_unix_time_stamp()
    drive_driving_distance = q.driving_distance
    drive_safe_driving_distance = q.safe_driving_distance
    drive_mining_distance = q.mining_distance
    drive_total_mining = q.total_mining
    drive_running_time = drive_end_at - drive_start_at
    drive_nft_rarity = q.nft_rarity
    drive_nft_usage = q.nft_usage

    q.end_at = drive_end_at
    q.running_time = drive_running_time
    session.commit()

    history = DRIVE_HISTORY(user = drive_user, start_at = drive_start_at, end_at = drive_end_at, driving_distance = drive_driving_distance, safe_driving_distance = drive_safe_driving_distance, mining_distance = drive_mining_distance, total_mining = drive_total_mining, running_time = drive_running_time, nft_rarity = drive_nft_rarity, nft_usage = drive_nft_usage)
    session.add(history)
    session.commit()

    session.query(DRIVE_RECORD).filter(DRIVE_RECORD.user == drive_user).filter(DRIVE_RECORD.start_at == drive_start_at).filter(DRIVE_RECORD.end_at == drive_end_at).delete()


    # sdt 지급
    query1 = session.query(USER_BALANCE).filter(
        USER_BALANCE.wallet == _wallet).all()
    [q1] = query1
    q1.sdt += drive_total_mining * 1000000000
    session.commit()

    # nft usage
    query2 = session.query(NFT_INFO).filter(NFT_INFO.owner == _wallet).filter(NFT_INFO.equip == True).all()
    [q2] = query2
    q2.current_durability = q2.current_durability - drive_nft_usage if q2.current_durability >= drive_nft_usage else 0

    session.commit()




# def query_duplicate():
#     response = session.query(ROAD_INFO.road_name, text("duplicates")).from_statement(
#         text("select road_name, count(road_name) as duplicates from road_info group by road_name having count(road_name) > 1")).all()
#     result = [r[0] for r in response]

#     return result


# def check_duplicate():
#     duplicates = query_duplicate()

#     for name in duplicates:
#         response = query_road_type(name)
#         if 101 in response or 102 in response:
#             s = [str(r) for r in response]
#             print(name + " : " + ' '.join(s))


# locs = [[37.515263, 126.952187], [
#     37.515221, 126.952502], [37.515110, 126.952901]]
# check_status(locs, "BZqkHr5uwTUQpPqgLSr5erWDhx4VHz4DzN98fNsUVwwa", 1663904375)
# end_game("BZqkHr5uwTUQpPqgLSr5erWDhx4VHz4DzN98fNsUVwwa", 1663904375)