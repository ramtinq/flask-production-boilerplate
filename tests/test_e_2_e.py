import os
import time
import uuid
import pytest
import requests
from bs4 import BeautifulSoup
from scripts.secret_utils import generate_app_verification_token

BASE_URL = os.getenv("BASE_URL", "http://web:5000")

def get_csrf_token(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    token = soup.find('input', {'name': 'csrf_token'})
    return token['value'] if token else None

# ==========================================
# FIXTURES (Setup State)
# ==========================================

@pytest.fixture
def app_token():
    return generate_app_verification_token()

@pytest.fixture(scope="session")
def client():
    return requests.Session()

@pytest.fixture(scope="session")
def auth_client():
    session = requests.Session()
    username = f"tester_{uuid.uuid4().hex[:6]}"
    password = "StrongPassword123!"

    reg_page = session.get(f"{BASE_URL}/user/register")
    csrf_token = get_csrf_token(reg_page.text)

    reg_res = session.post(f"{BASE_URL}/user/register", data={
        "csrf_token": csrf_token,
        "username": username,
        "password": password,
        "password_confirmation": password
    })

    assert "/user/login" in reg_res.url, (
        f"Registration failed! The app didn't redirect to /user/login, it stayed on {reg_res.url}. "
    )
    
    login_page = session.get(f"{BASE_URL}/user/login")
    login_csrf = get_csrf_token(login_page.text)
    
    session.post(f"{BASE_URL}/user/login", data={
        "csrf_token": login_csrf,
        "username": username,
        "password": password
    })
    
    return session

# ==========================================
# TEST DOMAIN: Security & Routing
# ==========================================

def test_public_routes_accessible(client):
    assert client.get(f"{BASE_URL}/").status_code == 200
    assert client.get(f"{BASE_URL}/user/register").status_code == 200
    assert client.get(f"{BASE_URL}/user/login").status_code == 200


def test_api_endpoint_accessible_with_valid_token(client, app_token):
    response = client.get(
        f"{BASE_URL}/api/liveness",
        headers={
            "X-Auth": f"Bearer {app_token}"
        }
    )

    assert response.status_code == 200

def test_api_endpoint_not_accessible_with_invalid_token(client):
    response = client.get(
        f"{BASE_URL}/api/liveness",
        headers={
            "X-Auth": "Bearer some_invalid_token"
        }
    )

    assert response.status_code == 401

def test_protected_routes_block_unauthorized_users(client):
    res = client.get(f"{BASE_URL}/user/dashboard")
    assert "login" in res.url or res.status_code in [401, 403]
    
    res_pi = client.get(f"{BASE_URL}/user/task/estimate-pi/10")
    assert "login" in res_pi.url or res_pi.status_code in [401, 403]

def test_dashboard_accessible_when_logged_in(auth_client):
    res = auth_client.get(f"{BASE_URL}/user/dashboard")
    assert res.status_code == 200
    assert "login" not in res.url

# ==========================================
# TEST DOMAIN: Celery Standard Tasks
# ==========================================

def test_random_number_background_task(client):
    res_start = client.get(f"{BASE_URL}/task/generate-random/100")
    assert res_start.status_code == 200
    task_id = res_start.json().get("task_id")
    assert task_id is not None

    task_finished = False
    for _ in range(25):
        res_check = client.get(f"{BASE_URL}/task/result/{task_id}")
        data = res_check.json()
        if data.get("state") == "SUCCESS":
            task_finished = True
            assert 0 <= data.get("result") <= 100
            break
        time.sleep(1)

    assert task_finished, "Celery task did not succeed within timeout. Check worker logs."

# ==========================================
# TEST DOMAIN: Celery Chains & DB Writes
# ==========================================

def test_pi_estimation_chain_succeeds(auth_client):
    res_start = auth_client.get(f"{BASE_URL}/user/task/estimate-pi/5000")
    assert res_start.status_code == 200

    task_id = res_start.json().get("task_id")
    assert task_id is not None

    pipeline_finished = False
    for _ in range(15):
        res_calc = auth_client.get(f"{BASE_URL}/task/result/{task_id}")
        if res_calc.json().get("state") == "SUCCESS":
            pipeline_finished = True
            break
        time.sleep(1)
        
    assert pipeline_finished, "Pi calculation chain failed to process or render to UI."