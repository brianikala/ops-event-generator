"""
This module provides methods communicating with Google Authentication APIs
"""

import google.auth

def get_project_id():
    # credential of env and project
    credentials, project_id = google.auth.default()
    print("project_id", project_id)

    if project_id:
        return project_id
    return ""

def get_default_service_account():
    """
    https://google-auth.readthedocs.io/en/latest/reference/google.auth.html
    If the application is running in Compute Engine or Cloud Run or the App Engine flexible environment
    or the App Engine standard environment (second generation) then the credentials and project ID are 
    obtained from the Metadata Service.
    
    NG:
    The value of credentials.service_account_email is always be "default" in Cloud Run, which is the default
    value of class Credentials object. That indicates the value is always an empty string in Cloud Run environment.
    """

    # credential of env and project
    credentials, project_id = google.auth.default()
    print(credentials, project_id)

    email = ""
    if hasattr(credentials, "service_account_email"):
        email = credentials.service_account_email
        print("Default service account:", email)
    else:
        print("WARNING: no service account credential. User account credential?")

    return email