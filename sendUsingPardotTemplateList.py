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
maxBatchSize =2
batchSize = 0
batchProspects = []
batches = []

for client in clients:
    # get the listings we want to share with the client
    listings = listingService.getListingsForEmail(client['id'])
    print('for %s %s, we will show them %d listings' % (client['firstName'], client['lastName'], len(listings)))
    prospectFields = functions.prepareProspectFields(config, listings, client['agent'])
    prospectFields['id'] = client['id']
    batchProspects.append(prospectFields)
    batchSize = batchSize + 1
    if batchSize == maxBatchSize:
        # we need to update the batch in Pardot
        print('updating batch of %d Prospects' % maxBatchSize)
        functions.updateBatch(config, batchProspects)
        batches.append(batchProspects)
        batchProspects = []
        batchSize = 0

# once we've processed all clients, we may have an incomplete batch
if batchSize > 0:
    print('updating final batch of %d Prospects' % batchSize)
    # we need to update the batch in Pardot
    functions.updateBatch(config, batchProspects)
    batches.append(batchProspects)
    batchProspects = []
    batchSize=0

print('done updating prospects, sending email now')


# a single API call to send the email to the List
apiUrl = '%s/api/email/version/%d/do/send/?format=json' % (config['Pardot']['url'], int(config['Pardot']['legacy_api_version']))
print(apiUrl)
reqData = {
    # required fields for a one-to-one, providing complete HTML Content and Sender Details (not specifying Pardot User Id)
    'campaign_id': config['Pardot']['campaign_id'],
    'email_template_id': config['Pardot']['email_template_id'],
    'list_ids[]': config['Pardot']['sending_list_id']
}
reqHeaders = {
    'Authorization': 'Bearer '+ config['Salesforce']['access_token'],
    'Pardot-Business-Unit-Id': config['Pardot']['business_unit_id']
}
print(reqData)
r = requests.post(url=apiUrl, data=reqData, headers=reqHeaders)
json = r.json()

if r.status_code == 200 and json.get('@attributes').get('stat') == 'ok':
    print('Successfully sent email to list %s' % config['Pardot']['sending_list_id'] )
else:
    print('Could not send email to list %s' % config['Pardot']['sending_list_id'] )
    print(json)
    sys.exit(30)

print('email sent, cleaning prospect custom fields')
# now lets clean the prospect data up
print('batch count: %d' % len(batches))
for batch in batches:
    print('batch has %d prospects' % len(batch))
    # get the listings we want to share with the client
    for prospect in batch:
        print(prospect)
        functions.cleanProspectFields(prospect)
    functions.updateBatch(config, batch)

print('Script executed successfully')