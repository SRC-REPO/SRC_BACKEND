
# from db import engineconn
# from schema import ROAD_INFO, CHILD_PROTECTION_ROAD
# from sqlalchemy.sql import text
# import pandas as pd

# engine = engineconn()
# session = engine.session_maker()
# def read_csv():
#     datasheet = pd.read_csv(
#         "C:\\Users\\user\\Documents\\Maptest\\utils\\child_protection.csv", encoding='euc-kr')
#     df = datasheet.loc[:, ['대상시설명', '소재지도로명주소']]
#     df = df.drop_duplicates()
#     return df


# # !!!!!! before running this function you should do truncate table you use !!!!!!
# def migration_csv_to_sql():

#     data = read_csv()
#     print("total data length - " + str(len(data)))
#     cnt = 0
#     for i in range(1, len(data)):
#         d = data.iloc[i]
#         name = str(d['대상시설명'])
#         regions = str(d['소재지도로명주소']).split(" ")
#         region = regions[0]
        
#         if region == '서울특별시':
#             print(str(d['대상시설명']) +" "+ str(d['소재지도로명주소']))
#             cnt += 1
    
#     print("서울시 어린이보호도로 수 " + str(cnt))
        
#         # session.add(
#         #     ROAD_INFO(road_name=d['도로명'], road_type=d['도로등급'], region=d['링크권역']))
#         # session.commit()




