import requests

from google.auth.transport.requests import Request
from google.oauth2 import id_token

CUSTOMER = os.environ.get("CUSTOMER")
URL = f'https://{CUSTOMER}-admin-i7wsmqzjha-de.a.run.app'

# TODO: modulized same parts

def get_enabled_events(project_id):
    if CUSTOMER == None or project_id == None: return None

    api_path = f"{URL}/api/bq/get_enabled_events?customer={CUSTOMER}&project_id={project_id}"
    auth_req = Request()
    identity_token = id_token.fetch_id_token(auth_req, api_path)
    headers = {'Authorization': 'Bearer ' + identity_token,
                "Content-Type": "application/json; charset=utf-8"}
    response = requests.get(api_path, headers=headers)
    print("Enabled events:", response.status_code, response.text)
    return response.json()

def get_service_account(project_id):
    if CUSTOMER == None or project_id == None: return None

    api_path = f"{URL}/api/bq/get_service_account?customer={CUSTOMER}&project_id={project_id}"
    auth_req = Request()
    identity_token = id_token.fetch_id_token(auth_req, api_path)
    headers = {'Authorization': 'Bearer ' + identity_token,
            "Content-Type": "application/json; charset=utf-8"}
    response = requests.get(api_path, headers=headers)
    print("Service account:", response.status_code, response.text)
    return response.json()