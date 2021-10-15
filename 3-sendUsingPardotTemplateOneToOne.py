#!/usr/bin/env python3
import demoFunctions, requests, sys
from dataServices import RecipientService, ListingService

# read our configuration
config = demoFunctions.readConfig()
recipientService = RecipientService(config)
listingService = ListingService(config)

# login to the org
demoFunctions.authenticate(config)

# get a list of people that need emails!
recipients = recipientService.getRecipientsNeedingWeeklyEmail()
for recipient in recipients:
    # get the listings we want to share with the recipient
    listings = listingService.getListingsForRecipientId(recipient['id'])
    print('for {firstName} {lastName}, we will show them {itemCount} listings' \
            .format(firstName = recipient['firstName'], \
                    lastName = recipient['lastName'], \
                    itemCount = len(listings)))

    # lets update the prospect to have the right listing info!
    # first we need to build our Prospect Update Request data
    prospectFields = {}
    fieldNameFormat = config['Field Naming']['api_format']
    # these 2 fields are not line-item dependant, so we keep them out of a loop
    listingCountFieldName = fieldNameFormat.format(field='Count', lineItemNumber='')
    prospectFields[listingCountFieldName] = len(listings)

    agentNameFieldName = fieldNameFormat.format(field='AgentName', lineItemNumber='')
    prospectFields[agentNameFieldName] = recipient['agent']
    
    # now we loop through the listings
    listingNumber=1
    for listing in listings:
        # here we "build" the field name, taking into consideration the 
        # - "line item field" 
        # - "listing number", or the LineItemNumber
        priceFieldName = fieldNameFormat.format(field='Price', lineItemNumber=listingNumber)
        prospectFields[priceFieldName] = listing['price']
        # repeat for each field
        bedroomsFieldName = fieldNameFormat.format(field='Bedrooms', lineItemNumber=listingNumber)
        prospectFields[bedroomsFieldName] = listing['bedrooms']

        bathroomsFieldName = fieldNameFormat.format(field='Bathrooms', lineItemNumber=listingNumber)
        prospectFields[bathroomsFieldName] = listing['bathrooms']

        sqftFieldName = fieldNameFormat.format(field='Sqft', lineItemNumber=listingNumber)
        prospectFields[sqftFieldName] = listing['sqft']

        addressFieldName = fieldNameFormat.format(field='Address', lineItemNumber=listingNumber)
        prospectFields[addressFieldName] = listing['fullAddress']

        listingUrlFieldName = fieldNameFormat.format(field='ListingUrl', lineItemNumber=listingNumber)
        prospectFields[listingUrlFieldName] = listing['listing_url']

        imageUrlFieldName = fieldNameFormat.format(field='ImageUrl', lineItemNumber=listingNumber)
        prospectFields[imageUrlFieldName] = listing['image_url']
        
        listingNumber = listingNumber + 1

    # once we have all our Pardot Field updates ready, let's tell the API to make the Prospect Update
    demoFunctions.updateProspect(config, recipient['prospectId'], prospectFields)

    # now that the prospect has been updated, lets send the email
    apiUrl = '{pardotUrl}/api/email/version/{legacyVersion}/do/send/prospect_id/{prospectId}?format=json' \
            .format(pardotUrl = config['Pardot']['url'], \
                    legacyVersion = config['Pardot']['legacy_api_version'], \
                    prospectId = recipient['prospectId'])
    print(apiUrl)
    reqData = {
        # required fields for a one-to-one, providing Pardot Template Id with a Campaign Id
        'campaign_id': config['Pardot']['campaign_id'],
        'email_template_id': config['Pardot']['email_template_id']
    }
    reqHeaders = {
        'Authorization': 'Bearer '+ config['Salesforce']['access_token'],
        'Pardot-Business-Unit-Id': config['Pardot']['business_unit_id']
    }

    response= requests.post(url=apiUrl, data=reqData, headers=reqHeaders)
    json = response.json()

    if response.status_code == 200 and json.get('@attributes').get('stat') == 'ok':
        print('Successfully sent email to {prospectId}'.format(prospectId = recipient['prospectId']))
    else:
        print('Could not send email to {prospectId}'.format(prospectId = recipient['prospectId']))
        print(json)
        sys.exit(40)

    # a really good idea is to now clean the Prospect Fields so that they aren't left with dirty data
    # which could mess up a send later on
    for k,v in prospectFields.items():
        if k == 'id': continue # we don't want to wipe this value out
        prospectFields[k]=''
    demoFunctions.updateProspect(config, recipient['prospectId'], prospectFields)

print('Script executed successfully')