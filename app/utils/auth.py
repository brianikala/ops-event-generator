"""Authentication

This module provides methods communicating with Google Authentication APIs

"""
import google.auth
from google.auth import default
from google.auth.transport import requests as reqs

def get_project_id():
    """Gets the project ID from Application Default Credentials."""
    # credential of env and project
    credentials, project_id = google.auth.default()

    if project_id:
        return project_id
    return ""

def get_credential_token():
    """Gets the token from Application Default Credentials."""
    credential, project_id = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_req = reqs.Request()
    credential.refresh(auth_req)
    token = credential.token
    return token, project_id
