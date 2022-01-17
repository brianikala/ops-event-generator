#!/bin/bash

####################################################################################
# NOTE: This is script is used if gcloud command installing failed.                #
####################################################################################

set -e

USER=iKala-Cloud
DEFAULT_CONFIG_PATH="./config/default.json"

echo "Welcome to iKala AIOps! This is the part of ops event generator."
echo "Please follow the prompted instructions to continue the installation."
echo "If you have any question, please contact gcp-arch@ikala.tv. Thanks for your choosing!"
echo

## Agreement
read -e -n 100 -p "By using iKala AIOps, you agree that you will obey iKala security policy? (Y/n): " agree
test -z "$agree" && agree="Y" 
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
        curl -s https://raw.githubusercontent.com/iKala-Cloud/ops-event-generator/feature-disable-er/config/default.json > $CONFIG_PATH
    else
        test -e "$config_path" || echo "Config file not found: $config_path" && exit
    fi
fi

####################################################################################
# Select project to install EG (DEPRECATED)
# projectList=()
# i=0
# for pList in $(gcloud projects list --format='csv(projectId, projectNumber)')
# do
#     IFS=', ' read -r -a list <<< $pList
#     PID="${list[0]}"
#     PNO="${list[1]}"

#     if test $i = 0 ; then
#         printf "\tProject Number\tProject ID\n"
#         echo "--------------------------"
#     else 
#         printf "(%s)\t%s\t%s\n" $i $PNO $PID
#     fi
    
#     projectList+=($PID)
#     ((i=i+1))
# done
# read -e -n 100 -p "Please select the project you want to install the agent: " opt
# echo "You select project ID: ${projectList[$opt]}"
# PROJECT_ID=${projectList[$opt]}
# echo
####################################################################################

echo "Reading project metadata..."
PROJECT_NUMBER=$(gcloud projects describe ${DEVSHELL_PROJECT_ID} --format 'value(projectNumber)')
TOPIC_ID="${CUSTOMER}_${PROJECT_NUMBER}"
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
echo

# If the Event Receiver Service isn't enabled, Pub/Sub topic won't be used.
if test "$enable_event_receiver" = "N" -o "$enable_event_receiver" = "n" ; then
    printf "Customer name:\t%s\nProject ID:\t%s\n\n" $CUSTOMER $DEVSHELL_PROJECT_ID
else
    printf "Topic ID:\t%s\nCustomer name:\t%s\nProject ID:\t%s\n\n" $TOPIC_ID $CUSTOMER $DEVSHELL_PROJECT_ID
fi
echo "Is the configuration correct? (N/y): "
read -e -n 100 correct
[ -z "$correct" ] && agree="Y" 
if test "$correct" != "y" ; then
 exit
fi

# run gcloud command
# If the environment variable ENABLE_ER is not set, the default value is "false".
if test "$enable_event_receiver" = "N" -o "$enable_event_receiver" = "n" ; then
    gcloud run deploy demeter --region=asia-east1 --no-allow-unauthenticated \
        --image=gcr.io/cloud-tech-dev-2021/demeter-test \
        --min-instances=1 \
        --set-env-vars TOPIC_ID=$TOPIC_ID \
        --set-env-vars CUSTOMER=$CUSTOMER \
        --set-env-vars PROJECT_NUMBER=$PROJECT_NUMBER \
        --set-env-vars ENABLE_ER=false
else
    gcloud run deploy demeter --region=asia-east1 --no-allow-unauthenticated \
        --image=gcr.io/cloud-tech-dev-2021/demeter-test \
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

## Step 3: create eventarc triggers
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
fi
    
echo

if [ "$progress" == "completed" ]; then
    echo "Installation completed!"
fi
