import requests
import json
import os
import sys
import urllib2

# To run:
# python eventbrite-to-intranet.py [eventbrite-csv] [Event ID]
# Where eventbrite-csv is an exported CSV of attendees from Eventbrite with only 'First Name', 'Last Name', and 'Email' exported.

if len(sys.argv) != 3:
    print("Please include a path to the CSV and the event ID to replace.")
    sys.exit(0)

csv = open(sys.argv[1], 'r')
resource_id = sys.argv[2]
oauth = 'burC2Orn0Ed4byD1Cem'

BASE_URL = 'https://api.tnyu.org/v3'
TEST_BASE_URL = 'https://api.tnyu.org/v3-test'

headers = {
	'content-type': 'application/vnd.api+json',
	'accept': 'application/*, text/*',
	'authorization': 'Bearer ' + oauth
}

# Reading data from the API
r = requests.get(BASE_URL + '/people', headers=headers, verify=False)
data = r.json()
list_of_people = data['data']

attendees = []
rows = csv.readlines()
for row in rows:
	info = row.split(',')
	orderNumber = info[0]
	name = info[1] + ' ' + info[2]
	email = info[3]
	person_exists = False

	for person in list(list_of_people):
		if 'attributes' in person:
			if 'contact' in person['attributes']:
				if 'email' in person['attributes']['contact']:
					if person['attributes']['contact']['email'] == email:
						attendees.append(person['id'])
						person_exists = True

	if not person_exists:
		people = {}
		people['data'] = {}
		people['data']['attributes'] = {}
		people['data']['attributes']['name'] = name
		people['data']['attributes']['contact'] = {}
		people['data']['attributes']['contact']['email'] = email
		people['data']['type'] = 'people'
		
		people = json.dumps(people)
		r = requests.post(BASE_URL + '/people', data=people, headers=headers, verify=False)
		data = r.json()
		attendees.append(data['data']['id'])

resource_type = 'events'

# Make your small change
event = {}
event['id'] = resource_id
event['type'] = resource_type
event['attributes'] = {}
event['relationships'] = {}
event['relationships']['attendees'] = {}
event['relationships']['attendees']['data'] = []

for attendee in attendees:
	event['relationships']['attendees']['data'].append({ "type": "people", "id": attendee })

document = {}
document['data'] = event

document = json.dumps(document)

# Send a PUT request with the new data to the API
r = requests.patch(BASE_URL + '/events/' + resource_id, data=document, headers=headers, verify=False)