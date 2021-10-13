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
    prospectFields = demoFunctions.updateProspectWithListingInfo(config, recipient['prospectId'], listings, recipient['agent'])

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

    demoFunctions.updateProspectCleaningListingFields(config, recipient['prospectId'], prospectFields)

print('Script executed successfully')