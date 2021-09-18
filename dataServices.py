import csv, os, random

class ListingService:
    def __init__(self, config):
        self._maxListings = int(config['Field Naming']['listing_count_max'])
        self._minListings = int(config['Field Naming']['listing_count_min'])
        self._listings = self._readListings()

    def _readListings(self):
        listings = []
        
        with open('data/listings.csv','r') as csvFile:
            csvReader = csv.DictReader(csvFile)
            for row in csvReader:
                listings.append(row)
        return listings

    def getListingsForEmail(self, emailAddress):
        numberOfListings = random.randint(self._minListings, self._maxListings)
        listings = []
        for i in range(0,numberOfListings):
            randomListingIndex = random.randint(0, len(self._listings)-1)
            listings.append(self._listings[randomListingIndex])
        return listings

class ClientService:
    def __init__(self, config):
        self._clients = self._readClients()

    def _readClients(self):
        clients = []
        
        with open('data/clients.csv','r') as csvFile:
            csvReader = csv.DictReader(csvFile)
            for row in csvReader:
                clients.append(row)

        return clients
    
    def getClientsNeedingWeeklyEmail(self):
        return self._clients