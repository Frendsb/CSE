from flask import Flask, request, jsonify, make_response
from flask_mysqldb import MySQL
import jwt
import datetime
from functools import wraps
import dicttoxml

app = Flask(__name__)

app.config['SECRET_KEY'] = 'your-secret-key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask_api_db'

mysql = MySQL(app)
