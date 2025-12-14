from flask import Flask, request, jsonify, make_response
from flask_mysqldb import MySQL
import jwt
import datetime
from functools import wraps
import dicttoxml

#FLASK DATABASE SETUP
app = Flask(__name__)

app.config['SECRET_KEY'] = '27811497e80109982a54cb6fc9d7e055cb492c757f6248aad09f3c63123b43f4'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'cselec'

mysql = MySQL(app)

#JWT 
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token.split(' ')[1]
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    return decorated