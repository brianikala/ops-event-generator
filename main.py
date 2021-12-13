import os
from flask import Flask

from auth import get_project_id
from customer_data import get_enabled_events, get_service_account


project_id = "cloud-tech-dev-2021" # prod
topic_id = os.environ.get("TOPIC_ID")

app = Flask(__name__)

# Route Maps
from eventarc import trigger_creator
from eventarc.handlers import gcp_generic

# NEEDLESS. DEFINE RULES IN VIEW FILES SEPEARATELY
# app.add_url_rule('/user/<username>', view_func=views.user)
# app.add_url_rule('/eventarc/trigger/creator', endpoint='index', view_func=trigger_creator.hello_world)


#### ↓ DEVELOPEMENT ONLY ↓ ####

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
    customer = os.environ.get("CUSTOMER")

    events = get_enabled_events(customer, project_id)
    return ''.join(events)

@app.route("/service_account")
def service_account():
    # TODO: 改成 call Admin Run API
    """
    curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
    https://demeter-xog7tpoz7a-de.a.run.app/service_account
    """    
    project_id = get_project_id()
    customer = os.environ.get("CUSTOMER")
    service_account = get_service_account(customer, project_id)
    return service_account

#### ↑ DEVELOPEMENT ONLY ↑ ####

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
