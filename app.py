from flask import Flask, request, jsonify, make_response
from flask_mysqldb import MySQL
import jwt
import datetime
from functools import wraps
import dicttoxml

app = Flask(__name__)
app.config['SECRET_KEY'] = '27811497e80109982a54cb6fc9d7e055cb492c757f6248aad09f3c63123b43f4'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Mystery'
app.config['MYSQL_DB'] = 'cse'
mysql = MySQL(app)

#JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token missing'}), 401
        try:
            if token.startswith('Bearer '):
                token = token.split(' ')[1]
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except:
            return jsonify({'error': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated

#JSON/XML HELPER
def format_response(data, status=200):
    format_type = request.args.get('format', 'json')
    if format_type == 'xml':
        xml = dicttoxml.dicttoxml(data, custom_root='response', attr_type=False)
        response = make_response(xml)
        response.headers['Content-Type'] = 'application/xml'
        response.status_code = status
        return response
    return jsonify(data), status

#LOGIN
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'error': 'Username and password required'}), 400
        if data['username'] == 'admin' and data['password'] == 'password':
            token = jwt.encode({'user': data['username'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'], algorithm='HS256')
            return jsonify({'token': token}), 200
        return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#CREATE
@app.route('/api/students', methods=['POST'])
@token_required
def create_student():
    try:
        data = request.get_json()
        if not data or not data.get('first_name') or not data.get('last_name') or not data.get('gender'):
            return jsonify({'error': 'first_name, last_name, and gender required'}), 400
        if data['gender'] not in ['Male', 'Female']:
            return jsonify({'error': 'gender must be Male or Female'}), 400
        
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO students (first_name, last_name, gender) VALUES (%s, %s, %s)", (data['first_name'], data['last_name'], data['gender']))
        mysql.connection.commit()
        student_id = cursor.lastrowid
        cursor.close()
        return format_response({'message': 'Student created', 'id': student_id}, 201)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#READ ALL STUDENT
@app.route('/api/students', methods=['GET'])
@token_required
def get_students():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT student_id, first_name, last_name, gender FROM students")
        students = cursor.fetchall()
        cursor.close()
        students_list = [{'id': s[0], 'first_name': s[1], 'last_name': s[2], 'gender': s[3]} for s in students]
        return format_response({'students': students_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
#SEARCH
@app.route('/api/students/search', methods=['GET'])
@token_required
def search_students():
    try:
        first_name = request.args.get('first_name', '')
        last_name = request.args.get('last_name', '')
        gender = request.args.get('gender', '')
        
        cursor = mysql.connection.cursor()
        query = "SELECT student_id, first_name, last_name, gender FROM students WHERE 1=1"
        params = []
        
        if first_name:
            query += " AND first_name LIKE %s"
            params.append(f"%{first_name}%")
        if last_name:
            query += " AND last_name LIKE %s"
            params.append(f"%{last_name}%")
        if gender:
            query += " AND gender = %s"
            params.append(gender)
        
        cursor.execute(query, tuple(params))
        students = cursor.fetchall()
        cursor.close()
        students_list = [{'id': s[0], 'first_name': s[1], 'last_name': s[2], 'gender': s[3]} for s in students]
        return format_response({'students': students_list, 'count': len(students_list)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#READ ONE STUDENT (BASE IN ID)
@app.route('/api/students/<int:id>', methods=['GET'])
@token_required
def get_student(id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT student_id, first_name, last_name, gender FROM students WHERE student_id = %s", (id,))
        student = cursor.fetchone()
        cursor.close()
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        student_data = {'id': student[0], 'first_name': student[1], 'last_name': student[2], 'gender': student[3]}
        return format_response(student_data)
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
        cursor.execute("SELECT student_id FROM students WHERE student_id = %s", (id,))
        if not cursor.fetchone():
            cursor.close()
            return jsonify({'error': 'Student not found'}), 404
        
        updates = []
        values = []
        if 'first_name' in data:
            updates.append("first_name = %s")
            values.append(data['first_name'])
        if 'last_name' in data:
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
        cursor.execute(f"UPDATE students SET {', '.join(updates)} WHERE student_id = %s", tuple(values))
        mysql.connection.commit()
        cursor.close()
        return format_response({'message': 'Student updated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#DELETE
@app.route('/api/students/<int:id>', methods=['DELETE'])
@token_required
def delete_student(id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT student_id FROM students WHERE student_id = %s", (id,))
        if not cursor.fetchone():
            cursor.close()
            return jsonify({'error': 'Student not found'}), 404
        cursor.execute("DELETE FROM students WHERE student_id = %s", (id,))
        mysql.connection.commit()
        cursor.close()
        return format_response({'message': 'Student deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#APP RUNNER
if __name__ == '__main__':
    app.run(debug=True)