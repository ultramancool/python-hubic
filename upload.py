#!/usr/bin/env python
# originally (c) 2013 Antoine Sirinelli <antoine@monte-stello.com>
# hacked up a bunch after that though. 

import requests
import json
from base64 import b64decode
import sys
import os
from swiftclient import Connection


class auth_hubic:
    def __init__(self, user, passwd):
        self.SessionHandler = 'https://ws.ovh.com/sessionHandler/r4/'
        self.hubicws = 'https://ws.ovh.com/hubic/r5/'

        r = requests.get(self.SessionHandler + 'rest.dispatcher/' + 'getAnonymousSession')
        sessionId = r.json()['answer']['session']['id']

        params = { 'sessionId': sessionId,
                   'email': user}
        payload = {'params': json.dumps(params)}

        r = requests.get(self.hubicws + 'rest.dispatcher/' + 'getHubics',
                         params=payload)
        hubics = r.json()
        self.hubicsId = hubics['answer'][0]['id']

        params = { 'login': hubics['answer'][0]['nic'],
                   'password': passwd,
                   'context': 'hubic'}
        payload = {'params': json.dumps(params)}

        r = requests.get(self.SessionHandler + 'rest.dispatcher/' + 'login',
                         params=payload)

        self.sessionId = r.json()['answer']['session']['id']

    def get_credentials(self):
        params = { 'sessionId': self.sessionId,
                   'hubicId': self.hubicsId}
        payload = {'params': json.dumps(params)}

        r = requests.get(self.hubicws + 'rest.dispatcher/' + 'getHubic',
                         params=payload)
        Storage_Url = b64decode(r.json()['answer']['credentials']['username'])
        Auth_Token = r.json()['answer']['credentials']['secret']
        return Storage_Url, Auth_Token

    def logout(self):
        params = { 'sessionId': self.sessionId}
        payload = {'params': json.dumps(params)}
        r = requests.get(self.SessionHandler + 'rest.dispatcher/' + 'logout',
                         params=payload)

if (len(sys.argv) < 4):
	print "usage: script user password file"
	sys.exit(1)

user = sys.argv[1]
passwd = sys.argv[2]
hubic = auth_hubic(user, passwd)
storage_url, auth_token = hubic.get_credentials()

options = {'auth_token': auth_token,
           'object_storage_url': storage_url}
conn = Connection(os_options=options, auth_version=2)

conn.put_object("default/", os.path.basename(sys.argv[3]), open(sys.argv[3],'rb'))

hubic.logout()
