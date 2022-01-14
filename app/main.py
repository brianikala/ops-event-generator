"""Flask Server for OPs Event Generator"""
import json

from flask import Flask
from flask import request
from flask_apscheduler import APScheduler

from app.utils.env import get_port
from app.utils.adminrun import get_enabled_events
from app.utils.eventarc import create_eventarc_triggers, update_eventarc_triggers
from app import events

app = Flask(__name__)

#### ↓ SCHEDULERS ↓ ####
# TODO: [ER] Disable scheduler if not enable ER

class Config: # pylint-disable: too-few-public-methods
    """
    This class is used to configure whether to use the APScheduler APIs.

    Typical Usage:
        - [GET] /scheduler - returns basic information about the webapp
        - [GET] /scheduler/jobs - returns json with details of all jobs
        - [GET] /scheduler/job/<job_id> - returns json of job details

    For more information, check https://viniciuschiele.github.io/flask-apscheduler/rst/api.html
    """
    SCHEDULER_API_ENABLED = True
app.config.from_object(Config())

scheduler = APScheduler()
scheduler.init_app(app)

# Run at 00:00, 04:00, 08:00, 12:00, 16:00 and 20:00, every day
@scheduler.task('cron', id='update_eventarc', hour='*/4')
def update_eventarc():
    """Checks the Admin Run API and updates the Eventarc"""
    print(json.dumps({
        'severity': 'INFO',
        'message': 'Start to update eventarc triggers',
    }))
    update_eventarc_triggers()

scheduler.start()

#### ↑ SCHEDULERS ↑ ####

#### ↓ APIS ↓ ####

@app.route('/', methods=['GET'])
def hello_world():
    """Health check API

    Typical Usage:
    curl -X GET "$RUN_URL" \
    -H "Authorization: Bearer $(gcloud auth print-identity-token)"

    """
    return 'Hello World!'

@app.route('/enabled_events', methods=['GET'])
def enabled_events():
    """API to get the enabled events

    Typical Usage:
    curl -X GET "$RUN_URL/enabled_events" \
    -H "Authorization: Bearer $(gcloud auth print-identity-token)"

    """
    # TODO: [ER] get enabled events from eventarc if not enable ER
    events = get_enabled_events()
    return json.dumps(events)

@app.route('/create/eventarc/triggers', methods=['GET'])
def create_eventarc():
    """API to create eventarc triggers

    Typical Usage:
    curl -X GET "$RUN_URL/create/eventarc/triggers" \
    -H "Authorization: Bearer $(gcloud auth print-identity-token)"

    """
    # TODO: [ER] Receive the config data if not enable ER
    result = create_eventarc_triggers()
    return result

@app.route('/eventarc/handler/gcp/<event_name>', methods=['POST'])
def eventarc_handler(event_name):
    """API to handle eventarc events

    Typical Usage:
    curl -X POST "$RUN_URL/eventarc/handler/gcp/event_name" \
    -H "Authorization: Bearer $(gcloud auth print-identity-token)" \

    """
    headers = dict(request.headers)
    body = dict(request.json)
    print(json.dumps({
        'severity': 'INFO',
        'message': f'Received eventarc event: {event_name}',
        'headers': headers,
        'body': body,
    }))
    if event_name in events.handlers:
        result = events.handlers[event_name](headers, body)
        print(json.dumps({
            'severity': 'INFO',
            'message': f'Successfully handle eventarc event: {event_name}',
            'headers': headers,
            'body': body,
            'result': result,
        }))
        return result
    print(json.dumps({
        'severity': 'INFO',
        'message': f'Method not supported: {event_name}',
        'headers': headers,
        'body': body
    }))
    return f'Method not supported: {event_name}'

#### ↑ APIS ↑ ####

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=get_port())
