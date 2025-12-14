
THIS IS A FLASK BASED REST API FOR MANAGING STUDENT RECORDS

FEATURES-

CRUD operations for student records - can create, list, change, and remove things from the database
JWT token authentication - there are some datas that only authernticated people are allowed access
JSON and XML response formats - diff kinds of results, could be xml format or json format depending on your preference
Search functionality - search for specific info such as names and gender
Input validation and error handling - if theres an error the code can reply appropriately

LIBRARIES-

blinker
click
colorama
Flask
Flask-MySQLdb
importlib-metadata
itsdangerous
Jinja2
MarkupSafe
mysqlclient
Werkzeug
zipp
PyJWT
dicttoxml

HOW TO INSTALL-

1.Clone the repository

2.Create and activate virtual environment

3.Install dependencies (requirements.txt)

4.Configure database in app.py, credentials must be the same with your database

How to run and test the app-

python app.py

python test_api.py


