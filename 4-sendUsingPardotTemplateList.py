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
maxBatchSize =2
batchSize = 0
batchProspects = []
batches = []

for recipient in recipients:
    # get the listings we want to share with this recipient
    listings = listingService.getListingsForRecipientId(recipient['id'])
    print('for {firstName} {lastName}, we will show them {itemCount} listings' \
            .format(firstName = recipient['firstName'], \
                    lastName = recipient['lastName'], \
                    itemCount = len(listings)))

    prospectFields = demoFunctions.prepareProspectFields(config, listings, recipient['agent'])
    prospectFields['id'] = recipient['prospectId']
    batchProspects.append(prospectFields)
    batchSize = batchSize + 1
    if batchSize == maxBatchSize:
        # we need to update the batch in Pardot
        print('updating batch of {batchSize} Prospects'.format(batchSize = maxBatchSize))
        demoFunctions.updateBatch(config, batchProspects)
        batches.append(batchProspects)
        batchProspects = []
        batchSize = 0

# once we've processed all recipients, we may have an incomplete batch
if batchSize > 0:
    print('updating final batch of {batchSize} Prospects'.format(batchSize = batchSize))
    # we need to update the batch in Pardot
    demoFunctions.updateBatch(config, batchProspects)
    batches.append(batchProspects)
    batchProspects = []
    batchSize=0

print('done updating prospects, sending email now')


# a single API call to send the email to the List
apiUrl = '{pardotUrl}/api/email/version/{legacyVersion}/do/send/?format=json' \
        .format(pardotUrl = config['Pardot']['url'], \
                legacyVersion = config['Pardot']['legacy_api_version'])
print(apiUrl)
reqData = {
    # required fields for a one-to-one, providing complete HTML Content and Sender Details 
    # (not specifying Pardot User Id)
    'campaign_id': config['Pardot']['campaign_id'],
    'email_template_id': config['Pardot']['email_template_id'],
    'list_ids[]': config['Pardot']['sending_list_id']
}
reqHeaders = {
    'Authorization': 'Bearer '+ config['Salesforce']['access_token'],
    'Pardot-Business-Unit-Id': config['Pardot']['business_unit_id']
}
print(reqData)
response = requests.post(url=apiUrl, data=reqData, headers=reqHeaders)
json = response.json()

if response.status_code == 200 and json.get('@attributes').get('stat') == 'ok':
    print('Successfully sent email to list {pardotListId}'.format(\
        pardotListId = config['Pardot']['sending_list_id'] ))
else:
    print('Could not send email to list {pardotListId}'.format(\
        pardotListId = config['Pardot']['sending_list_id'] ))
    print(json)
    sys.exit(30)

print('email sent, cleaning prospect custom fields')
# now lets clean the prospect data up
print('batch count: {batchCount}'.format(batchCount=len(batches)))
for batch in batches:
    print('batch has {prospectCount} prospects'.format(prospectCount = len(batch)))
    for prospect in batch:
        # a really good idea is to now clean the Prospect Fields so that they aren't left with dirty data
        # which could mess up a send later on
        for k,v in prospect.items():
            if k == 'id': continue # we don't want to wipe this value out
            prospect[k]=''
    demoFunctions.updateBatch(config, batch)

print('Script executed successfully')