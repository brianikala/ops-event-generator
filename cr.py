"""
This module provides methods communicating with Cloud Run
"""

def get_eventarc_trigger():
    # TMP
    result = {
        'trigger': 'cloud-resource-manager-SetIamPolicy', # CHANGED
        'location': 'global',
        'destination-run-service': 'demeter',
        'destination-run-region': 'asia-east1',
        'destination-run-path': '/SetIamPolicy', # CHANGED
        'type': 'google.cloud.audit.log.v1.written',
        'serviceName': 'cloudresourcemanager.googleapis.com',
        'methodName': 'SetIamPolicy', # CHANGED
        'service-account': '1097778675156-compute@developer.gserviceaccount.com' # default service account
    }

    # TODO: access ER BQ table enabled_event_list by accessing API of Admin run

    return result