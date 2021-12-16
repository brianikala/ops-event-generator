#!/bin/bash

# NOTE: This is script is used if gcloud command installing failed.

set -e

export USER=iKala-Cloud

echo "Welcome to iKala AIOps! This is the part of ops event generator."
echo "Please follow the prompted instructions to continue the installation."
echo "If you have any question, please contact gcp-arch@ikala.tv. Thanks for your choosing!"
echo
read -e -n 100 -p "Please input your name (registered in iKala): " CUSTOMER

echo $CUSTOMER

## Agreement
read -e -n 100 -p "By using iKala AIOps, you agree that you will obey iKala security policy.(Y/n)?: " agree
[ -z "$agree" ] && agree="Y" 
if [ "$agree" != "Y" ]; then
 exit
fi

# TODO: run gcloud command
# gcloud run deploy demeter --region=asia-east1 --set-env-vars TOPIC_ID=$CUSTOMER_1097778675156 --set-env-vars CUSTOMER=$CUSTOMER --source .

echo "Installation completed!"
