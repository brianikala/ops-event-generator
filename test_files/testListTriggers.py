import requests

from google.auth.transport import requests as reqs
from google.auth import default

"""
https://cloud.google.com/eventarc/docs/reference/rest/v1/projects.locations.triggers/list

curl -H "Authorization: Bearer $(gcloud auth print-access-token)" -H "Content-type: application/json" 
https://eventarc.googleapis.com/v1/projects/customer-a-project-1/locations/global/triggers
"""

REGION = 'asia-east1'
PROJECT = 'customer-a-project-1'
EVENTARC_API_URL = f"https://eventarc.googleapis.com/v1/projects/{PROJECT}/locations/{REGION}/triggers"

creds, project = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
auth_req = reqs.Request()
creds.refresh(auth_req)
token = creds.token
header = {'Authorization': f"Bearer {token}"}
response = requests.get(EVENTARC_API_URL, headers=header)
print(response.json())

"""
$ curl -H "Authorization: Bearer $(gcloud auth print-access-token)" -H "Content-type: application/json" 
https://eventarc.googleapis.com/v1/projects/customer-a-project-1/locations/asia-east1/triggers
{}  # {}   ???

為什麼在 asia-east1 是空的？

------

$ gcloud eventarc triggers list --location=asia-east1
Listed 0 items.

真的耶！？credential 也沒錯啊？

------

啊～看了一下 Benson 哥的實作，他的 location 指定為 global (cloud run 內的 eventarc 的關係？)
改一下後再查詢就有了：
$ gcloud eventarc triggers list --location=global
NAME                                   TYPE                               DESTINATION         ACTIVE
cloud-resource-manager-set-iam-policy  google.cloud.audit.log.v1.written  Cloud Run: demeter  Yes

$ curl -H "Authorization: Bearer $(gcloud auth print-access-token)" -H "Content-type: application/json"  https://eventarc.googleapis.com/v1/projects/customer-a-project-1/locations/global/triggers
{
  "triggers": [
    {
      "name": "projects/customer-a-project-1/locations/global/triggers/cloud-resource-manager-set-iam-policy",
      "uid": "ec3c5ee3-2193-49fd-ac4a-04dddcdc8b63",
      "createTime": "2021-10-26T09:14:31.513262109Z",
      "updateTime": "2021-10-26T09:14:40.633511189Z",
      "eventFilters": [
        {
          "attribute": "methodName",
          "value": "SetIamPolicy"
        },
        {
          "attribute": "type",
          "value": "google.cloud.audit.log.v1.written"
        },
        {
          "attribute": "serviceName",
          "value": "cloudresourcemanager.googleapis.com"
        }
      ],
      "serviceAccount": "1097778675156-compute@developer.gserviceaccount.com",
      "destination": {
        "cloudRun": {
          "service": "demeter",
          "path": "/eventarc",
          "region": "asia-east1"
        }
      },
      "transport": {
        "pubsub": {
          "topic": "projects/customer-a-project-1/topics/eventarc-global-cloud-resource-manager-set-iam-policy-561",
          "subscription": "projects/customer-a-project-1/subscriptions/eventarc-global-cloud-resource-manager-set-iam-policy-sub-561"
        }
      }
    }
  ]
}
"""