#!/usr/bin/env python3
import demoFunctions, csv, os

# read our configuration
config = demoFunctions.readConfig()

# login to the org
demoFunctions.authenticate(config)

# get a list of the fields to remove
with open('config/fields.csv','r') as csvFile:
    csvReader = csv.reader(csvFile)
    for row in csvReader:
        fieldApiName = row[0]
        fieldId = int(row[1])
        print('removing Custom field {fieldApiName} with id {fieldId}' \
                .format(fieldApiName = fieldApiName, fieldId = fieldId))

        demoFunctions.deleteCustomField(config, fieldApiName, fieldId)

os.remove('config/fields.csv')
print('Done removing fields, file config/fields.csv removed')