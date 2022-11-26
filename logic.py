from lib2to3.pgen2.driver import Driver
import math
from signal import raise_signal
import requests
from typing import List
from loguru import logger
from db import engineconn
from schema import ROAD_INFO, NFT_INFO, DRIVE_RECORD, USER_BALANCE, DRIVE_HISTORY
from model import Road, Result
from fastapi import HTTPException
import time
import copy
CHECK_INTERVAL = 1 #sec

engine = engineconn()
session = engine.session_maker()

# To be adjusted
RarityAdjustment = {"base": 1.0, 
"safe_driver": 1.0, 
"accident_free": 1.0, 
"instructor": 1.0,
"level5":1.0,
"level6":1.0,
"level7":1.0,
"level8":1.0,
"level9":1.0,
"level10":1.0}

def check_road(lat: float, lon: float) -> str:
    request_url = "http://49.247.31.91:5000/nearest/v1/driving/"
    param = str(lon)+","+str(lat)
    number = "?number="+str(2)
    response = requests.get(request_url+param+number).json()
    road_name = response['waypoints'][0]['name']
    return road_name

def get_road_node(lat: float, lon: float) -> str:
    request_url = "http://49.247.31.91:5000/nearest/v1/driving/"
    param = str(lon)+","+str(lat)
    number = "?number="+str(2)
    response = requests.get(request_url+param+number).json()
    node = response['waypoints'][0]['nodes'] #list ['node1', 'node2']
    return node[0]


# 현재 속도 계산
def calc_speed(before: List, after: List) -> tuple:
    distance = calc_distance(before, after)
    speed = distance * 3600 / CHECK_INTERVAL
    return round(speed, 1), distance


# 이전 위치에서 이동한 거리 계산
def calc_distance(before: List, after: List) -> float:
    theta = before[1] - after[1]
    dist = math.sin(deg2rad(before[0])) * math.sin(deg2rad(after[0])) + math.cos(
        deg2rad(before[0])) * math.cos(deg2rad(after[0])) * math.cos(deg2rad(theta))
    dist = rad2deg(math.acos(dist)) * 60 * 1.1515 * 1.609344
    return dist

# Daily mining distance cap 도달 여부
def is_reach_daily_limit_mining_distance(_wallet: str, _daily_cap_mining_distance: float) -> bool:
    dt = date.today()
    print(datetime.combine(dt, datetime.min.time()))    
    # 오늘 00:00분
    midnight_behind = datetime.combine(dt, datetime.min.time())

    query_h = session.query(DRIVE_HISTORY).filter(
        DRIVE_HISTORY.end_at > midnight_behind).filter(DRIVE_HISTORY.user == _wallet).all()
    mining_distance_history = query_h.mining_distance
    query_a = session.query(DRIVE_RECORD).filter(DRIVE_RECORD.user == _wallet).one()
    mining_distance_active = query_a.mining_distance

    if mining_distance_history + mining_distance_active < _daily_cap_mining_distance:
        return False
    else:
        return True


# nft mining distance 소모량 = mining distance

# nft durability 소모량 계산. 에너지 소모량 = 채굴*_damage_factor
def calc_decrease_amount(_mining_rate: float, _distance: str, _damage_factor: float, _adj: float, _c: int, _total_nft_usage: float, _nft_durability: float) -> float:

    decrease_amount = round(
        (pow(_mining_rate * _distance, _c) * 1 * 1 / _adj) * _damage_factor, 1)

    if _total_nft_usage + decrease_amount >= _nft_durability:
        return round(abs(_nft_durability - _total_nft_usage), 1)

    return decrease_amount


# calc mining amount
def calc_mining(_wallet: str, _distance: float, _current_speed: float, _speed_limit: float) -> float:
    mining_rate = 1  # per km
    c = 1
    adj, durability = get_equipped_nft_info(_wallet)  # td
    v = is_violate(_current_speed, _speed_limit)
    amount = pow((mining_rate * _distance), c) * durability * v * adj
    amount = round(amount, 3)
    return amount


def deg2rad(deg: float) -> float:
    return (deg * math.pi / 180.0)


def rad2deg(rad: float) -> float:
    return (rad * 180 / math.pi)


def get_unix_time_stamp() -> int:
    return round(time.time())


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

    if current_location == "":
        raise HTTPException(status_code=404, detail="NO ROAD NAME FOUND")

    return current_location


# return adj, duability
def get_equipped_nft_info(_wallet: str) -> tuple:
    query = session.query(NFT_INFO).filter(
        NFT_INFO.owner == _wallet).filter(NFT_INFO.equip == 1).all()
    result = [(q.rarity, q.max_durability, q.current_durability)for q in query]
    rr = RarityAdjustment[result[0][0]]
    mx = result[0][1]
    cr = result[0][2]
    if len(result) == 0:
        raise HTTPException(status_code=404, detail="NFT NOT FOUND")

    # This should be evaluated on the fly
    if cr <= 30:
        reduction_factor = 0.3
    elif cr <= 50:
        reduction_factor = 0.5
    elif cr <= 70:
        reduction_factor = 0.7
    else
        reduction_factor = 1.0

    return (rr, reduction_factor)


# 속도 위반 체크
def is_violate(_current_speed: float, _speed_limit: float) -> int:
    return 1 if _current_speed <= _speed_limit else 0


# 현재 시 위치, 도로 명에 맞는 type 반
def query_road_type(road_name: str, city: str) -> list:
    query = session.query(ROAD_INFO.road_type, ROAD_INFO.region).filter(
        ROAD_INFO.road_name.like(road_name)).filter(ROAD_INFO.region.like(city))
    result = [i.road_type for i in query]
    return result


# 시 단위 현재 위치 파악
# def check_city(lat: float, lon: float) -> str:
#     request_url = "http://49.247.31.91/nominatim/reverse?format=json&addressdetails=1&zoom=14&"
#     url_param = "lon=" + str(lon) + "&lat="+str(lat)
#     response = requests.get(request_url + url_param).json()
#     return response['address']['city']


# 현재 진행 중인 게임이 있는지 확인
def check_running_game(_wallet: str) -> None:
    query = session.query(DRIVE_RECORD).filter(
        DRIVE_RECORD.user == _wallet).filter(DRIVE_RECORD.end_at == None).all()

    # 이미 진행 중인 게임이 존재하는지
    if len(query) > 0:
        raise HTTPException(status_code=403, detail="ALREADY RUNNING GAME")
    

# 제한 속도 체크
def check_speed_limit(_road_types: list, _road_name: str, _lat: float, _lon: float) -> int:
    return


# #  고속도로 2 고속화도로 1 국도 0 중복 -1
# def check_highway_or_general(_road_types: list) -> int:
#     if _road_types == []:
#         raise HTTPException(status_code=404, detail="NO ROAD_TYPES FOUND")
#     r_type = {"general": 0, "high": 0, "city": 0}

#     general_road = [103, 104, 105, 106, 107]
#     high_way = [101]
#     city_high_way = [102]

#     for road_type in _road_types:
#         if road_type in general_road:
#             r_type["general"] = r_type["general"] + 1
#         elif road_type in high_way:
#             r_type["high"] = r_type["high"] + 1
#         elif road_type in city_high_way:
#             r_type["city"] = r_type["city"] + 1
#     logger.debug(_road_types)

#     if r_type["high"] > 0 and r_type["city"] == 0 and r_type["general"] == 0:
#         return 2
#     elif r_type["city"] > 0 and r_type["high"] == 0 and r_type["general"] == 0:
#         return 1
#     elif r_type["general"] > 0 and r_type["high"] == 0 and r_type["city"] == 0:
#         return 0
#     else:
#         return -1


# main function
def check_status(locations: List, _user: str, _start_at: int) -> Road:
    location = on_road(locations)  # 현재 도로명
    speed, distance = calc_speed(locations[-2], locations[-1])  # 속도
    distance = round(distance, 3)
    _lat, _lon = locations[-1]
    city = check_city(_lat, _lon)
    city = city + "특별시" if city == "서울" else city
    road_types = query_road_type(location, city)
    speed_limit = check_speed_limit(
        road_types, location, locations[-2][0], locations[-2][1])

    adj, _ = get_equipped_nft_info(_user)
    safe_driving_distance, mining_distance, mining_amount, nft_usage = update_record(
        _user, speed, speed_limit, _start_at, distance, adj)

    query = session.query(DRIVE_RECORD).filter(DRIVE_RECORD.user == _user).filter(
        DRIVE_RECORD.start_at == _start_at).all()
    [q] = query
    response = Road(location=location, city=city, speed=speed, speed_limit=speed_limit, start_at=_start_at, driving_distance=q.driving_distance,
                    safe_driving_distance=q.safe_driving_distance, mining_distance=q.mining_distance, total_mining=q.total_mining, total_nft_usage=q.nft_usage)

    logger.debug("road : " + location + " city : " + city + " speed : " + str(speed) + "km/h limit : "+str(speed_limit) + " distance : " + str(distance) + "km" + " safe distance : " + str(
        safe_driving_distance) + "km mining distance : " + str(mining_distance) + "km mining_amount : " + str(mining_amount) + " nft_usage : " + str(nft_usage))

    return response


# 게임이 진행 중 일 때 지속적으로 테이블 업데이트
def update_record(_wallet: str, _current_speed: float, _speed_limit: float, _start_at: int, _driving_distance: float, _adj: float) -> tuple:
    # 속도 위반 여부
    violation = is_violate(_current_speed, _speed_limit)

    q1 = session.query(NFT_INFO).filter(
        NFT_INFO.owner == _wallet).filter(NFT_INFO.equip == True).all()
    [qq] = q1
    current_nft_durability = qq.current_durability

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

    nft_usage = calc_decrease_amount(1, valid_distance, 0.2, _adj, 1, copy.deepcopy(
        q.nft_usage), current_nft_durability)


    q.driving_distance += _driving_distance
    q.safe_driving_distance += safe_driving_distance
    q.mining_distance += valid_distance
    q.total_mining += mining_amount
    q.nft_usage += nft_usage
    session.commit()

    return safe_driving_distance, valid_distance, mining_amount, nft_usage


# 게임 시작
def start_game(_wallet: str) -> int:
    check_running_game(_wallet)  # 게임 진행중인지 체크
    check_24h(_wallet)
    query = session.query(NFT_INFO).filter(
        NFT_INFO.owner == _wallet).filter(NFT_INFO.equip == True).all()
    if len(query) == 0:
        raise HTTPException(405, "NO NFT EQUIPED")
    [q] = query

    _start_at = get_unix_time_stamp()

    dr = DRIVE_RECORD(user=_wallet, start_at=_start_at, end_at=None, driving_distance=0,
                      safe_driving_distance=0, mining_distance=0, total_mining=0, running_time=0, nft_rarity=q.rarity, nft_usage=0.0)
    session.add(dr)
    session.commit()
    return _start_at


# 게임 종료 / 유저 잔고, nft 내구도 감소, nft 남은 채굴거리 소모
def end_game(_wallet: str, _start_at: int) -> Result:
    query = session.query(DRIVE_RECORD).filter(
        DRIVE_RECORD.start_at == _start_at).filter(DRIVE_RECORD.user == _wallet).all()
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

    history = DRIVE_HISTORY(user=drive_user, start_at=drive_start_at, end_at=drive_end_at, driving_distance=drive_driving_distance, safe_driving_distance=drive_safe_driving_distance,
                            mining_distance=drive_mining_distance, total_mining=drive_total_mining, running_time=drive_running_time, nft_rarity=drive_nft_rarity, nft_usage=drive_nft_usage)
    session.add(history)
    session.commit()

    session.query(DRIVE_RECORD).filter(DRIVE_RECORD.user == drive_user).filter(
        DRIVE_RECORD.start_at == drive_start_at).filter(DRIVE_RECORD.end_at == drive_end_at).delete()

    # sdt 지급
    query1 = session.query(USER_BALANCE).filter(
        USER_BALANCE.wallet == _wallet).all()
    [q1] = query1
    q1.sdt += drive_total_mining * 1000000000
    session.commit()

    # nft usage
    query2 = session.query(NFT_INFO).filter(
        NFT_INFO.owner == _wallet).filter(NFT_INFO.equip == True).all()
    [q2] = query2
    q2.current_durability = q2.current_durability - \
        drive_nft_usage if q2.current_durability >= drive_nft_usage else 0

    # nft remaining_mining_distance 차감.
    #

    session.commit()

    return Result(user=_wallet, start_at=history.start_at, end_at=history.end_at, driving_distance=history.driving_distance, safe_driving_distance=history.safe_driving_distance, mining_distance=history.mining_distance, total_mining=history.total_mining, total_nft_usage=history.nft_usage, running_time=history.running_time)
