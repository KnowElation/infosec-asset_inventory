'''
1. Pull lists into data directory
2. Extract fields into DataFrames
    who.json FK (first.last), email (first.last@host), hipchat, loc
    CDW18-19.csv PK Serial (chop front S), Asset Tag ID, Ship to State
    JIRA.csv  Issue Key (Ticket ID), PK Summary (Serial), FK Assignee, Status
3. Put extracted fields into SQLite DB with index of {assignee,id} and foreign key of {asset tag, serial}
4. Compare human (assignee) to asset (asset tag)
5. Find people without asset
6. Produce CSV / XLS output
7. Produce console output

"a sample of humans (5%, say, of the current employees from ADP) and to make sure they have machines
in inventory (~ they are assigned an INV ticket). A script that can do that to hand off to IA is great."

requirements.txt
pandas
'''
import pandas as pd
import numpy as np
import json
import csv
import sqlite3
import requests
import json
import random


def run_assets(percent=100, output='stdout'):
    # Make sure percent is legal
    if percent > 100 or percent < 1:
        return False
    try:
        # Get users from RallyWho
        url = 'https://who.werally.in/rest/who/v1/people'
        users = requests.get(url).json()
        # print(json.dumps(users[:2], indent=2))
        # Get JIRA inventory from file
        jira_json = json_from_file('data/jira.csv')
        # print(json.dumps(jira_json[:2], indent=2))
        # Get CDW records from file
        cdw_json = json_from_file('data/cdw.csv')
        # print(json.dumps(cdw_json[:2], indent=2))
    except:
        # REST failure, file read failure
        return False

    # Get a random sample of some percent of users
    final_dict = \
        [
            {
                'username': cur['id'],
                'name': cur['name'],
                'user_location': cur['loc']
                # more as needed
            } for cur in random.sample(
                users, len(users) * percent // 100
            )
        ]

    true_count = 0
    has_machine = 0
    for cur in final_dict:
        user = cur['username']
        jira_cur = search_for_item(jira_json, 'Assignee', user)
        if len(jira_cur) > 0:
            cur.update(
                {
                    'serial': jira_cur[0]['Summary'],  # ,
                    'machines_owned': len(jira_cur)
                    # 'machine_location': jira_cur['Custom field (Location)']
                    # Any others you find relevant
                }
            )
            has_machine += len(jira_cur)
            serial = cur['serial']
            cdw_cur = search_for_item(cdw_json, 'Serial', 'S' + serial)
            if len(cdw_cur) > 0:
                cur.update(
                    {
                        'ship_to_state': cdw_cur[0]['Ship to State'],
                        'complete_data': True
                        # Any other fields
                    }
                )
                true_count += 1
            else:
                cur['complete_data'] = False
        else:
            cur['machines_owned'] = 0
            cur['complete_data'] = False

    if output == "stdout":
        print(json.dumps(final_dict, indent=2))
    else:
        columns = ['username', 'name', 'user_location', 'serial',
                   'machines_owned', 'ship_to_state', 'complete_data']
        with open(output, 'w') as out_file:
            csv_w = csv.writer(out_file)
            csv_w.writerow(columns)

            for i_r in final_dict:
                csv_w.writerow(map(lambda x: i_r.get(x, ""), columns))

    print(str(100 * has_machine // len(final_dict)) + " % have machines")
    print(str(100 * true_count // len(final_dict)) + " % match inventory")


def search_for_item(dataset, key, value):
    # This could be made into binary if we care about efficiency
    ret = []
    for item in dataset:
        if item[key] == value:
            ret.append(item)
    return ret


def json_from_file(filename, sorted_by=None):
    csv_reader = csv.DictReader(open(filename))
    ret_list = []
    for line in csv_reader:
        ret_list.append(line)
    if sorted_by and sorted_by in ret_list[0]:
        ret_list = sorted(ret_list, key=lambda i: i[sorted_by])
    return ret_list


def data_parsing():
    # Get People Records
    url = 'https://who.werally.in/rest/who/v1/people'
    people_import_df = pd.read_json(url, orient='columns', encoding=ascii)
    people_cols = ['id', 'name', 'loc']
    people_df = people_import_df[people_cols]
    #people_import_df = pd.DataFrame(columns=people_cols)
    print(people_df.head(10))

    # Get Inventory Records
    inv_cols = ['Summary','Assignee','Custom field (Location)']
    inv_df = pd.read_csv('data/JIRA.csv', usecols=inv_cols)
    print(inv_df.head)

    # Get Supplier Records
    cdw_cols = ['Ship to State','Asset Tag ID','Serial Number']
    cdw_df = pd.read_csv('data/CDW18-19.csv', usecols=cdw_cols)
    #for cdw_df['Serial Number'] in cdw_df:
    #    cdw_df['Serial Number'] = cdw_df['Serial Number'].apply(lambda x : x[1:] if x.startswith("S") else x)
    #cdw_df['Serial Number'] = cdw_df['Serial Number'].str.replace("S","")
    sn = 'Serial Number'
    for sn in cdw_df:
        cdw_df[sn] = cdw_df[sn].apply(lambda x : x[1:] if x.startswith("S") else x)
    print(cdw_df.head)

if __name__ == '__main__':
    # run_assets(percent=1)
    run_assets(percent=5, output='data/inventory_output.csv')