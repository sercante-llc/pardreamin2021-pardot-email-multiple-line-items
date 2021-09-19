#!/usr/bin/env python3
import functions, requests, sys
from dataServices import ClientService, ListingService
from mako.template import Template

# read our configuration
config = functions.readConfig()
clientService = ClientService(config)
listingService = ListingService(config)

# login to the org
functions.authenticate(config)

# get our email template
mailTemplate = Template(filename='templates/completeHtmlTemplate.html')

# get a list of people that need emails!
clients = clientService.getClientsNeedingWeeklyEmail()
for client in clients:
    # get the listings we want to share with the client
    listings = listingService.getListingsForEmail(client['id'])
    print('for %s %s, we will show them %d listings' % (client['firstName'], client['lastName'], len(listings)))
    emailHtml = mailTemplate.render(listings=listings, client=client)

    # now that we've assembled our own HTML, we can send this directly to Pardot    
    apiUrl = '%s/api/email/version/%d/do/send/prospect_id/%s?format=json' % (config['Pardot']['url'], int(config['Pardot']['legacy_api_version']), client['id'])
    print(apiUrl)
    reqData = {
        # required fields for a one-to-one, providing complete HTML Content and Sender Details (not specifying Pardot User Id)
        'campaign_id': config['Pardot']['campaign_id'],
        'text_content': 'If you used a real Email Browser, you would see listings. Please join the modern world',
        'name': 'ParDreamin Realty Weekly Email',
        'subject': 'Here are %d Listings Waiting for You!' % len(listings),
        'from_email': 'realty@pardreamin.com',
        'from_name': 'ParDreamin Realty',
        'html_content' : emailHtml
    }
    reqHeaders = {
        'Authorization': 'Bearer '+ config['Salesforce']['access_token'],
        'Pardot-Business-Unit-Id': config['Pardot']['business_unit_id']
    }

    r = requests.post(url=apiUrl, data=reqData, headers=reqHeaders)
    json = r.json()

    if r.status_code == 200 and json.get('@attributes').get('stat') == 'ok':
        print('Successfully sent email to %s' % client['id'])
    else:
        print('Could not send email to %s' % client['id'])
        print(json)
        sys.exit(5)

print('Script executed successfully')