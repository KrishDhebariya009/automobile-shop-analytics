import mysql
import mysql.connector
try:
    def get_connection():
        return mysql.connector.connect(
            user = "root",
        host = "localhost",
        password = "",
        database = "automobile_shop"
        )
except:
    print("No connection")
