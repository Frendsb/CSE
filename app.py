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

#LOGIN SETUP
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'error': 'Username and password required'}), 400
        
        if data['username'] == 'admin' and data['password'] == 'password':
            token = jwt.encode({
                'user': data['username'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
            }, app.config['SECRET_KEY'], algorithm='HS256')
            
            return jsonify({'token': token}), 200
        
        return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
#CRUD SECTION
#CREATE
@app.route('/api/students', methods=['POST'])
@token_required
def create_student():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body required'}), 400
        
        if 'first_name' not in data or not data['first_name']:
            return jsonify({'error': 'first_name is required'}), 400
        
        if 'last_name' not in data or not data['last_name']:
            return jsonify({'error': 'last_name is required'}), 400
            
        if 'gender' not in data or not data['gender']:
            return jsonify({'error': 'gender is required'}), 400
        
        if data['gender'] not in ['Male', 'Female']:
            return jsonify({'error': 'gender must be Male or Female'}), 400
        
        cursor = mysql.connection.cursor()
        query = "INSERT INTO students (first_name, last_name, gender) VALUES (%s, %s, %s)"
        cursor.execute(query, (data['first_name'], data['last_name'], data['gender']))
        mysql.connection.commit()
        student_id = cursor.lastrowid
        cursor.close()
        
        response_data = {
            'message': 'Student created',
            'id': student_id
        }
        
        format_type = request.args.get('format', 'json')
        if format_type == 'xml':
            xml = dicttoxml.dicttoxml(response_data, custom_root='response', attr_type=False)
            response = make_response(xml)
            response.headers['Content-Type'] = 'application/xml'
            return response, 201
        
        return jsonify(response_data), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
 
#READ ALL STUDENT
@app.route('/api/students', methods=['GET'])
@token_required
def get_students():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, first_name, last_name, gender FROM students")
        students = cursor.fetchall()
        cursor.close()
        
        students_list = []
        for student in students:
            students_list.append({
                'id': student[0],
                'first_name': student[1],
                'last_name': student[2],
                'gender': student[3]
            })
        
        response_data = {'students': students_list}
        

        format_type = request.args.get('format', 'json')
        if format_type == 'xml':
            xml = dicttoxml.dicttoxml(response_data, custom_root='response', attr_type=False)
            response = make_response(xml)
            response.headers['Content-Type'] = 'application/xml'
            return response
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
 
#READ ONE STUDENT  
@app.route('/api/students/<int:id>', methods=['GET'])
@token_required
def get_student(id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, first_name, last_name, gender FROM students WHERE id = %s", (id,))
        student = cursor.fetchone()
        cursor.close()
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        student_data = {
            'id': student[0],
            'first_name': student[1],
            'last_name': student[2],
            'gender': student[3]
        }
        
        format_type = request.args.get('format', 'json')
        if format_type == 'xml':
            xml = dicttoxml.dicttoxml(student_data, custom_root='response', attr_type=False)
            response = make_response(xml)
            response.headers['Content-Type'] = 'application/xml'
            return response
        
        return jsonify(student_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
#UPDATE 
@app.route('/api/students/<int:id>', methods=['PUT'])
@token_required
def update_student(id):
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body required'}), 400
        
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id FROM students WHERE id = %s", (id,))
        if not cursor.fetchone():
            cursor.close()
            return jsonify({'error': 'Student not found'}), 404
        
        updates = []
        values = []
        
        if 'first_name' in data:
            if not data['first_name']:
                return jsonify({'error': 'first_name cannot be empty'}), 400
            updates.append("first_name = %s")
            values.append(data['first_name'])
        
        if 'last_name' in data:
            if not data['last_name']:
                return jsonify({'error': 'last_name cannot be empty'}), 400
            updates.append("last_name = %s")
            values.append(data['last_name'])
        
        if 'gender' in data:
            if data['gender'] not in ['Male', 'Female']:
                return jsonify({'error': 'gender must be Male or Female'}), 400
            updates.append("gender = %s")
            values.append(data['gender'])
        
        if not updates:
            return jsonify({'error': 'No fields to update'}), 400
        
        values.append(id)
        query = f"UPDATE students SET {', '.join(updates)} WHERE id = %s"
        cursor.execute(query, tuple(values))
        mysql.connection.commit()
        cursor.close()
        
        response_data = {'message': 'Student updated'}
        
        format_type = request.args.get('format', 'json')
        if format_type == 'xml':
            xml = dicttoxml.dicttoxml(response_data, custom_root='response', attr_type=False)
            response = make_response(xml)
            response.headers['Content-Type'] = 'application/xml'
            return response
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500