#!/bin/bash

####################################################################################
# NOTE: This is script is used if gcloud command installing failed.                #
####################################################################################

set -e

USER=iKala-Cloud
DEFAULT_CONFIG_PATH="./config.json"

echo "Welcome to iKala AIOps! This is the part of ops event generator."
echo "Please follow the prompted instructions to continue the installation."
echo "If you have any question, please contact gcp-arch@ikala.tv. Thanks for your choosing!"
echo

## Agreement
read -e -n 100 -p "By using iKala AIOps, you agree that you will obey iKala security policy? (Y/n): " agree
test -z "$agree" -o "$agree" = "y" && agree="Y"
if test "$agree" != "Y" ; then
    exit
fi

read -e -n 100 -p "Please input your name (registered in iKala): " CUSTOMER
echo "Your input name: ${CUSTOMER}"
echo

read -e -n 100 -p "Do you need to enable iKala Event Receiver Service? (y/N): " enable_event_receiver
test -z "$enable_event_receiver" && enable_event_receiver="N"

if test "$enable_event_receiver" = "N" -o "$enable_event_receiver" = "n" ; then
    read -e -n 100 -p "Please input the path of Eventarc config file (default): " config_path
    test -z "$config_path" && config_path="default"
    if test "$config_path" = "default" ; then
        echo "Requesting default config file..."
        curl -s https://raw.githubusercontent.com/iKala-Cloud/ops-event-generator/master/config/default.json > $DEFAULT_CONFIG_PATH
        config_path=$DEFAULT_CONFIG_PATH
    else
        test -e "$config_path" || echo "Config file not found: $config_path" && exit
    fi
fi

echo "Reading project metadata..."
PROJECT_NUMBER=$(gcloud projects describe ${DEVSHELL_PROJECT_ID} --format 'value(projectNumber)')
TOPIC_ID="${CUSTOMER}_${PROJECT_NUMBER}"
echo

# If the Event Receiver Service isn't enabled, Pub/Sub topic won't be used.
if test "$enable_event_receiver" = "N" -o "$enable_event_receiver" = "n" ; then
    printf "Customer name:\t%s\nProject ID:\t%s\n\n" $CUSTOMER $DEVSHELL_PROJECT_ID
else
    printf "Topic ID:\t%s\nCustomer name:\t%s\nProject ID:\t%s\n\n" $TOPIC_ID $CUSTOMER $DEVSHELL_PROJECT_ID
fi
echo "Is the configuration correct? (N/y): "
read -e -n 100 correct
[ "$correct" = "Y" ] && correct="y"
[ -z "$correct" -o "$correct" != "y" ] && correct="N"
if test "$correct" != "y" ; then
 exit
fi

# run gcloud command
# If the environment variable ENABLE_ER is not set, the default value is "false".
if test "$enable_event_receiver" = "N" -o "$enable_event_receiver" = "n" ; then
    gcloud run deploy demeter --region=asia-east1 --no-allow-unauthenticated \
        --image=gcr.io/cloud-tech-dev-2021/demeter \
        --min-instances=1 \
        --set-env-vars TOPIC_ID=$TOPIC_ID \
        --set-env-vars CUSTOMER=$CUSTOMER \
        --set-env-vars PROJECT_NUMBER=$PROJECT_NUMBER \
        --set-env-vars ENABLE_ER=false
else
    gcloud run deploy demeter --region=asia-east1 --no-allow-unauthenticated \
        --image=gcr.io/cloud-tech-dev-2021/demeter \
        --min-instances=1 \
        --set-env-vars TOPIC_ID=$TOPIC_ID \
        --set-env-vars CUSTOMER=$CUSTOMER \
        --set-env-vars PROJECT_NUMBER=$PROJECT_NUMBER \
        --set-env-vars ENABLE_ER=true
fi

##############################################################################

# Initializations

## Step 1: enable eventarc API
## https://cloud.google.com/endpoints/docs/openapi/enable-api#gcloud
gcloud config set project $DEVSHELL_PROJECT_ID
gcloud services enable eventarc.googleapis.com

## Step 2: configuration permissions
## https://cloud.google.com/eventarc/docs/run/quickstart
gcloud projects add-iam-policy-binding $DEVSHELL_PROJECT_ID \
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role='roles/eventarc.developer' \
    --condition=None

gcloud projects add-iam-policy-binding $DEVSHELL_PROJECT_ID \
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role='roles/eventarc.eventReceiver' \
    --condition=None

gcloud projects add-iam-policy-binding $DEVSHELL_PROJECT_ID \
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role='roles/eventarc.serviceAgent' \
    --condition=None

## Step 3: enable audit log for eventarc
echo "[Enabling audit log]"
echo "fetching configure script..."
curl -s https://raw.githubusercontent.com/iKala-Cloud/ops-event-generator/master/configAuditLog.py -o configAuditLog.py
echo "fetching IAM policy..."
gcloud projects get-iam-policy $DEVSHELL_PROJECT_ID --format yaml > /tmp/policy-get.yaml
echo "modifying IAM policy..."
# cat /tmp/policy-get.yaml
python3 configAuditLog.py
# cat /tmp/policy-set.yaml
echo "setting IAM policy..."
gcloud projects set-iam-policy $DEVSHELL_PROJECT_ID /tmp/policy-set.yaml
rm configAuditLog.py
echo "Audit log enabled"

## Step 4: create eventarc triggers
SERVICE_URL=$(gcloud run services describe demeter --region=asia-east1 --format 'value(status.url)')
if test "$enable_event_receiver" = "N" -o "$enable_event_receiver" = "n" ; then
    result=$(curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" -H "Content-Type: application/json" -d @${config_path} "${SERVICE_URL}/update/eventarc/triggers")
else
    result=$(curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" "${SERVICE_URL}/create/eventarc/triggers")
fi
if [ "$result" != "success" ]; then
    echo "Failed to create Cloud eventarc triggers. Check up the logs of demeter to know more detailed."
    echo "https://console.cloud.google.com/run/detail/asia-east1/demeter/logs?project=${DEVSHELL_PROJECT_ID}"
    progress="failed"
else
    progress="completed"
fi

echo

if [ "$progress" == "completed" ]; then
    echo "Installation completed!"
fi