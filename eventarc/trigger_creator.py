
import os, requests

from yachalk import chalk
from pprint import pprint as pp

from google.auth.transport import requests as reqs
from google.auth import default

from __main__ import app

from adminrun import get_enabled_events

CREDENTIAL, PROJECT_ID = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])

def hello_world():
    return "eventarc/hanlders/trigger_creator"

# TODO: access ER BQ table Projects.methodNames by accessing API of Admin run
def get_eventarc_detail():
    events = get_enabled_events(PROJECT_ID)
    if events:
        pp(events)
    # TMP
    # events = [{
    #     'trigger': 'cloud-resource-manager-SetIamPolicy', # CHANGED
    #     'location': 'global',
    #     'destination-run-service': 'demeter',
    #     'destination-run-region': 'asia-east1',
    #     'destination-run-path': '/SetIamPolicy', # CHANGED
    #     'type': 'google.cloud.audit.log.v1.written',
    #     'serviceName': 'cloudresourcemanager.googleapis.com',
    #     'methodName': 'SetIamPolicy', # CHANGED
    #     'service-account': '1097778675156-compute@developer.gserviceaccount.com' # default service account
    # },{
    #     'trigger': 'cloud-resource-manager-GetIamPolicy', # CHANGED
    #     'location': 'global',
    #     'destination-run-service': 'demeter',
    #     'destination-run-region': 'asia-east1',
    #     'destination-run-path': '/GetIamPolicy', # CHANGED
    #     'type': 'google.cloud.audit.log.v1.written',
    #     'serviceName': 'cloudresourcemanager.googleapis.com',
    #     'methodName': 'GetIamPolicy', # CHANGED
    #     'service-account': '1097778675156-compute@developer.gserviceaccount.com' # default service account
    # }]

    return events

def create_trigger(event):
    """
    https://cloud.google.com/eventarc/docs/reference/rest/v1/projects.locations.triggers/create
    POST https://eventarc.googleapis.com/v1/{parent=projects/*/locations/*}/triggers

    對應的 gcloud command:
    gcloud eventarc triggers create TRIGGER \
    --location=global \
    --destination-run-service=DESTINATION_RUN_SERVICE \
    --destination-run-region=DESTINATION_RUN_REGION \
    --destination-run-path=DESTINATION_RUN_PATH \
    --event-filters="type=google.cloud.audit.log.v1.written" \
    --event-filters="serviceName=cloudresourcemanager.googleapis.com" \
    --event-filters="methodName=SetIamPolicy" \
    --service-account=1097778675156-compute@developer.gserviceaccount.com
    """

    auth_req = reqs.Request()
    CREDENTIAL.refresh(auth_req)
    token = CREDENTIAL.token
    header = {'Authorization': f"Bearer {token}"}

    data = {
        "name": f"projects/{PROJECT_ID}/locations/global/triggers/{event['trigger']}",
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
        "serviceAccount": event['service-account'],
        "destination": {
            'cloudRun': {
                'service': event['destination-run-service'],
                'region': event['destination-run-region'],
                'path': event['destination-run-path']
            }       
        }
    }

    pp(data)
    trigger_id = event['trigger'].lower()
    query_params = f"triggerId={trigger_id}&validateOnly=False"
    api_url = f"https://eventarc.googleapis.com/v1/projects/{PROJECT_ID}/locations/global/triggers?{query_params}"

    response = requests.post(api_url, headers=header, json=data)
    result = response.json()
    if 'error' in result:
        print(result['error']['status'])
        print(f"Trigger {event['trigger']} creation",chalk.red("failed"))
        return "failed"

    pp(result)
    print(f"Trigger {event['trigger']} creation", chalk.green("success"))
    return 'success'
        
def create_eventarc_triggers():
    """
    Create a new trigger in a particular project and location.
    """
    events = get_eventarc_detail()
    pp(events)

    # TODO: 因為應該會有很多 events (初期有 5 個)，因此應要做成非同步的，呼叫完此 API 後就導向狀態頁面看進度
    # results = [create_trigger(e) for e in events]

    return "success"

def delete_trigger(event):
    return None


### ROUTE MAPS ###
app.add_url_rule('/module1', endpoint="module1", view_func=hello_world, methods=["GET"])
app.add_url_rule(
    '/create/eventarc/triggers',
    endpoint='/create/eventarc/triggers',
    view_func=create_eventarc_triggers,
    methods=['GET']
)
app.add_url_rule(
    '/delete/eventarc/trigger/<event_name>',
    endpoint='/delete/eventarc/trigger/',
    view_func=delete_trigger,
    methods=['GET']
)