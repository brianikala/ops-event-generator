"""Set IAM Policy

This module provides methods handle SetIamPolicy events

"""
import sys
import json

from google.cloud import pubsub_v1

from app.utils.pubsub import publish

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

    future = publish(data)

    # TODO: [Log] Structured logging
    try:
        if future.result() is not None:
            print("Result: ", future.result())
            return (future.result(), 200)
        return ("Publisher Error", 502)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        return ("Server Error", 502)
