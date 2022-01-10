"""Eventarc Event Handler

This module contains the functions to handle Eventarc events

"""
from app.events.set_iam_policy import handle_set_iam_policy

# TODO: [Func] SetOrgPolicy
# TODO: [Func] v1.compute.firewalls.insert
# TODO: [Func] v1.compute.firewalls.patch
# TODO: [Func] v1.compute.firewalls.delete

handlers = {
    'SetIamPolicy': handle_set_iam_policy,
}
