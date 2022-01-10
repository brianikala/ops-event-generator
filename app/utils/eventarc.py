"""Eventarc

This module contains the functions to manage Eventarc

"""
import json

import requests

from app.utils.adminrun import get_enabled_events
from app.utils.auth import get_credential_token

# TODO: [Config] Make region as the environment variable
REGION = 'global'

def create_eventarc_triggers():
    """Create Eventarc Triggers"""
    data = get_enabled_events()
    if not data or 'events' not in data or 'service_account' not in data:
        return 'failed'
    events = data['events']
    service_account = data['service_account'][0]
    # TODO: [Valid] Validate creation results
    # TODO: [Async] Async creation
    creation_result = [create_eventarc_trigger(event, service_account) for event in events]
    return "success"

def update_eventarc_triggers():
    """Update Eventarc Triggers"""
    data = get_enabled_events()
    if not data or 'events' not in data or 'service_account' not in data:
        return 'failed'
    events = data['events']
    service_account = data['service_account'][0]
    event_methods = [event['methodName'] for event in events]
    triggers = list_eventarc_triggers()
    trigger_methods = [trigger['methodName'] for trigger in triggers]
    events_to_create = [
        event
        for event in events
        if event['methodName'] not in trigger_methods
    ]
    triggers_to_delete = [
        trigger['id']
        for trigger in triggers
        if trigger['methodName'] not in event_methods
    ]
    # TODO: [Async] Async creation and deletion
    print(json.dumps({
        'severity': 'INFO',
        'message': f"Update eventarc triggers, {len(events_to_create)} events to create, {len(triggers_to_delete)} triggers to delete",
        'events_to_create': events_to_create,
        'triggers_to_delete': triggers_to_delete,
    }))
    # TODO: [Valid] Validate creation and deletion results
    creation_result = [create_eventarc_trigger(event, service_account) for event in events_to_create]
    deletion_result = [delete_eventarc_trigger(trigger_id) for trigger_id in triggers_to_delete]
    return "success"

def list_eventarc_triggers():
    """List Eventarc Triggers"""
    token, project_id = get_credential_token()
    api_url = f"https://eventarc.googleapis.com/v1/projects/{project_id}/locations/{REGION}/triggers"
    headers = {'Authorization': f"Bearer {token}"}
    response = requests.get(api_url, headers=headers)
    data = response.json()
    if 'triggers' not in data:
        return []
    # TODO: [Valid] Filter triggers by destinationRunRegion to list only the triggers created by EG
    result = [
        {
            'id': trigger['name'].split('/')[-1],
            'methodName': event_filter['value'],
        }
        for trigger in data['triggers']
        for event_filter in trigger['eventFilters']
        if event_filter['attribute'] == 'methodName'
    ]
    return result

def create_eventarc_trigger(event, service_account):
    """Create Eventarc Trigger"""
    if not event:
        return 'failed'
    token, project_id = get_credential_token()
    headers = {'Authorization': f"Bearer {token}"}
    data = {
        "name": f"projects/{project_id}/locations/{REGION}/triggers/{event['trigger']}",
        "eventFilters": [
            {
                "attribute": "methodName",
                "value": event['methodName']
            },
            {
                "attribute": "type",
                "value": event['type']
            },
            {
                "attribute": "serviceName",
                "value": event['serviceName']
            }
        ],
        "serviceAccount": service_account,
        "destination": {
            'cloudRun': {
                'service': event['destinationRunService'],
                'region': event['destinationRunRegion'],
                'path': event['destinationRunPath']
            }
        }
    }
    trigger_id = event['trigger'].lower()
    query_params = f"triggerId={trigger_id}&validateOnly=False"
    api_url = f"https://eventarc.googleapis.com/v1/projects/{project_id}/locations/{REGION}/triggers?{query_params}"
    response = requests.post(api_url, headers=headers, json=data)
    result = response.json()
    if 'error' in result:
        print(json.dumps({
            'severity': 'ERROR',
            'message': f"Trigger {event['trigger']} creation failed",
            "error": result['error']
        }))
        return "failed"
    print(json.dumps({
        'severity': 'INFO',
        'message': f"Trigger {event['trigger']} creation succeeded",
        'response': result
    }))
    return 'success'

def delete_eventarc_trigger(trigger_id):
    """Delete Eventarc Trigger"""
    token, project_id = get_credential_token()
    headers = {'Authorization': f"Bearer {token}"}
    query_params = "validateOnly=False"
    api_url = f"https://eventarc.googleapis.com/v1/projects/{project_id}/locations/{REGION}/triggers/{trigger_id}?{query_params}"
    response = requests.delete(api_url, headers=headers)
    result = response.json()
    print(json.dumps({
        'severity': 'INFO',
        'message': f"Trigger {trigger_id} deletion succeeded",
        'response': result
    }))
    return "success"
