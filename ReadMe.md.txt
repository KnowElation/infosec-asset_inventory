# ReadMe.md

## Introduction to asset_inventory.py

Required: data/cdw.csv, data/jira.csv, "Rally Who?" connection

Download files from their respective sources: 

cdw.csv from Walt Fitzgerald <WALTFIT@cdw.com>, Executive Account Manager, CDW. Request full asset list for the period being checked. 
Open cdw.csv in an editor and change "Serial Number" to "Serial", save. 

jira.csv from search for:
project = INV AND Type = "Computer Asset" AND status = "Issued to User" and description is not EMPTY ORDER BY createdDate ASC

Click Export -> CSV (Current Fields)

Open Terminal or iTerm and:
    cd to Asset_Inventory/venv
    sh bin/activate
    python3 asset_inventory.py

Output will look similar to this:

$ python3 asset_inventory.py
86 % have machines
32 % matches

Additionally, in the data directory the file asset_inventory.py will have the results.

## Troubleshooting 

1. Check the files are in data/ and have the correct names: jira.csv, cdw.csv
2. Make sure you're using python3
3. Are you on the VPN or otherwise able to connect to "Rally Who?" 

## Future features

1. Use JIRA API
2. Scrape CDW website for all records
3. Check AD for user terminated status 
4. Put in a database and mark off those checked

## Credits

James "@SortOfIntern" Coombs <james.coombs@rallyhealth.com> 
Matthew J. Harmon <matthew.harmon@rallyhealth.com>
