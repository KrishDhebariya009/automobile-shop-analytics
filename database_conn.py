import os
import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", ""),
        database=os.environ.get("DB_NAME", "automobile_shop")
    )




# import mysql
# import mysql.connector
# try:
#     def get_connection():
#         return mysql.connector.connect(
#             user = "root",
#         host = "localhost",
#         password = "",
#         database = "automobile_shop"
#         )
# except:
#     print("No connection")
