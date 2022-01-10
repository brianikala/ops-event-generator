"""Set IAM Policy

This module provides methods handle SetIamPolicy events

"""
import sys
import json

from google.cloud import pubsub_v1

from app.utils.env import get_topic_id

# TODO: [Config]: Make ER project id as the environment variable
PROJECT_ID = "cloud-tech-dev-2021"

def handle_set_iam_policy(headers, body):
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
            'bindingDeltas': protoPayload['serviceData']['policyDelta']['bindingDeltas'] if 'policyDelta' in protoPayload['serviceData'] and 'bindingDeltas' in protoPayload['serviceData']['policyDelta'] else [],
            'status': protoPayload['status'] if protoPayload['status'] else None
        },
        'header': {
            'resourceName': headers['Ce-Resourcename'],
            'recordedTime': headers['Ce-Recordedtime'],
            'methodName': headers['Ce-Methodname']
        }
    }

    # TODO: [Mod] Modulize the pubsub procedure
    topic_id = get_topic_id()
    publisher = pubsub_v1.PublisherClient()

    # The `topic_path` method creates a fully qualified identifier
    # in the form `projects/{project_id}/topics/{topic_id}`
    topic_path = publisher.topic_path(PROJECT_ID, topic_id)

    # Data must be a bytestring
    data = json.dumps(data).encode("utf-8")

    # When you publish a message, the client returns a future.
    future = publisher.publish(topic_path, data, retry=None)

    # TODO: [Log] Structured logging
    try:
        if future.result() is not None:
            print("Result: ", future.result())
            return (future.result(), 200)
        return ("Publisher Error", 502)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        return ("Server Error", 502)
