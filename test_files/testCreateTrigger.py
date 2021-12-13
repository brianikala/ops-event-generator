import requests
import json

from google.auth.transport import requests as reqs
from google.auth import default

"""
https://cloud.google.com/eventarc/docs/reference/rest/v1/projects.locations.triggers/create

curl -H "Authorization: Bearer $(gcloud auth print-access-token)" -H "Content-type: application/json" 
https://eventarc.googleapis.com/v1/projects/customer-a-project-1/locations/global/triggers
"""

REGION = 'global'
PROJECT = 'customer-a-project-1'
EVENTARC_API_URL = f"https://eventarc.googleapis.com/v1/projects/{PROJECT}/locations/{REGION}/triggers?triggerId=thenameoftrigger&validateOnly=False"

creds, project = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
auth_req = reqs.Request()
creds.refresh(auth_req)
token = creds.token
header = {'Authorization': f"Bearer {token}"}

with open("./createConfig.json") as f:
    data = json.load(f)
    print(data)
    response = requests.post(EVENTARC_API_URL, headers=header, json=data)
    print(response.json())

"""
不論是用這個 script 還是 curl

$ curl -H "Authorization: Bearer $(gcloud auth print-access-token)" \
    -H "Content-type: application/json"  -X POST -d @createConfig.json \
    https://eventarc.googleapis.com/v1/projects/customer-a-project-1/locations/global/triggers\?triggerId\=thenameoftrigger\&validateOnly\=True

都回傳空集合 {}
然後沒有新建立 trigger
但是用 gcloud 就成功了:

$ gcloud eventarc triggers create hkhkd04 \
    --location=global \
    --destination-run-service="demeter" \
    --destination-run-region="asia-east1" \
    --destination-run-path="/eventarc" \
    --event-filters="type=google.cloud.audit.log.v1.written" \
    --event-filters="serviceName=cloudresourcemanager.googleapis.com" \
    --event-filters="methodName=GetIamPolicy" \
    --service-account=1097778675156-compute@developer.gserviceaccount.com
Creating trigger [hkhkd04] in project [customer-a-project-1], location [global]...done.
WARNING: It may take up to 10 minutes for the new trigger to become active.    
"""