# from pymongo import MongoClient
# from shapely.geometry import Polygon, Point
# mongodb_URI = "mongodb://49.247.31.91:27017"
# client = MongoClient(mongodb_URI)
# db = client['road_info']


# def check_ramp(_road_name: str, _lat: float, _lon: float) -> int:
#     post = db.map.find_one({"road": _road_name})
#     if post is None:
#         return -1

#     loc = Point(_lat, _lon)
#     for key in post['speed'].keys():
#         polygons = post['speed'][key]

#         for area in polygons:
#             polygon = Polygon(area)
#             if polygon.contains(loc):
#                 return key

#     return -1
