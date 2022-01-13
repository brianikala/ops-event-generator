"""Admin Run API

This module contains functions to interact with the Admin Run API.

"""
import json

import requests
from google.auth.transport.requests import Request
from google.oauth2 import id_token

from app.utils.auth import get_project_id
from app.utils.env import get_customer

def get_base_url(customer):
    """Get base URL for Admin Run API"""
    return f'https://{customer}-admin-i7wsmqzjha-de.a.run.app'

def get_enabled_events():
    """Get enabled events from Admin Run API"""
    project_id = get_project_id()
    customer = get_customer()
    if project_id is None or customer is None:
        return None
    base_url = get_base_url(customer)
    # TODO: [API] Change to API /api/event_package?project_id=project_id to avoid passing customer name
    api_path = f'{base_url}/api/bq/get_enabled_events?customer={customer}&project_id={project_id}'
    auth_req = Request()
    identity_token = id_token.fetch_id_token(auth_req, api_path)
    headers = {
        'Authorization': f'Bearer {identity_token}',
        'Content-Type': 'application/json; charset=utf-8'
    }
    response = requests.get(api_path, headers=headers)
    message = ''
    result = {}
    if response.status_code == 200:
        message = '[adminrun.py/get_enabled_events] Success'
        result = response.json()
        result['events'] = [event for event in result['events'] if event['enabled']]
        return result
    elif response.status_code == 404:
        message = '[adminrun.py/get_enabled_events] The admin run for this customer does not exist'
    elif response.status_code == 403:
        message = '[adminrun.py/get_enabled_events] Service account is not added to admin run API'
    else:
        message = '[adminrun.py/get_enabled_events] No available enabled events of current customer'
    print(json.dumps({
        'severity': 'INFO',
        'message': message,
        'status_code': response.status_code,
        'data': response.json() if response.status_code == 200 else response.text
    }))
    return result
