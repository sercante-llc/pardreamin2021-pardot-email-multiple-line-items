"""These functions support the rest of the demo.

This file simply provides functions that can be reused. In a real production
codebase, it would be best to separate different types of logic into their
own dedicated classes so that they can be reused a little bit better.
"""
import configparser, json, requests, sys

def readConfig():
    """Reads configuration from `config/app.ini`, making it available to app

    Returns:
        A 2 dimensional dict mapping groups and keys to their configuration
        values. For example:

        config['Pardot']['url'] will provide the Pardot URL for API requests
    """
    print('Reading configuration from config/app.ini ...')
    config = configparser.ConfigParser()
    config.read('config/app.ini')
    print('Configuration loaded')
    return config

def authenticate(config):
    """Authenticates to Salesforce API using Username/Password Oauth Flow.

    Once authenticated, the accessToken is stored IN MEMORY in the config dict
    accessible by config['Salesforce']['access_token']

    If possible, it is highly recommended to NOT use the Username/Password
    Oauth Flow, as it requires your code/configuration to have sensitive
    information such as password and security token. We recommend using the
    JWT Bearer flow with a certificate, though chose this approach to keep
    the demo simple.

    Args:
        config:
            The configuration dict that could have been loaded from the
            readConfig method above in this file
    """
    print('Authenticating to Salesforce')
    authReqData = {
        'grant_type':'password',
        'client_id':config['Salesforce']['consumer_key'],
        'client_secret':config['Salesforce']['consumer_secret'],
        'username': config['Salesforce']['username'],
        'password': config['Salesforce']['password'] + config['Salesforce']['security_token']
    }
    tokenUrl = config['Salesforce']['url'] + '/services/oauth2/token'

    response = requests.post(tokenUrl, data=authReqData)

    # print(response.json()) # uncomment this line to view the response JSON if you are having troubles
    if response.status_code == 200:
        print('Got access token, ready to make API requests')
        config['Salesforce']['access_token'] = response.json().get('access_token')
    else:
        print('Had trouble getting access token. Make sure User and Connected App are correctly configured in config/app.ini')
        print('Status:{}, {}: {}'.format(r.status_code, response.json().get('error'), response.json().get('error_description') ))
        sys.exit(1)

# ****************************************************************************
# These functions support the set up and tear down of the demo. Useful to look
# at, but not necessarily required for a solution to work
# ****************************************************************************
def createCustomField(config, fieldName, rowNum):
    """Creates a single Custom Field via Pardot API.

    Upon successful creation of a Custom Field, the file config/fields.csv
    will be created/appended to include details for the field, so that it can
    be removed later on

    Args:
        config:
            The configuration dict that could have been loaded from the
            readConfig method above in this file
        fieldName:
            The trailing piece of the Field Name, used for both 
            Label and API name of the Custom Field
        rowNum:
            As custom fields might be created for multiple line items, 
            this arg is used to include the line item number in the
            Label and API name of the Custom Field
    """
    fieldApiName = config['Field Naming']['api_format'].replace('{d}', str(rowNum)).replace('{field}', fieldName)
    fieldLabel = config['Field Naming']['human_format'].replace('{d}', str(rowNum)).replace('{field}', fieldName)

    apiUrl = '{pardotUrl}/api/customField/version/{legacyVersion}/do/create?format=json' \
            .format(pardotUrl=config['Pardot']['url'], \
                    legacyVersion=config['Pardot']['legacy_api_version'])

    reqData = {
        'name': fieldLabel,
        'field_id': fieldApiName
    }
    reqHeaders = {
        'Authorization': 'Bearer '+ config['Salesforce']['access_token'],
        'Pardot-Business-Unit-Id': config['Pardot']['business_unit_id']
    }
    response = requests.post(url=apiUrl, data=reqData, headers=reqHeaders)
    json = response.json()

    if response.status_code == 200 and json.get('@attributes').get('stat') == 'ok':
        print('Successfully created {fieldName}'.format(fieldName=fieldApiName))
        fieldId = json.get('customField').get('id')
        # store the created field in a CSV so that it can be later deleted
        f = open('config/fields.csv','a')
        f.write('{fieldName},{fieldId}\n'.format(fieldName=fieldApiName, fieldId=fieldId))
        f.close()
    else:
        print('Could not create custom field')
        print(json)
        sys.exit(2)

def createCustomFields(config, fieldNames, rowNum):
    """Creates a list of Custom Fields via Pardot API.

    This function simply wraps the previous createCustomField function,
    creating 1 field at a time.

    Args:
        config:
            The configuration dict that could have been loaded from the
            readConfig method above in this file
        fieldNames:
            A list of field names that will be created, used for both
            Label and API name of the Custom Field
        rowNum:
            As custom fields might be created for multiple line items, 
            this arg is used to include the line item number in the
            Label and API name of the Custom Field
    """
    for fieldName in fieldNames:
        createCustomField(config, fieldName, rowNum)

def deleteCustomField(config, fieldApiName, fieldId):
    """Deletes a single Custom Field via Pardot API.

    Args:
        config:
            The configuration dict that could have been loaded from the
            readConfig method above in this file
        fieldApiName:
            The API Name of the Custom Field that is being deleted. Not used
            in the API request itself, though helpful to display in console
            output
        fieldId:
            The Custom Field Id for the Custom Field in Pardot.
    """
    apiUrl = '{pardotUrl}/api/customField/version/{legacyVersion}/do/delete/id/{fieldId}?format=json' \
            .format(pardotUrl = config['Pardot']['url'], \
                    legacyVersion=config['Pardot']['legacy_api_version'], \
                    fieldId=fieldId)
    reqHeaders = {
        'Authorization': 'Bearer '+ config['Salesforce']['access_token'],
        'Pardot-Business-Unit-Id': config['Pardot']['business_unit_id']
    }
    response = requests.delete(url=apiUrl,headers=reqHeaders)
    if response.status_code == 204:
        print('Successfully deleted {fieldName}'.format(fieldName=fieldApiName))
    else:
        print('Could not create custom field {fieldName}'.format(fieldName=fieldApiName))
        print(json)
        sys.exit(3)
# ****************************************************************************
# End of functions that support the set up and tear down of the demo
# ****************************************************************************

def updateProspect(config, prospectId, prospectFields):
    # now we can prepare the API request
    apiUrl = '{pardotUrl}/api/prospect/version/{legacyVersion}/do/update/id/{prospectId}?format=json' \
            .format(pardotUrl = config['Pardot']['url'], \
                    legacyVersion = config['Pardot']['legacy_api_version'], \
                    prospectId = prospectId)

    reqHeaders = {
        'Authorization': 'Bearer '+ config['Salesforce']['access_token'],
        'Pardot-Business-Unit-Id': config['Pardot']['business_unit_id']
    }
    response = requests.post(url=apiUrl, data=prospectFields, headers=reqHeaders)
    json = response.json()

    if response.status_code != 200 or json.get('@attributes').get('stat') != 'ok':
        print('Could not update prospect {}'.format(prospectId))
        print(json)
        sys.exit(4)

def prepareProspectFields(config, listings, agentName):
    prospectFields = {}
    listingCountFieldName = config['Field Naming']['api_format'] \
        .replace('{d}', '') \
        .replace('{field}', 'Count')
    prospectFields[listingCountFieldName] = len(listings)

    agentNameFieldName = config['Field Naming']['api_format'] \
        .replace('{d}', '') \
        .replace('{field}', 'AgentName')
    prospectFields[agentNameFieldName] = agentName
    
    listingNumber=1
    for listing in listings:
        priceFieldName = config['Field Naming']['api_format'] \
            .replace('{d}', str(listingNumber)) \
            .replace('{field}', 'Price')
        prospectFields[priceFieldName] = listing['price']

        bedroomsFieldName = config['Field Naming']['api_format'] \
            .replace('{d}', str(listingNumber)) \
            .replace('{field}', 'Bedrooms')
        prospectFields[bedroomsFieldName] = listing['bedrooms']

        bathroomsFieldName = config['Field Naming']['api_format'] \
            .replace('{d}', str(listingNumber)) \
            .replace('{field}', 'Bathrooms')
        prospectFields[bathroomsFieldName] = listing['bathrooms']

        sqftFieldName = config['Field Naming']['api_format'] \
            .replace('{d}', str(listingNumber)) \
            .replace('{field}', 'Sqft')
        prospectFields[sqftFieldName] = listing['sqft']

        addressFieldName = config['Field Naming']['api_format'] \
            .replace('{d}', str(listingNumber)) \
            .replace('{field}', 'Address')
        prospectFields[addressFieldName] = listing['fullAddress']

        listingUrlFieldName = config['Field Naming']['api_format'] \
            .replace('{d}', str(listingNumber)) \
            .replace('{field}', 'ListingUrl')
        prospectFields[listingUrlFieldName] = listing['listing_url']

        imageUrlFieldName = config['Field Naming']['api_format'] \
            .replace('{d}', str(listingNumber)) \
            .replace('{field}', 'ImageUrl')
        prospectFields[imageUrlFieldName] = listing['image_url']
        
        listingNumber = listingNumber + 1
    return prospectFields

def updateProspectWithListingInfo(config, prospectId, listings, agentName):
    # first we need to build our Prospect Update Request data
    prospectFields = prepareProspectFields(config, listings, agentName)
    updateProspect(config, prospectId, prospectFields)
    return prospectFields

def cleanProspectFields(prospectFields):
    for k,v in prospectFields.items():
        if k == 'id': continue # we don't want to wipe this out
        prospectFields[k]=''

def updateProspectCleaningListingFields(config, prospectId, prospectFields):
    cleanProspectFields(prospectFields)
    updateProspect(config, prospectId, prospectFields)

def updateBatch(config, batchProspects):
    reqData = {'prospects': batchProspects }
    if(int(config['Pardot']['legacy_api_version']) == 3):
        # we need to adjust the data structure of the request for API version 3
        reqData = {'prospects': {}}
        for prospect in batchProspects:  # loop thru each prospect
            pData = {prospect['id']: {}} # create MAP for the actual Prospect
            for k,v in prospect.items(): # loop thru each field
                if k == 'id': continue   # we don't want this in the values
                pData[prospect['id']][k] = v

    apiUrl = '{pardotUrl}/api/prospect/version/{legacyVersion}/do/batchUpdate?format=json' \
            .format(pardotUrl = config['Pardot']['url'], \
                    legacyVersion = config['Pardot']['legacy_api_version'])

    reqHeaders = {
        'Authorization': 'Bearer '+ config['Salesforce']['access_token'],
        'Pardot-Business-Unit-Id': config['Pardot']['business_unit_id']
    }
    prospectsString = json.dumps(reqData)
    response = requests.post(url=apiUrl, data={'prospects': prospectsString}, headers=reqHeaders)
    jsonResponse = response.json()

    if response.status_code != 200 or jsonResponse.get('@attributes').get('stat') != 'ok':
        print('Could not update batch')
        print(jsonResponse)
        sys.exit(5)