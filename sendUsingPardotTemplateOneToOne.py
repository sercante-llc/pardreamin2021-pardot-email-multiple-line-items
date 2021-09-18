#!/usr/bin/env python3
import functions, requests, sys
from dataServices import ClientService, ListingService

# read our configuration
config = functions.readConfig()
clientService = ClientService(config)
listingService = ListingService(config)

# login to the org
functions.authenticate(config)

# get a list of people that need emails!
clients = clientService.getClientsNeedingWeeklyEmail()
for client in clients:
    # get the listings we want to share with the client
    listings = listingService.getListingsForEmail(client['identifier'])
    print('for %s %s, we will show them %d listings' % (client['firstName'], client['lastName'], len(listings)))

    # lets update the prospect to have the right listing info!
    functions.updateProspectWithListingInfo(config, client['identifier'], listings, client['agent'])

    # now that the prospect has been updated, lets send the email
    oneToOneSendType='prospect_id'
    if '@' in client['identifier']: oneToOneSendType = 'prospect_email'
    apiUrl = '%s/api/email/version/%d/do/send/%s/%s?format=json' % (config['Pardot']['url'], int(config['Pardot']['legacy_api_version']), oneToOneSendType, client['identifier'])
    print(apiUrl)
    reqData = {
        # required fields for a one-to-one, providing complete HTML Content and Sender Details (not specifying Pardot User Id)
        'campaign_id': config['Pardot']['campaign_id'],
        'email_template_id': config['Pardot']['email_template_id'],
        oneToOneSendType: client['identifier']
    }
    reqHeaders = {
        'Authorization': 'Bearer '+ config['Salesforce']['access_token'],
        'Pardot-Business-Unit-Id': config['Pardot']['business_unit_id']
    }

    r = requests.post(url=apiUrl, data=reqData, headers=reqHeaders)
    json = r.json()

    if r.status_code == 200 and json.get('@attributes').get('stat') == 'ok':
        print('Successfully sent email to %s' % client['identifier'])
    else:
        print('Could not send email to %s' % client['identifier'])
        print(json)
        sys.exit(6)

    functions.updateProspectCleaningListingFields(config, client['identifier'], len(listings))

print('Script executed successfully')