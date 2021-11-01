import os, sys
import json
import subprocess
from flask import Flask, request

from google.cloud import pubsub_v1

from auth import get_project_id
from cr import get_eventarc_trigger
from customer_data import get_enabled_events, get_service_account


project_id = "cloud-tech-dev-2021" # prod
# project_id = "ikala-cloud-sandbox-veck" # dev
topic_id = os.environ.get("TOPIC_ID")

app = Flask(__name__)

#### ↓ DEVELOPEMENT ONLY ↓ ####

@app.route("/")
def hello_world():
    name = os.environ.get("NAME", "World")
    return "Hello {}!".format(name)

# DEVELOPEMENT ONLY
"""
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
https://demeter-xog7tpoz7a-de.a.run.app/enabled_events
"""
@app.route("/enabled_events")
def enabled_events():
    project_id = get_project_id()
    customer = 'a' # FIXME: should not be hard-coded

    events = get_enabled_events(customer, project_id)
    return ''.join(events)

# TODO: 改成 call Admin Run API
"""
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
https://demeter-xog7tpoz7a-de.a.run.app/service_account
"""
@app.route("/service_account")
def service_account():
    project_id = get_project_id()
    service_account = get_service_account(project_id)
    return service_account

#### ↑ DEVELOPEMENT ONLY ↑ ####

# eventarc_generic_handler
# the path matches to eventarc trigger in Cloud Run service demeter
@app.route('/eventarc', methods=['POST'])
def eventarc():
    print('Event received!')

    print('HEADERS:')
    headers = dict(request.headers)
    headers.pop('Authorization', None)  # do not log authorization header if exists
    print(headers)

    print('BODY:')
    body = dict(request.json)
    print(body)

    protoPayload = body['protoPayload']


    data = {
        'body': {
            'logName': body['logName'],
            'severity': body['severity'],
            'serviceName': protoPayload['serviceName'],
            'resourceName': protoPayload['resourceName'],
            'methodName': protoPayload['methodName'],
            'callerIp': protoPayload['requestMetadata']['callerIp'],
            'principalEmail': protoPayload['authenticationInfo']['principalEmail'],
            'bindingDeltas': protoPayload['serviceData']['policyDelta']['bindingDeltas'] if 'policyDelta' in protoPayload['serviceData'] else [],
            'status': protoPayload['status'] if protoPayload['status'] else None
        },
        'header': {
            'resourceName': headers['Ce-Resourcename'],
            'recordedTime': headers['Ce-Recordedtime'],
            'methodName': headers['Ce-Methodname']
        }
    }

    publisher = pubsub_v1.PublisherClient()
    # The `topic_path` method creates a fully qualified identifier
    # in the form `projects/{project_id}/topics/{topic_id}`
    topic_path = publisher.topic_path(project_id, topic_id)

    # Data must be a bytestring
    data = json.dumps(data).encode("utf-8")

    # When you publish a message, the client returns a future.
    future = publisher.publish(topic_path, data, retry=None)

    try:
        if future.result() is not None:
            print("Result: ", future.result())
            return (future.result(), 200)
        return ("Publisher Error", 502)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        return ("Server Error", 502)

# create eventarc trigger
@app.route('/connect')
def create_eventarc_trigger():
    """
    doc:
    https://cloud.google.com/sdk/gcloud/reference/eventarc/triggers/create

    command:
    gcloud eventarc triggers create TRIGGER \
    --location=global \
    --destination-run-service=DESTINATION_RUN_SERVICE \
    --destination-run-region=DESTINATION_RUN_REGION \
    --destination-run-path=DESTINATION_RUN_PATH
    --event-filters="type=google.cloud.audit.log.v1.written" \
    --event-filters="serviceName=cloudresourcemanager.googleapis.com" \
    --event-filters="methodName=SetIamPolicy" \
    --service-account=1097778675156-compute@developer.gserviceaccount.com
    """

    event = get_eventarc_trigger()

    if(subprocess.run(["gcloud", "eventarc", "triggers", "create",
                        f"{event['trigger']}",
                        f"--location={event['location']}", f"--destination-run-service={event['destination-run-service']}",
                        f"--destination-run-region={event['destination-run-region']}", f"--destination-run-path={event['destination-run-path']}",
                        f"--event-filters=type={event['type']}",
                        f"--event-filters=serviceName={event['serviceName']}",
                        f"--event-filters=methodName={event['methodName']}",
                        f"--service-account={event['service-account']}"]).returncode==0):

        return "Connection succeeded"

    return "Connection failed"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
