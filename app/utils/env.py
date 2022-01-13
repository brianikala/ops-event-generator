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
