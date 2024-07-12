import jwt, datetime, os
from flask import Flask, request
from flask_mysqldb import MySQL
from dotenv import load_dotenv

load_dotenv()

server = Flask(__name__)
mysql = MySQL(server)

#config 
# print(server.config["MYSQL_HOST"])

server.config["MYSQL_HOST"] = os.getenv("MYSQL_HOST")
server.config["MYSQL_USER"] = os.getenv("MYSQL_USER")
server.config["MYSQL_PASSWORD"] = os.getenv("MYSQL_PASSWORD")
server.config["MYSQL_DB"] = os.getenv("MYSQL_DB")
server.config["MYSQL_PORT"] =  os.getenv("MYSQL_PORT")

@server.route("/login", methods=["POST"])
def login():
    auth = request.authorization
    if not auth:
        return "Missing credentials", 401
    # auth.username
    # auth.password
    ## check db for username and password
    cur = mysql.connection.cursor()
    res = cur.execute(
        "SELECT email, password FROM users WHERE email = %s", (auth.username,))
    
    if res > 0:
        user_row = cur.fetchone()
        email = user_row[0]
        password = user_row[1]

        if auth.username != email or auth.password != password:
            return "Invalid credentials", 401
        else:
            return createJWT(auth.username, os.getenv("JWT_SECRET_KEY"), True)
    else:
        return "Invalid credentials", 401




