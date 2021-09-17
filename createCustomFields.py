#!/usr/bin/env python3
import functions, os.path, sys

# read our configuration
config = functions.readConfig()

# login to the org
functions.authenticate(config)

# make sure we haven't previously created fields
if os.path.isfile('config/fields.csv'):
    print('This script has already generated fields in the past. Please delete them first using deleteCustomFields.py, then try re-running this script')
    sys.exit(4)

# loop through number of listings we can have at most in an email
rowCount = int(config['Field Naming']['listing_count_max'])
print('need to create %d rows' % rowCount)
for i in range(1,rowCount+1):
    # loop through all the fields, creating them all
    print('Creating Fields for listing %d' % i)
    functions.createCustomFields(config, ['Price','Bedrooms','Bathrooms','Sqft','Address','ListingUrl','ImageUrl'], i)

print('Done creating fields, details stored in config/fields.csv')