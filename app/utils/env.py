""""Environment variables

The module contains the environment variables used in the application.
To avoid that the update of Cloud Run config isn't applied immediately,
get the environment variables every time when needed.

Dos:
def get_abc():
    return os.environ.get("ABC")

Don't:
# The global vairables won't be updated until the server restart
ABC = os.environ.get("ABC")

"""
import os

# TODO: [Config]: Make ER project id as the environment variable
ER_PROJECT_ID = "cloud-tech-dev-2021"

def get_port():
    """
    Returns the port number of the application.
    """
    return int(os.environ.get("PORT", 8080))

def get_customer():
    """
    Returns the customer name of the application.
    """
    return os.environ.get("CUSTOMER")

def get_topic_id():
    """
    Returns the topic id of the application.
    """
    return os.environ.get("TOPIC_ID")

def get_project_number():
    """
    Returns the project number of the application.
    """
    return os.environ.get("PROJECT_NUMBER")

def get_enable_er():
    """
    Returns the enable_er of the application.
    """
    enable_er = os.environ.get("ENABLE_ER")
    if enable_er is not None and enable_er.lower() in ('true', '1'):
        return True
    return False
