"""Provides fake data services to represent the Recipient and their listings

In a real world integration, you would be retrieving Recipients and LineItems
(Listings in our example) from a real data source. There are a lot of ways
that this could be done, such as a "Real Estate Customer" database
(perhaps mySql?) and a Listings Recommendation Engine.

This demo/sample implementation simply loads data from sample CSVs,
encapsulating the demo into a nice little package.
"""
import csv, os, random

class ListingService:
    def __init__(self, config):
        self._maxListings = int(config['Field Naming']['listing_count_max'])
        self._minListings = int(config['Field Naming']['listing_count_min'])
        self._listings = self._readListings()

    def _readListings(self):
        """Reads the Listings from the CSV file.

        Returns:
            an array of listings, with each listing in a dict format
        """
        listings = []
        
        with open('data/listings.csv','r') as csvFile:
            csvReader = csv.DictReader(csvFile)
            for row in csvReader:
                listings.append(row)
        return listings

    def getListingsForRecipientId(self, recipientId):
        """Provides a random set of Listings, ignoring the Recipient entirely.

        The number of listings provided will vary between the listing_count_min
        and the listing_count_max (defined in config/app.ini)

        Returns:
            an array of listings, randomly selected.
        """
        numberOfListings = random.randint(self._minListings, self._maxListings)
        listings = []
        for i in range(0,numberOfListings):
            randomListingIndex = random.randint(0, len(self._listings)-1)
            listings.append(self._listings[randomListingIndex])
        return listings

class RecipientService:
    def __init__(self, config):
        self._recipients = self._readRecipients()

    def _readRecipients(self):
        """Reads the Recipients from the CSV file.

        Returns:
            an array of Recipients, with each recipient in a dict format
        """
        recipients = []
        
        with open('data/recipients.csv','r') as csvFile:
            csvReader = csv.DictReader(csvFile)
            for row in csvReader:
                recipients.append(row)

        return recipients
    
    def getRecipientsNeedingWeeklyEmail(self):
        """Simply provides all recipients in the CSV, each time it is called.

        Returns:
            an array of Recipients, with each recipient in a dict format
        """
        return self._recipients