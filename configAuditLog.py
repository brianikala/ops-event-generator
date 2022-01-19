import yaml

with open('/tmp/policy-get.yaml', 'r') as getf:
    data = yaml.load(getf, Loader=yaml.FullLoader)

print('[Before]')
print(yaml.dump(data['auditConfigs']))

services = [d['service'] for d in data['auditConfigs']]

# Audit log for cloud-resource-manager-set-*-policy
if 'cloudresourcemanager.googleapis.com' not in services:    
    data['auditConfigs'].append({
        'auditLogConfigs': [
                { "logType": "ADMIN_READ" },
                { "logType": "DATA_WRITE" },
                { "logType": "DATA_READ" }
        ],
        'service': 'cloudresourcemanager.googleapis.com'
    })
else:
    print('Audit log of Cloud Resource Manager API already enable')

# Audit log for compute-firewall-*
if 'compute.googleapis.com' not in services:  
    data['auditConfigs'].append({
        'auditLogConfigs': [
                { "logType": "ADMIN_READ" },
                { "logType": "DATA_WRITE" },
                { "logType": "DATA_READ" }
        ],
        'service': 'compute.googleapis.com'
    })
else:
    print('Audit log of Compute Engine API already enable')

print('-----------------------------\n')
print('[After]')
print(yaml.dump(data['auditConfigs']))

with open('/tmp/policy-set.yaml', 'w') as setf:
    yaml.dump(data, setf, default_flow_style=False)
