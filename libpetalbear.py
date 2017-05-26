#####
# libpetalbear.py - Load ravelry one-use codes into Mailchimp merge fields
#####

import configparser
import os
import requests
import json
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
			'count': 50,
			'offset': 0
		}

		result = self.api('GET','/lists',payload)
		for list in result['lists']:
			if list['name'] == list_name:
				return list['id']

		return None

	# Get the ID of a Segment from its name
	def get_segment_id_by_name(self,list_id,segment_name):
		
		payload = {
			'fields': 'segments.id,segments.name',
			'count': 50,
			'offset': 0
		}

		result = self.api('GET','/lists/' + list_id + '/segments',payload)
		for segment in result['segments']:
			if segment['name'] == segment_name:
				return segment['id']

		return None

	# Create a new segment from a given JSON payload
	def create_segment(self,list_id,payload):

		result = self.api("POST",'/lists/' + list_id + '/segments',payload)

		if 'id' in result:
			return result['id']
		else:
			return None

	# Pull the members of a segment
	def get_segment_members(self,list_id,segment_id):

		payload = {
			'fields': 'members.id,members.email_address,members.status,members.merge_fields',
			'count': 50,
			'offset': 0,
		}

		result = self.api("GET",'/lists/' + list_id + '/segments/' + str(segment_id) + '/members',payload)

		return result

	def update_member(self,list_id,subscriber_hash,ravcamp,ravcode):

		payload = {
			'merge_fields': {
				'RAVCAMP': ravcamp,
				'RAVCODE': ravcode
			}
		}

		result = self.api("PATCH",'/lists/' + list_id + '/members/' + subscriber_hash,payload)

		return result

	### Petalbear Methods

	def create_autoload_segment(self,list_id,ravcamp):

		payload = {
			'name': 'Autoload',
			'options': {
				'match': 'all',
				'conditions': [
					{
						'condition_type': 'TextMerge',
						'field': 'RAVCAMP',
						'op': 'not',
						'value': ravcamp
					}
				]
			}
		}

		segment_id = self.get_segment_id_by_name(list_id,'Autoload')

		if segment_id is None:
			segment_id = self.create_segment(list_id,payload)

		return segment_id

	def load_ravcodes_to_segment(self,list_id,segment_id):

		result = self.get_segment_members(list_id,segment_id)

		for member in result['members']:
			if member['status'] == 'subscribed':
				result = self.update_member(list_id,member['id'],'petalbear','code1')
				print(result['email_address'])
