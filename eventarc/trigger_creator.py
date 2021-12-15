
import requests

from yachalk import chalk
from pprint import pprint as pp

from google.auth.transport import requests as reqs
from google.auth import default

from adminrun import get_enabled_events

# FIXME: 不是 GCP 的 EG project 怎麼辦？
CREDENTIAL, PROJECT_ID = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])

def hello_world():
    return "eventarc/hanlders/trigger_creator"

# access ER BQ table Projects.methodNames by accessing API of Admin run
def get_eventarc_detail():
    data = get_enabled_events(PROJECT_ID)
    return data

def create_trigger(event, service_account):
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
        "serviceAccount": service_account,
        "destination": {
            'cloudRun': {
                'service': event['destinationRunService'],
                'region': event['destinationRunRegion'],
                'path': event['destinationRunPath']
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

# 這個是建立 provisioned 的五個      
def create_eventarc_triggers():
    """
    Create a new trigger in a particular project and location.

    [TEST]
    curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
    https://demeter-xog7tpoz7a-de.a.run.app/create/eventarc/triggers
    """
    data = get_eventarc_detail()
    events = data['events']
    service_account = data['service_account'][0]

    # TODO: 因為應該會有很多 events (初期有 5 個)，因此應要做成非同步的，呼叫完此 API 後就導向狀態頁面看進度
    results = [create_trigger(e, service_account) for e in events]
    print(results)

    return "success"

def delete_trigger(trigger_id):
    """
    https://cloud.google.com/eventarc/docs/reference/rest/v1/projects.locations.triggers/delete
    DELETE https://eventarc.googleapis.com/v1/{name=projects/*/locations/*/triggers/*} 

    [TEST]
    curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
    -X DELETE https://demeter-xog7tpoz7a-de.a.run.app/delete/eventarc/trigger/compute-firewall-delete   
    """
    auth_req = reqs.Request()
    CREDENTIAL.refresh(auth_req)
    token = CREDENTIAL.token
    header = {'Authorization': f"Bearer {token}"}
    query_params = "validateOnly=False"
    api_url = f"https://eventarc.googleapis.com/v1/projects/{PROJECT_ID}/locations/global/triggers/{trigger_id}?{query_params}"
    response = requests.delete(api_url, headers=header)
    result = response.json()
    pp(result)
    return "done"