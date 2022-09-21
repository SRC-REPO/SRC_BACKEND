from pymongo import MongoClient

mongodb_URI = "mongodb://localhost:27017"
client = MongoClient(mongodb_URI)


db = client['src']

post = {"road_name" : "우리집", "address" : "고척로 52길 21"}


post_id = db.map.insert_one(post).inserted_id

print(post_id)