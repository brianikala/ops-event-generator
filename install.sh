#!/bin/bash

# NOTE: This is script is used if gcloud command installing failed.

set -e

USER=iKala-Cloud

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


projectList=()
i=0
for pList in $(gcloud projects list --format='csv(projectId, projectNumber)')
do
    IFS=', ' read -r -a list <<< $pList
    PID="${list[0]}"
    PNO="${list[1]}"

    if test $i = 0 ; then
        printf "\tProject Number\tProject ID\n"
        echo "--------------------------"
    else 
        printf "(%s)\t%s\t%s\n" $i $PNO $PID
    fi
    
    projectList+=($PID)
    ((i=i+1))
done
read -e -n 100 -p "Please select the project you want to install the agent: " opt
echo "You select project ID: ${projectList[$opt]}"
PROJECT_ID=${projectList[$opt]}
echo

echo "Reading project metadata..."
PROJECT_NUMBER=$(gcloud projects describe ${PROJECT_ID} --format 'value(projectNumber)')
TOPIC_ID="${CUSTOMER}_${PROJECT_NUMBER}"
echo

printf "Topic ID:\t%s\nCustomer name:\t%s\nProject ID:\t%s\n\n" $TOPIC_ID $CUSTOMER $PROJECT_ID
echo "Is the configuration correct? (N/y): "
read -e -n 100 correct
[ -z "$correct" ] && agree="Y" 
if test "$correct" != "y" ; then
 exit
fi

# run gcloud command
gcloud run deploy demeter --region=asia-east1 --no-allow-unauthenticated \
    --image=gcr.io/cloud-tech-dev-2021/demeter:latest \
    --set-env-vars TOPIC_ID=$TOPIC_ID \
    --set-env-vars CUSTOMER=$CUSTOMER

echo "Installation completed!"