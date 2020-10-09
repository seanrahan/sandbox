#!/usr/local/bin/python3
"""
Author: Sean Hanrahan
shanrahan@vmware.com
script will enumerate and then delete all public apps an OG and below
"""

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError

# define auth (uses basic, requires aw admin creds)
awtenantcode = ''
user = ''
passwd = ''

# define environment
host = '' # e.g. cn135.awmdm.com
og = '' # Org Group ID

# define headers
headers = {
    'Accept': 'application/json;version=1, application/xml;version=1',
    'ContentType': 'application\json',
    'aw-tenant-code': awtenantcode
}

#prep URLs
appListUrl = 'https://'+ host + '/api/mam/apps/search?applicationtype=Public&locationgroupid='+ og+ '&IncludeAppsFromParentOgs=false&includeAppsFromChildOgs=true'
deleteAppUrl = 'https://'+ host + '/api/mam/apps/public/'

try:
    # enumerate apps in the OG and below
    r = requests.get(appListUrl, auth=(user, passwd), headers=headers )
    r.raise_for_status()
    
    # check for app list returned
    if (r.status_code == 204):
        print("EMPTY response - are you sure there are Public apps at this OG?")
        exit(1)

    # parse json response
    jsonResp = r.json()

    # print list of apps to delete for confirmation
    print('Found the following apps at this OG:')
    for app in jsonResp['Application']:
        print(app['ApplicationName'], ', ID: ', app['Id']['Value'])

    # confirm that we are really going to delete the apps
    print('***WARNING - About to delete ' + str(jsonResp['Total']) + ' apps. This cannot be undone.***\n')
    proceed = input('Are you sure?  Type \'YES\' to proceed, anything else to cancel: ')
    if (proceed.upper() != 'YES'):
        print('ok, exiting')
        exit(1)
    else: print('Starting deletion of '+ str(jsonResp['Total']) + ' apps.')

    #loop through response
    print('Iterating through response - applications in OG:')
    for app in jsonResp['Application']:
        # delete app from console
        print( 'PROCESSING: ', app['ApplicationName'], ', ID: ', app['Id']['Value'])
        d = requests.delete(deleteAppUrl + str(app['Id']['Value']), auth=(user,passwd), headers=headers)
        if d.status_code == 204: print("COMPLETE")
        else: print('Error deleting. Status code received: ' + str(d.status_code))

except HTTPError as http_err:
    print(f'HTTP Error: {http_err}')
except Exception as err:
    print(f'Other error: {err}')
