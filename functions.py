import configparser, json, requests, sys

def readConfig():
    #read our app config
    print('Reading configuration from config/app.ini ...')
    config = configparser.ConfigParser()
    config.read('config/app.ini')
    print('Configuration loaded')
    return config

def authenticate(config):
    print('Authenticating to Salesforce')
    authReqData = {
        'grant_type':'password',
        'client_id':config['Salesforce']['consumer_key'],
        'client_secret':config['Salesforce']['consumer_secret'],
        'username': config['Salesforce']['username'],
        'password': config['Salesforce']['password'] + config['Salesforce']['security_token']
    }
    tokenUrl = config['Salesforce']['url'] + '/services/oauth2/token'

    r = requests.post(tokenUrl, data=authReqData)

    # print(r.json())
    if r.status_code == 200:
        print('Got access token, ready to make API requests')
        config['Salesforce']['access_token'] = r.json().get('access_token')
    else:
        print('Had trouble getting access token. Make sure User and Connected App are correctly configured in config/app.ini')
        print('Status:{}, {}: {}'.format(r.status_code, r.json().get('error'), r.json().get('error_description') ))
        sys.exit(1)

def createCustomField(config, fieldName, rowNum):
    fieldApiName = config['Field Naming']['api_format'].replace('{d}', rowNum).replace('{field}', fieldName)
    fieldLabel = config['Field Naming']['human_format'].replace('{d}', rowNum).replace('{field}', fieldName)

    apiUrl = '%s/api/customField/version/%d/do/create?format=json' % (config['Pardot']['url'], int(config['Pardot']['legacy_api_version']))
    reqData = {
        'name': fieldLabel,
        'field_id': fieldApiName
    }
    reqHeaders = {
        'Authorization': 'Bearer '+ config['Salesforce']['access_token'],
        'Pardot-Business-Unit-Id': config['Pardot']['business_unit_id']
    }
    r = requests.post(url=apiUrl, data=reqData, headers=reqHeaders)
    json = r.json()

    if r.status_code == 200 and json.get('@attributes').get('stat') == 'ok':
        print('Successfully created %s' % fieldApiName)
        fieldId = json.get('customField').get('id')
        storeCreatedCustomField(fieldApiName, fieldId)
    else:
        print('Could not create custom field')
        print(json)
        sys.exit(2)

def createCustomFields(config, fieldNames, rowNum):
    for fieldName in fieldNames:
        createCustomField(config, fieldName, str(rowNum))
        

def storeCreatedCustomField(fieldApiName, fieldId):
    f = open('config/fields.csv','a')
    f.write('%s,%d\n' % (fieldApiName, fieldId))
    f.close()

def deleteCustomField(config, fieldApiName, fieldId):
    apiUrl = '%s/api/customField/version/%d/do/delete/id/%d?format=json' % (config['Pardot']['url'], int(config['Pardot']['legacy_api_version']), fieldId)
    reqHeaders = {
        'Authorization': 'Bearer '+ config['Salesforce']['access_token'],
        'Pardot-Business-Unit-Id': config['Pardot']['business_unit_id']
    }
    r = requests.delete(url=apiUrl,headers=reqHeaders)
    if r.status_code == 204:
        print('Successfully deleted %s' % fieldApiName)
    else:
        print('Could not create custom field')
        print(json)
        sys.exit(2)