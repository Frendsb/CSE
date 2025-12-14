"""
API Test Suite for Student Management REST API
This file contains automated tests for all CRUD operations and features.
Run this after starting the Flask app (python app.py).
"""

import requests

# Base URL for all API endpoints
BASE_URL = "http://127.0.0.1:5000/api"

# Global variable to store JWT token after login
# All other tests will use this token for authentication
token = None

def test_login():
    """
    TEST 1: Authentication/Login
    - Tests the login endpoint to get a JWT token
    - This token is required for all other API operations
    - Token expires after 30 minutes
    """
    print("\n=== TEST 1: LOGIN ===")
    try:
        # Send POST request to login endpoint with credentials
        response = requests.post(
            f"{BASE_URL}/login", 
            json={"username": "admin", "password": "password"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Store token globally so other tests can use it
        global token
        if response.status_code == 200:
            # Extract token from response and save it
            token = response.json()['token']
            print("✓ Login successful!")
            return True
        print("✗ Login failed!")
        return False
    except Exception as e:
        # Catch any errors (network issues, server down, etc.)
        print(f"✗ Error: {e}")
        return False

def test_create_student():
    """
    TEST 2: CREATE Operation (JSON format)
    - Tests creating a new student record
    - Uses JWT token for authentication
    - Returns the ID of the created student
    - Expected response: 201 Created
    """
    print("\n=== TEST 2: CREATE STUDENT ===")
    try:
        # Include JWT token in Authorization header
        headers = {"Authorization": f"Bearer {token}"}
        
        # Student data to create
        data = {
            "first_name": "TestUser", 
            "last_name": "TestLast", 
            "gender": "Male"
        }
        
        # Send POST request to create student
        response = requests.post(
            f"{BASE_URL}/students", 
            json=data, 
            headers=headers
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            print("✓ Student created!")
            # Return the new student's ID for use in later tests
            return response.json()['id']
        print("✗ Failed!")
        return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def test_create_xml():
    """
    TEST 3: CREATE Operation (XML format)
    - Tests creating a student with XML response format
    - Uses ?format=xml query parameter
    - Verifies that the API can return XML instead of JSON
    """
    print("\n=== TEST 3: CREATE STUDENT (XML) ===")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "first_name": "XMLTest", 
            "last_name": "XMLUser", 
            "gender": "Female"
        }
        
        # Note: ?format=xml tells API to return XML instead of JSON
        response = requests.post(
            f"{BASE_URL}/students?format=xml", 
            json=data, 
            headers=headers
        )
        print(f"Status: {response.status_code}")
        # Only print first 200 chars of XML (it can be long)
        print(f"Response: {response.text[:200]}...")
        print("✓ XML format works!" if response.status_code == 201 else "✗ Failed!")
    except Exception as e:
        print(f"✗ Error: {e}")

def test_get_all():
    """
    TEST 4: READ All Operation
    - Tests retrieving all student records
    - Should return a list of students in JSON format
    - Expected response: 200 OK
    """
    print("\n=== TEST 4: GET ALL STUDENTS ===")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Send GET request to retrieve all students
        response = requests.get(f"{BASE_URL}/students", headers=headers)
        print(f"Status: {response.status_code}")
        
        # Try to parse response as JSON
        try:
            data = response.json()
            print(f"Response: {data}")
            
            # Check if response has 'students' key (expected structure)
            if response.status_code == 200 and 'students' in data:
                print(f"Total students: {len(data['students'])}")
                print("✓ Retrieved all students!")
            else:
                print("✗ Failed! Response doesn't contain 'students' key")
        except ValueError:
            # This happens if response is not valid JSON
            print(f"✗ Failed! Response is not JSON: {response.text}")
    except Exception as e:
        print(f"✗ Error: {e}")

def test_get_one(student_id):
    """
    TEST 5: READ Single Operation
    - Tests retrieving a specific student by ID
    - Uses the ID from the create test
    - Expected response: 200 OK with student data
    """
    print(f"\n=== TEST 5: GET STUDENT ID {student_id} ===")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # GET request with student ID in URL path
        response = requests.get(
            f"{BASE_URL}/students/{student_id}", 
            headers=headers
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print("✓ Retrieved student!" if response.status_code == 200 else "✗ Failed!")
    except Exception as e:
        print(f"✗ Error: {e}")

def test_update(student_id):
    """
    TEST 6: UPDATE Operation
    - Tests updating an existing student's information
    - Can update one or more fields (first_name, last_name, gender)
    - Expected response: 200 OK
    """
    print(f"\n=== TEST 6: UPDATE STUDENT ID {student_id} ===")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Update data - only updating first_name and gender
        # last_name will remain unchanged
        data = {"first_name": "Updated", "gender": "Female"}
        
        # Send PUT request to update student
        response = requests.put(
            f"{BASE_URL}/students/{student_id}", 
            json=data, 
            headers=headers
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print("✓ Student updated!" if response.status_code == 200 else "✗ Failed!")
    except Exception as e:
        print(f"✗ Error: {e}")

def test_search():
    """
    TEST 7: SEARCH Functionality
    - Tests the search endpoint with query parameters
    - Searches for students by gender (Male)
    - Can also search by first_name, last_name, or combinations
    - Expected response: 200 OK with matching students and count
    """
    print("\n=== TEST 7: SEARCH STUDENTS ===")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Search using query parameter: ?gender=Male
        response = requests.get(
            f"{BASE_URL}/students/search?gender=Male", 
            headers=headers
        )
        print(f"Status: {response.status_code}")
        
        try:
            data = response.json()
            # Check if response includes 'count' field
            if 'count' in data:
                print(f"Found: {data['count']} male students")
                print("✓ Search works!" if response.status_code == 200 else "✗ Failed!")
            else:
                print(f"Response: {data}")
                print("✗ Failed!")
        except ValueError:
            print(f"✗ Response is not JSON: {response.text}")
    except Exception as e:
        print(f"✗ Error: {e}")

def test_validation():
    """
    TEST 8: INPUT VALIDATION
    - Tests that API properly validates input data
    - Sends incomplete data (missing last_name and gender)
    - Expected response: 400 Bad Request with error message
    """
    print("\n=== TEST 8: VALIDATION ERROR ===")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Intentionally missing required fields to trigger validation error
        data = {"first_name": "Test"}  # Missing last_name and gender
        
        response = requests.post(
            f"{BASE_URL}/students", 
            json=data, 
            headers=headers
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Success means validation is working (returns 400 error)
        print("✓ Validation works!" if response.status_code == 400 else "✗ Failed!")
    except Exception as e:
        print(f"✗ Error: {e}")

def test_not_found():
    """
    TEST 9: ERROR HANDLING (404)
    - Tests that API handles non-existent resources properly
    - Tries to get a student with ID 99999 (likely doesn't exist)
    - Expected response: 404 Not Found
    """
    print("\n=== TEST 9: NOT FOUND ERROR ===")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to get student with very high ID that likely doesn't exist
        response = requests.get(
            f"{BASE_URL}/students/99999", 
            headers=headers
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Success means 404 error handling works correctly
        print("✓ 404 error works!" if response.status_code == 404 else "✗ Failed!")
    except Exception as e:
        print(f"✗ Error: {e}")

def test_delete(student_id):
    """
    TEST 10: DELETE Operation
    - Tests deleting a student record
    - Uses the ID from the create test
    - Expected response: 200 OK
    - This is done last so we delete the test student we created
    """
    print(f"\n=== TEST 10: DELETE STUDENT ID {student_id} ===")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Send DELETE request
        response = requests.delete(
            f"{BASE_URL}/students/{student_id}", 
            headers=headers
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print("✓ Student deleted!" if response.status_code == 200 else "✗ Failed!")
    except Exception as e:
        print(f"✗ Error: {e}")

def run_all_tests():
    """
    Main test runner function
    - Orchestrates all tests in logical order
    - Stops if login fails (can't proceed without token)
    - Creates a student, tests operations on it, then deletes it
    
    Test Flow:
    1. Login (get token)
    2. Create student (save ID)
    3. Create with XML format
    4. Get all students
    5. Get one student (using saved ID)
    6. Update student (using saved ID)
    7. Search students
    8. Test validation errors
    9. Test 404 errors
    10. Delete student (cleanup, using saved ID)
    """
    print("=" * 50)
    print("STARTING API TESTS")
    print("=" * 50)
    
    # STEP 1: Login first - if this fails, we can't run other tests
    if not test_login():
        print("\n✗ Login failed. Cannot proceed.")
        return
    
    # STEP 2-3: Test CREATE operations
    student_id = test_create_student()  # Save the ID for later tests
    test_create_xml()
    
    # STEP 4-5: Test READ operations
    test_get_all()
    if student_id:
        test_get_one(student_id)  # Use the ID we saved
        test_update(student_id)    # Update the same student
    
    # STEP 6-9: Test SEARCH and ERROR HANDLING
    test_search()
    test_validation()
    test_not_found()
    
    # STEP 10: DELETE (cleanup)
    if student_id:
        test_delete(student_id)  # Delete the test student we created
    
    print("\n" + "=" * 50)
    print("ALL TESTS COMPLETED")
    print("=" * 50)

# This block runs when you execute: python test_api.py
if __name__ == "__main__":
    run_all_tests()