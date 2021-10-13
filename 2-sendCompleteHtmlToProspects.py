#!/usr/bin/env python3
import demoFunctions, requests, sys
from dataServices import RecipientService, ListingService
from mako.template import Template

# read our configuration
config = demoFunctions.readConfig()
recipientService = RecipientService(config)
listingService = ListingService(config)

# login to the org
demoFunctions.authenticate(config)

# get our email template
mailTemplate = Template(filename='templates/completeHtmlTemplate.html')

# get a list of people that need emails!
recipients = recipientService.getRecipientsNeedingWeeklyEmail()
for recipient in recipients:
    # get the listings we want to share with the recipient
    listings = listingService.getListingsForRecipientId(recipient['id'])
    print('for {firstName} {lastName}, we will show them {itemCount} listings' \
            .format(firstName = recipient['firstName'], \
                    lastName = recipient['lastName'], \
                    itemCount = len(listings)))
                    
    emailHtml = mailTemplate.render(listings=listings, recipient=recipient)

    # now that we've assembled our own HTML, we can send this directly to Pardot    
    apiUrl = '{pardotUrl}/api/email/version/{legacyVersion}/do/send/prospect_id/{prospectId}?format=json' \
            .format(pardotUrl = config['Pardot']['url'], \
                    legacyVersion = config['Pardot']['legacy_api_version'], \
                    prospectId = recipient['prospectId'])

    print(apiUrl)
    reqData = {
        # required fields for a one-to-one, providing complete HTML Content and Sender Details (not specifying Pardot User Id)
        'campaign_id': config['Pardot']['campaign_id'],
        'text_content': 'This is a demo, so we are skipping the text version. In the real world, you would need to do this as well. {{EmailPreferenceCenter}}',
        'name': 'ParDreamin Realty Weekly Email',
        'subject': 'Here are {itemCount} Listings Waiting for You!'.format(itemCount = len(listings)),
        'from_email': 'realty@pardreamin.com',
        'from_name': 'ParDreamin Realty',
        'html_content' : emailHtml
    }
    reqHeaders = {
        'Authorization': 'Bearer '+ config['Salesforce']['access_token'],
        'Pardot-Business-Unit-Id': config['Pardot']['business_unit_id']
    }

    response = requests.post(url=apiUrl, data=reqData, headers=reqHeaders)
    json = response.json()

    if response.status_code == 200 and json.get('@attributes').get('stat') == 'ok':
        print('Successfully sent email to {prospectId}'.format(prospectId = recipient['prospectId']))
    else:
        print('Could not send email to {prospectId}'.format(prospectId = recipient['prospectId']))
        print(json)
        sys.exit(20)

print('Script executed successfully')