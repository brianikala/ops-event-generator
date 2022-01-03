import os, requests

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
    print("[adminrun.py/get_enabled_events] Enabled events:", response.status_code, response.text)
    if response.status_code == 200:
        result = response.json()
        result['events'] = [event for event in result['events'] if event['enabled']]
        return result
    elif response.status_code == 404:
        print("[adminrun.py/get_enabled_events] The admin run for this customer does not exist")
    else:
        print("[adminrun.py/get_enabled_events] No available enabled events of current customer")

    return {}

def get_service_account(project_id):
    if CUSTOMER == None or project_id == None: return None

    api_path = f"{URL}/api/bq/get_service_account?customer={CUSTOMER}&project_id={project_id}"
    auth_req = Request()
    identity_token = id_token.fetch_id_token(auth_req, api_path)
    headers = {'Authorization': 'Bearer ' + identity_token,
            "Content-Type": "application/json; charset=utf-8"}
    response = requests.get(api_path, headers=headers)
    print("[adminrun.py/get_service_account] Service account:", response.status_code, response.text)
    return response.text