"""Set IAM Policy

This module provides methods handle v1.compute.firewalls.delete events
"""
import sys

from app.utils.pubsub import publish

def handle_enable_service(headers, body): # Headers and body of requests from Eventarc Triggers
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
            'description': protoPayload['request']['description'] if 'description' in protoPayload['request'] else None,
            'allowed': [
                {
                    'IPProtocol': a['IPProtocol'] if 'IPProtocol' in a else '',
                    'ports': a['ports'] if 'ports' in a else [],
                } for a in protoPayload['request']['alloweds']
            ] if 'alloweds' in protoPayload['request'] else [],
            'denied': [
                {
                    'IPProtocol': d['IPProtocol'] if 'IPProtocol' in d else '',
                    'ports': d['ports'] if 'ports' in d else [],
                }
                for d in protoPayload['request']['denieds']
            ] if 'denieds' in protoPayload['request'] else [],
            'disabled': protoPayload['request']['disabled'] if 'disabled' in protoPayload['request'] else None,
            'logConfig': protoPayload['request']['logConfig'] if 'logConfig' in protoPayload['request'] else None,
            'priority': int(protoPayload['request']['priority']) if 'priority' in protoPayload['request'] else None,
            'sourceRanges': protoPayload['request']['sourceRanges'] if 'sourceRanges' in protoPayload['request'] else [],
            'sourceTags': protoPayload['request']['sourceTags'] if 'sourceTags' in protoPayload['request'] else [],
            'targetTags': protoPayload['request']['targetTags'] if 'targetTags' in protoPayload['request'] else [],
            'targetServiceAccounts': protoPayload['request']['targetServiceAccounts'] if 'targetServiceAccounts' in protoPayload['request'] else [],
            'name': protoPayload['request']['name'] if 'name' in protoPayload['request'] else None,
            'direction': protoPayload['request']['direction'] if 'direction' in protoPayload['request'] else None,
            'network': protoPayload['request']['network'] if 'network' in protoPayload['request'] else None,
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
