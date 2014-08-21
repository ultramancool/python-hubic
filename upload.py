from swiftclient import Connection
import os
import sys

if len(sys.argv) < 4:
	print "usage: script storage_url auth_token file_to_upload"
	sys.exit(1)

options = {'auth_token': sys.argv[2],
           'object_storage_url': sys.argv[1]}
conn = Connection(os_options=options, auth_version=2)

conn.put_object("default/", os.path.basename(sys.argv[3]), open(sys.argv[3],'rb'))

