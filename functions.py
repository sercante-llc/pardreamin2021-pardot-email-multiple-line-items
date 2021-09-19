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

def getListingFieldName(config, name, row):
    return config['Field Naming']['api_format'].replace('{d}', str(row)).replace('{field}', name)

def getFieldName(config, name):
    return getListingFieldName(config,name,'')

def createCustomField(config, fieldName, rowNum):
    fieldApiName = getListingFieldName(config,fieldName,rowNum)
    fieldLabel = config['Field Naming']['human_format'].replace('{d}', str(rowNum)).replace('{field}', fieldName)

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
        createCustomField(config, fieldName, rowNum)
        

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

def updateProspect(config, prospectId, prospectFields):
    # now we can prepare the API request
    apiUrl = '%s/api/prospect/version/%d/do/update/id/%s?format=json' % (config['Pardot']['url'], int(config['Pardot']['legacy_api_version']), prospectId)
    reqHeaders = {
        'Authorization': 'Bearer '+ config['Salesforce']['access_token'],
        'Pardot-Business-Unit-Id': config['Pardot']['business_unit_id']
    }
    r = requests.post(url=apiUrl, data=prospectFields, headers=reqHeaders)
    json = r.json()

    if r.status_code != 200 or json.get('@attributes').get('stat') != 'ok':
        print('Could not update prospect %s' % prospectId)
        print(json)
        sys.exit(7)

def updateProspectWithListingInfo(config, prospectId, listings, agentName):
    # first we need to build our Prospect Update Request data
    prospectFields = {}
    prospectFields[getFieldName(config, 'Count')] = len(listings)
    prospectFields[getFieldName(config, 'AgentName')] = agentName
    
    listingNumber=1
    for listing in listings:
        prospectFields[getListingFieldName(config, 'Price', listingNumber)] = listing['price']
        prospectFields[getListingFieldName(config, 'Bedrooms', listingNumber)] = listing['bedrooms']
        prospectFields[getListingFieldName(config, 'Bathrooms', listingNumber)] = listing['bathrooms']
        prospectFields[getListingFieldName(config, 'Sqft', listingNumber)] = listing['sqft']
        prospectFields[getListingFieldName(config, 'Address', listingNumber)] = listing['address']
        prospectFields[getListingFieldName(config, 'ListingUrl', listingNumber)] = listing['listing_url']
        prospectFields[getListingFieldName(config, 'ImageUrl', listingNumber)] = listing['image_url']
        listingNumber = listingNumber + 1

    print(prospectFields)
    updateProspect(config, prospectId, prospectFields)

def updateProspectCleaningListingFields(config, prospectId, listingCount):
    prospectFields = {}
    prospectFields[getFieldName(config, 'Count')] = ''
    prospectFields[getFieldName(config, 'AgentName')] = ''

    for i in range(1,listingCount+1):
        prospectFields[getListingFieldName(config, 'Price', i)] = ''
        prospectFields[getListingFieldName(config, 'Bedrooms', i)] = ''
        prospectFields[getListingFieldName(config, 'Bathrooms', i)] = ''
        prospectFields[getListingFieldName(config, 'Sqft', i)] = ''
        prospectFields[getListingFieldName(config, 'Address', i)] = ''
        prospectFields[getListingFieldName(config, 'ListingUrl', i)] = ''
        prospectFields[getListingFieldName(config, 'ImageUrl', i)] = ''
    updateProspect(config, prospectId, prospectFields)