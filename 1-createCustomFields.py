#!/usr/bin/env python3
"""Sets up the Custom Fields needed to support this ParDreamin Demo.

Like all scripts in this project, this script requires that the `config/app.ini`
file has been set up already. Check out the README.md file in this project for
more information on configuration.
"""
import demoFunctions, os.path, sys

# read our configuration
config = demoFunctions.readConfig()

# login to the org
demoFunctions.authenticate(config)

# make sure we haven't previously created fields
if os.path.isfile('config/fields.csv'):
    print('This script has already generated fields in the past. Please delete them first using 5-deleteCustomFields.py, then try re-running this script')
    sys.exit(10)

# create the fields to support the Template, which aren't specific to the number of listings we want to display
demoFunctions.createCustomField(config,'Count','')
demoFunctions.createCustomField(config,'AgentName','')


# loop through number of listings we can have at most in an email
itemCount = int(config['Field Naming']['listing_count_max'])
print('need to create {lineItemCount} groups of custom fields'\
        .format(lineItemCount = itemCount))

for i in range(1,itemCount+1):
    # loop through all the fields, creating them all
    print('Creating Fields for listing {lineItemNumber}'\
            .format(lineItemNumber = i))
            
    # fields will be named with the prefix defined in app.ini (for example: PD2021_Listing_XXXXXXXX)
    demoFunctions.createCustomFields(config, ['Price','Bedrooms','Bathrooms','Sqft','Address','ListingUrl','ImageUrl'], i)

print('Done creating fields, details stored in config/fields.csv')