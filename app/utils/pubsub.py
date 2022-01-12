"""Pub/Sub

This module contains the functions to interact with Pub/Sub

"""
import json

from google.cloud import pubsub_v1

from app.utils.env import get_topic_id, ER_PROJECT_ID

def publish(data):
    """Publish a message to a Pub/Sub topic."""
    topic_id = get_topic_id()
    publisher = pubsub_v1.PublisherClient()

    # The `topic_path` method creates a fully qualified identifier
    # in the form `projects/{project_id}/topics/{topic_id}`
    topic_path = publisher.topic_path(ER_PROJECT_ID, topic_id)

    # Data must be a bytestring
    data = json.dumps(data).encode("utf-8")

    # When you publish a message, the client returns a future.
    future = publisher.publish(topic_path, data, retry=None)

    return future
