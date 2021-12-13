import os, sys
import json

from flask import request

from google.cloud import pubsub_v1

project_id = "cloud-tech-dev-2021" # prod
topic_id = os.environ.get("TOPIC_ID")

def hello_world():
    return "eventarc/handlers/gcp_generic"

# NOTE: 現在是每個 event 都會呼叫同一個 handler，之後如果有針對不同 event 要有客製化的 handler 就加入此
def event_dispatcher(event_name):
    print(event_name)
    handler = {
        "SetIamPolicy": eventarc_generic_handler
    }

    handler[event_name]()
    return f"method: {event_name}, result:"

def eventarc_generic_handler():
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