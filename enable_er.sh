#!/bin/bash

####################################################################################
# NOTE: This is script is used if gcloud command installing failed.                #
####################################################################################

set -e

USER=iKala-Cloud

echo "Welcome to iKala AIOps! This is the part of ops event generator."
echo "Please follow the prompted instructions to continue the installation."
echo "If you have any question, please contact gcp-arch@ikala.tv. Thanks for your choosing!"
echo

printf "Project ID:\t%s\n\n" $DEVSHELL_PROJECT_ID
echo "Is the configuration correct? (N/y): "
read -e -n 100 correct
[ "$correct" = "Y" ] && correct="y"
[ -z "$correct" -o "$correct" != "y" ] && correct="N"
if test "$correct" != "y" ; then
 exit
fi

echo "Do you sure to enable iKala Event Receiver Service? (N/y): "
read -e -n 100 sure
[ "$sure" = "Y" ] && sure="y"
[ -z "$sure" -o "$sure" != "y" ] && sure="N"
if test "$sure" != "y" ; then
 exit
fi

gcloud run service update demeter --region=asia-east1 \
    --update-env-vars ENABLE_ER=true

SERVICE_URL=$(gcloud run services describe demeter --region=asia-east1 --format 'value(status.url)')

result=$(curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" "${SERVICE_URL}/create/eventarc/triggers")

if [ "$result" != "success" ]; then
  echo "Failed to create Cloud eventarc triggers. Check up the logs of demeter to know more detailed."
  echo "https://console.cloud.google.com/run/detail/asia-east1/demeter/logs?project=${DEVSHELL_PROJECT_ID}"
  progress="failed"
else
  progress="completed"
fi

echo

if [ "$progress" == "completed" ]; then
    echo "Enabling Eventarc Receiver Service completed!"
fi
