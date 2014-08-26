#!/usr/bin/env python
# this code hacked off https://github.com/alkivi-sas/duplicity-hubic/blob/github/hubicbackend.py

import requests
import json
import sys
import os
from swiftclient import Connection
import base64

session = requests.session()


def get_access_token(client_id, client_secret, refresh_token):
    # Fix headers
    credentials = '%s:%s' % (client_id, client_secret)
    encoded_credentials = base64.b64encode(credentials)

    session.headers.update({
        'Authorization': 'Basic %s' % encoded_credentials,
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    })

    # Call api
    url = 'https://api.hubic.com/oauth/token/'
    data = 'refresh_token=%s&grant_type=refresh_token' % refresh_token
    r = session.post(url, data=data)
    if r.status_code == 200:
        data = json.loads(r.content)
        return data['access_token']
    else:
        raise Exception('Got status_code %d in getAccessToken on url %s. Reason: %s' % (r.status_code, url, r.text))


def get_open_stack_credentials(access_token):
    for i in range(0, 10):
        # Fix authentification headers
        session.headers.update({'Authorization': 'Bearer %s' % access_token})

        # Call api
        url = 'https://api.hubic.com/1.0/account/credentials'
        r = session.get(url)
        if r.status_code == 200:
            data = json.loads(r.content)
            return data
        else:
            last_error = 'Got status_code %d in getOpenStackCredentials on url %s. Reason: %s' % \
                         (r.status_code, url, r.text)
    print last_error


def get_credentials(client_id, client_secret, refresh_token):
    access_token = get_access_token(
        client_id=client_id,
        client_secret=client_secret,
        refresh_token=refresh_token,
    )
    credentials = get_open_stack_credentials(access_token=access_token)
    conn_kwargs = {}
    if ('endpoint' in credentials) and ('token' in credentials):
        conn_kwargs['preauthurl'] = credentials['endpoint']
        conn_kwargs['preauthtoken'] = credentials['token']
    else:
        print "Asplod"

    conn_kwargs['auth_version'] = '1'

    conn = Connection(**conn_kwargs)
    return conn


if len(sys.argv) < 6:
    print "Wrong args. Use: client_id client_secret refresh_token out_path file"

conn = get_credentials(sys.argv[1], sys.argv[2], sys.argv[3])
conn.put_object(None, sys.argv[4] + os.path.basename(sys.argv[5]), open(sys.argv[5], "rb"))
