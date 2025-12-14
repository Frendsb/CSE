import requests

BASE_URL = "http://127.0.0.1:5000/api"
token = None

def test_login():
    print("\n=== TEST 1: LOGIN ===")
    try:
        response = requests.post(f"{BASE_URL}/login", json={"username": "admin", "password": "password"})
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        global token
        if response.status_code == 200:
            token = response.json()['token']
            print("✓ Login successful!")
            return True
        print("✗ Login failed!")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_create_student():
    print("\n=== TEST 2: CREATE STUDENT ===")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {"first_name": "TestUser", "last_name": "TestLast", "gender": "Male"}
        response = requests.post(f"{BASE_URL}/students", json=data, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            print("✓ Student created!")
            return response.json()['id']
        print("✗ Failed!")
        return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def test_create_xml():
    print("\n=== TEST 3: CREATE STUDENT (XML) ===")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {"first_name": "XMLTest", "last_name": "XMLUser", "gender": "Female"}
        response = requests.post(f"{BASE_URL}/students?format=xml", json=data, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        print("✓ XML format works!" if response.status_code == 201 else "✗ Failed!")
    except Exception as e:
        print(f"✗ Error: {e}")

def test_get_all():
    print("\n=== TEST 4: GET ALL STUDENTS ===")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/students", headers=headers)
        print(f"Status: {response.status_code}")
        
        # Check if response is JSON
        try:
            data = response.json()
            print(f"Response: {data}")
            
            if response.status_code == 200 and 'students' in data:
                print(f"Total students: {len(data['students'])}")
                print("✓ Retrieved all students!")
            else:
                print("✗ Failed! Response doesn't contain 'students' key")
        except ValueError:
            print(f"✗ Failed! Response is not JSON: {response.text}")
    except Exception as e:
        print(f"✗ Error: {e}")

def test_get_one(student_id):
    print(f"\n=== TEST 5: GET STUDENT ID {student_id} ===")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/students/{student_id}", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print("✓ Retrieved student!" if response.status_code == 200 else "✗ Failed!")
    except Exception as e:
        print(f"✗ Error: {e}")

def test_update(student_id):
    print(f"\n=== TEST 6: UPDATE STUDENT ID {student_id} ===")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {"first_name": "Updated", "gender": "Female"}
        response = requests.put(f"{BASE_URL}/students/{student_id}", json=data, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print("✓ Student updated!" if response.status_code == 200 else "✗ Failed!")
    except Exception as e:
        print(f"✗ Error: {e}")

def test_search():
    print("\n=== TEST 7: SEARCH STUDENTS ===")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/students/search?gender=Male", headers=headers)
        print(f"Status: {response.status_code}")
        
        try:
            data = response.json()
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
    print("\n=== TEST 8: VALIDATION ERROR ===")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {"first_name": "Test"}  # Missing required fields
        response = requests.post(f"{BASE_URL}/students", json=data, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print("✓ Validation works!" if response.status_code == 400 else "✗ Failed!")
    except Exception as e:
        print(f"✗ Error: {e}")

def test_not_found():
    print("\n=== TEST 9: NOT FOUND ERROR ===")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/students/99999", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print("✓ 404 error works!" if response.status_code == 404 else "✗ Failed!")
    except Exception as e:
        print(f"✗ Error: {e}")

def test_delete(student_id):
    print(f"\n=== TEST 10: DELETE STUDENT ID {student_id} ===")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.delete(f"{BASE_URL}/students/{student_id}", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print("✓ Student deleted!" if response.status_code == 200 else "✗ Failed!")
    except Exception as e:
        print(f"✗ Error: {e}")

def run_all_tests():
    print("=" * 50)
    print("STARTING API TESTS")
    print("=" * 50)
    
    if not test_login():
        print("\n✗ Login failed. Cannot proceed.")
        return
    
    student_id = test_create_student()
    test_create_xml()
    test_get_all()
    if student_id:
        test_get_one(student_id)
        test_update(student_id)
    test_search()
    test_validation()
    test_not_found()
    if student_id:
        test_delete(student_id)
    
    print("\n" + "=" * 50)
    print("ALL TESTS COMPLETED")
    print("=" * 50)

if __name__ == "__main__":
    run_all_tests()