import os
from flask import Flask

from auth import get_project_id
from adminrun import get_enabled_events, get_service_account


project_id = "cloud-tech-dev-2021" # prod
topic_id = os.environ.get("TOPIC_ID")

app = Flask(__name__)

#### ↓ ROUTE MAPS ↓ ####
from eventarc import trigger_creator
from eventarc.handlers import gcp_generic

app.add_url_rule('/module1', endpoint="module1", view_func=trigger_creator.hello_world, methods=["GET"])
app.add_url_rule(
    '/create/eventarc/triggers',
    endpoint='/create/eventarc/triggers',
    view_func=trigger_creator.create_eventarc_triggers,
    methods=['GET']
)
app.add_url_rule(
    '/delete/eventarc/trigger/<trigger_id>',
    endpoint='/delete/eventarc/trigger/',
    view_func=trigger_creator.delete_trigger,
    methods=['DELETE']
)

app.add_url_rule('/module2', endpoint="module2", view_func=gcp_generic.hello_world, methods=["GET"])
app.add_url_rule(
    '/eventarc/handler/gcp/<event_name>',
    endpoint="/eventarc/handler/gcp",
    view_func=gcp_generic.event_dispatcher,
    methods=["GET"]
)

#### ↑ ROUTE MAPS ↑ ####

###↓ DEVELOPEMENT ONLY ↓ ####

@app.route("/")
def hello_world():
    name = os.environ.get("NAME", "World")
    return "Hello {}!".format(name)

@app.route("/enabled_events")
def enabled_events():
    """
    curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
    https://demeter-xog7tpoz7a-de.a.run.app/enabled_events
    """
    project_id = get_project_id()
    events = get_enabled_events(project_id)
    return ''.join(events)

@app.route("/service_account")
def service_account():
    # TODO: 改成 call Admin Run API
    """
    curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
    https://demeter-xog7tpoz7a-de.a.run.app/service_account
    """    
    project_id = get_project_id()
    service_account = get_service_account(project_id)
    return service_account

#### ↑ DEVELOPEMENT ONLY ↑ ####

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
