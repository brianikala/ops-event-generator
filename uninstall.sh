#!bin/bash

# delete eventarc trigger under service demeter
trigger_list=$(gcloud eventarc triggers list --format="get(name)" --filter=destination.cloudRun.service=demeter) 

if [ "$trigger_list" == "" ]
then
    echo "Could not found any trigger under service demeter"
else
    for trigger_id in $trigger_list
    do
        gcloud eventarc triggers delete $trigger_id --location=global
    done
fi

# delete cloud run service demeter
check_demeter_exist=$(gcloud run services list --format="get(metadata.name)" --filter=metadata.name=demeter)

if [ "$check_demeter_exist" == "demeter" ]
then
    gcloud run services delete demeter --region=asia-east1
else
    echo "Service demeter does not exist"
fi