#####
# libpetalbear.py - Load ravelry one-use codes into Mailchimp merge fields
#####

import configparser
import requests
import json
import csv
requests.packages.urllib3.disable_warnings()

class petalbear:

	# Take the passed in configuration file and get ready to Mailchimp
	def __init__(self,conffilename):
		self.conffilename = conffilename
		self.config = configparser.ConfigParser()
		try:
			self.config.read(self.conffilename)
		except:
			raise
		apikey_parts = self.config['mailchimp']['apikey'].split('-')
		self.apikey = self.config['mailchimp']['apikey']
		self.url = "https://" + apikey_parts[1] + ".api.mailchimp.com/3.0"
		self.list_id = self.get_list_id_by_name(self.config['mailchimp']['list_name'])

	# Generic API method to be used by all other methods when reaching out to mailchimp.
	# No pagination loops should happen inside of here. One and done.
	def api(self,method,api_endpoint,payload):

		# Fully combined URL that we will use in the request.
		request_url = self.url + api_endpoint

		# GET requests
		if method.lower() == "get":
			response = requests.get(request_url, auth=('apikey', self.apikey), params=payload, verify=False)

		# POST requests
		elif method.lower() == "post":
			response = requests.post(request_url, auth=('apikey', self.apikey), json=payload, verify=False)

		# PATCH requests
		elif method.lower() == "patch":
			response = requests.patch(request_url, auth=('apikey', self.apikey), json=payload, verify=False)

		# Blow up on bogus methods (or methods we can't handle yet)
		else:
			raise ValueError("Unknown method: {}".format(method))
			return None

		# Parse the response from the server
		try:
			response.raise_for_status()
			body = response.json()
		except requests.exceptions.HTTPError as err:
			print("Error: {} {}".format(str(response.status_code), err))
			print(json.dumps(response.json(), indent=4))
		except ValueError:
			print("Cannot decode json, got %s" % response.text)

		# Everything worked. Pass the returned data back to the calling 
		# function to do something with it.
		return body


	### Mailchimp Methods

	# Get the ID of a List from its name
	def get_list_id_by_name(self,list_name):
		
		payload = {
			'fields': 'lists.id,lists.name',
			'count': 10,
			'offset': 0
		}

		while True:
			result = self.api('GET','/lists',payload)

			if len(result['lists']) == 0:
				break

			for list in result['lists']:
				if list['name'] == list_name:
					return list['id']

			payload['offset'] += payload['count']

		return None

	# Get the ID of a Segment from its name
	def get_segment_id_by_name(self,segment_name):
		
		payload = {
			'fields': 'segments.id,segments.name',
			'count': 10,
			'offset': 0
		}

		while True:
			result = self.api('GET','/lists/' + self.list_id + '/segments',payload)

			if len(result['segments']) == 0:
				break

			for segment in result['segments']:
				if segment['name'] == segment_name:
					return segment['id']

			payload['offset'] += payload['count']

		return None

	# Create a new segment from a given JSON payload
	def create_segment(self,payload):

		result = self.api("POST",'/lists/' + self.list_id + '/segments',payload)

		if 'id' in result:
			return result['id']
		else:
			return None

	# Update a segment with a given JSON payload
	def update_segment(self,segment_id,payload):

		result = self.api("PATCH",'/lists/' + self.list_id + '/segments/' + str(segment_id),payload)

		if 'id' in result:
			return result['id']
		else:
			return None

	# Pull the members of a segment
	def get_segment_members_page(self,segment_id,count):

		payload = {
			'fields': 'members.id,members.email_address,members.status,members.merge_fields',
			'count': count,
			'offset': 0,
		}

		result = self.api("GET",'/lists/' + self.list_id + '/segments/' + str(segment_id) + '/members',payload)

		return result

	def update_member(self,subscriber_hash,ravcamp,ravcode):

		payload = {
			'merge_fields': {
				'RAVCAMP': ravcamp,
				'RAVCODE': ravcode
			}
		}

		result = self.api("PATCH",'/lists/' + self.list_id + '/members/' + subscriber_hash,payload)

		return result

	### Petalbear Methods

	def create_autoload_segment(self,ravcamp):

		self.ravcamp = ravcamp

		payload = {
			'name': 'Autoload',
			'options': {
				'match': 'all',
				'conditions': [
					{
						'condition_type': 'TextMerge',
						'field': 'RAVCAMP',
						'op': 'not',
						'value': self.ravcamp
					}
				]
			}
		}

		segment_id = self.get_segment_id_by_name('Autoload')

		if segment_id is None:
			segment_id = self.create_segment(payload)
		else:
			segment_id = self.update_segment(segment_id,payload)

		return segment_id

	def assign_ravcodes_to_segment(self,segment_id,count):

		while True:

			result = self.get_segment_members_page(segment_id,count)

			if len(result['members']) == 0:
				break

			for member in result['members']:
				if member['status'] == 'subscribed':
					result = self.update_member(member['id'],self.ravcamp,self.get_ravcode())

	def load_ravcodes(self,ravcodesfile):

		self.ravcodes = []

		try:
			with open(ravcodesfile, 'r') as ravcodesfilehandle:
				ravcodestack = csv.reader(ravcodesfilehandle)
				# Skip header row
				next(ravcodesfilehandle)
				for code in ravcodestack:
					self.ravcodes.insert(0,code[0])
		except:
			raise

	def get_ravcode(self):
		
		return self.ravcodes.pop()
