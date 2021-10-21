# ParDreamin 2021: Pardot Email with Multiple Line Items
This code project is written to accompany a Session at the ParDreamin 2021 
conference:
## How to send a Pardot Email with Multiple Line Items
It is impossible to send a Pardot email that has a list of related records... 
or is it?

In this session, we will uncover strategies to send a Pardot email with multiple 
line items. We’ll walk through a hypothetical use case at a realty company by 
going step-by-step through an email build. The email will send prospects many 
personalized property listings that may interest them.

# getting this to work
I've tried to make this as easy to set up and run in any Pardot environment. 
With that said, there are a few things that need to be set up.

## Prepare Python Environment
1. Make sure you have a python3 development environment working already
2. Add these 2 python packages (`Mako` and `requests`) into your environment
```
pip install Mako requests
```

## Prepare Script Configuration
1. Get Salesforce configured to allow API requests for a Pardot User. Follow 
   the steps here: https://thespotforpardot.com/2020/09/23/pardot-api-and-getting-ready-with-salesforce-sso-users/
2. Make a copy of `config/app.ini.sample` and name it `config/app.ini`.
3. Edit the file to provide user & Connected App information you set up in step 3
4. In `config/app.ini`, provide the Pardot Business Unit ID. If your account 
   does not have the feature **Allow Multiple Prospects with Same Email Address**, 
   then change the Legacy API Version from 4 to 3.
5. Working in a Pardot Sandbox? Change the Salesforce Login URL to 
   `https://test.salesforce.com` and change the Pardot API Url to 
   `https://pi.demo.pardot.com`
6. In Pardot, create a new Email Template. Use the HTML from 
   `templates/pardotEmailTemplate.html` and fill in the rest of the fields. 
   Be sure to grab the Pardot Email Template ID (you have to dig it out of 
   the URL sadly).
7. Create a Pardot Static List. You will add Prospects to it later, but for now 
   grab the Pardot List ID (again, digging it out of the URL)
8. Create or find a Pardot Test Campaign. You will need the ID of this campaign 
   for associating the Email Sends these scripts will perform.

## Prepare Recipient File
This script comes with sample recipients, however the Pardot Prospect ID needs 
to be included. The Prospect IDs I've used will not match prospects in your org 
(or maybe worse, they will match real people and they will wonder what these 
emails are!).

Create 3 or more Prospects in Pardot, add them to the Static List you created 
earlier and then update the `data/recipients.csv` file with the right details. 
In the real world, you wouldn't be driving this type of functionality from a 
hard coded CSV file, but this is a demo so we can cheat.

# Running Scripts!
Ok, now that the prep work is all done, we should be good to go!

The scripts of interest have number 1-5 in the file name:

- **1-createCustomFields.py** - Creates Custom Fields via API, and when done 
    writes the field API name and the Pardot Field ID to the 
    `config/fields.csv` file. You could create these manually, but since there 
    are 46 custom fields, it might just be easier to use this script!
- **2-sendCompleteHtmlToProspects.py** - Uses HTML in an External Template 
    (`templates/completeHtmlTemplate.html`), prepares the entire HTML code, 
    then asks Pardot to send the HTML to the right Prospect.
- **3-sendUsingPardotTemplateOneToOne.py** - Updates Prospect records with 
    Property listing information, then does a One-to-One email send via Pardot 
    API, then another update to clear the record values out.
- **4-sendUsingPardotTemplateList.py** - Updates Prospect records with Property 
    listing information in batches, then does a List email send via Pardot API, 
    finally another set of batch updates to clear the record values out.
- **5-deleteCustomFields.py** - Once you are done playing, you can run this 
    script to have the custom fields removed.

Other supporting files, and what they are for
- **dataServices.py** - Provides mocked services for getting recipient lists and 
    line items (Listings) to be included in the email
- **demoFunctions.py** - Some supporting code necessary to make the demo function, 
    but not important enough to highlignt in the session.