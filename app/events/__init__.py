"""Eventarc Event Handler

This module contains the functions to handle Eventarc events

"""
from app.events.set_iam_policy import handle_set_iam_policy
from app.events.insert_firewall import handle_insert_firewall
from app.events.patch_firewall import handle_patch_firewall
from app.events.delete_firewall import handle_delete_firewall
from app.events.enable_service import handle_enable_service

# TODO: [Func] SetOrgPolicy

handlers = {
    'SetIamPolicy': handle_set_iam_policy,
    'InsertFirewall': handle_insert_firewall,
    'PatchFirewall': handle_patch_firewall,
    'DeleteFirewall': handle_delete_firewall,
    'EnableService': handle_enable_service
}
