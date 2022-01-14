"""Set IAM Policy

This module provides methods handle v1.compute.firewalls.delete events

"""
import sys

from app.utils.pubsub import publish

def handle_delete_firewall(headers, body):
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
            'status': protoPayload['status'] if 'status' in protoPayload and protoPayload['status'] else None,
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
