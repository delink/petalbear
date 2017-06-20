#####
# libpetalbear.py - Load ravelry one-use codes into Mailchimp merge fields
#####

import uuid
import configparser
import requests
import json
import csv
import logging
import hashlib
requests.packages.urllib3.disable_warnings()

class petalbear:

	# Take the passed in configuration file and get ready to Mailchimp
	def __init__(self,conffilename):
		self.uuid = uuid.uuid4()
		logging.info("action=\"create uuid\" uuid=\"{}\"".format(self.uuid))
		logging.info("uuid=\"{}\" action=\"read config\" filename=\"{}\"".format(self.uuid,conffilename))
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
		logging.info("uuid=\"{}\" action=\"read config\" result=\"success\" list_name=\"{}\" list_id=\"{}\"".format(self.uuid,self.config['mailchimp']['list_name'],self.list_id))

	# Generic API method to be used by all other methods when reaching out to mailchimp.
	# No pagination loops should happen inside of here. One and done.
	def api(self,method,api_endpoint,payload):

		# Fully combined URL that we will use in the request.
		request_url = self.url + api_endpoint

		# GET requests
		if method.lower() == "get":
			logging.debug("uuid=\"{}\" action=\"api request\" method=\"get\" url=\"{}\"".format(self.uuid,request_url))
			response = requests.get(request_url, auth=('apikey', self.apikey), params=payload, verify=False)

		# POST requests
		elif method.lower() == "post":
			logging.debug("uuid=\"{}\" action=\"api request\" method=\"post\" url=\"{}\"".format(self.uuid,request_url))
			response = requests.post(request_url, auth=('apikey', self.apikey), json=payload, verify=False)

		# PATCH requests
		elif method.lower() == "patch":
			logging.debug("uuid=\"{}\" action=\"api request\" method=\"patch\" url=\"{}\"".format(self.uuid,request_url))
			response = requests.patch(request_url, auth=('apikey', self.apikey), json=payload, verify=False)

		# Blow up on bogus methods (or methods we can't handle yet)
		else:
			logging.error("uuid=\"{}\" action=\"api request\" method=\"unknown\" url=\"{}\"".format(self.uuid,request_url))
			raise ValueError("Unknown method: {}".format(method))
			return None

		# Parse the response from the server
		try:
			response.raise_for_status()
			body = response.json()
		except requests.exceptions.HTTPError as err:
			logging.error("uuid=\"{}\" action=\"api result\" result=\"failure\" http_error=\"{}\" url=\"{}\"".format(self.uuid,str(response.status_code),request_url))
			raise
		except ValueError:
			logging.error("uuid=\"{}\" action=\"api request\" result=\"failure\" url=\"{}\" message=\"{}\"".format(self.uuid,request_url,response.text))
			raise

		# Everything worked. Pass the returned data back to the calling 
		# function to do something with it.
		logging.debug("uuid=\"{}\" action=\"api request\" result=\"success\" url=\"{}\"".format(self.uuid,request_url))
		return body


	### Mailchimp Methods

	# Get the ID of a List from its name
	def get_list_id_by_name(self,list_name):
		
		payload = {
			'fields': 'lists.id,lists.name',
			'count': 10,
			'offset': 0
		}

		logging.debug("uuid=\"{}\" action=\"get list id\" list_name=\"{}\"".format(self.uuid,list_name))
		while True:
			result = self.api('GET','/lists',payload)

			if len(result['lists']) == 0:
				break

			for list in result['lists']:
				if list['name'] == list_name:
					logging.debug("uuid=\"{}\" action=\"get list id\" result=\"success\" list_name=\"{}\" list_id=\"{}\"".format(self.uuid,list_name,list['id']))
					return list['id']

			payload['offset'] += payload['count']

		logging.debug("uuid=\"{}\" action=\"get list id\" result=\"failure\" list_name=\"{}\"".format(self.uuid,list_name))
		return None

	# Get the ID of a Segment from its name
	def get_segment_id_by_name(self,segment_name):
		
		payload = {
			'fields': 'segments.id,segments.name',
			'count': 10,
			'offset': 0
		}

		logging.debug("uuid=\"{}\" action=\"get segment id\" segment_name=\"{}\"".format(self.uuid,segment_name))
		while True:
			result = self.api('GET','/lists/' + self.list_id + '/segments',payload)

			if len(result['segments']) == 0:
				break

			for segment in result['segments']:
				if segment['name'] == segment_name:
					logging.debug("uuid=\"{}\" action=\"get segment id\" result=\"success\" segment_name=\"{}\" segment_id=\"{}\"".format(self.uuid,segment_name,segment['id']))
					return segment['id']

			payload['offset'] += payload['count']

		logging.debug("uuid=\"{}\" action=\"get segment id\" result=\"failure\" segment_name=\"{}\"".format(self.uuid,segment_name))
		return None

	# Create a new segment from a given JSON payload
	def create_segment(self,payload):

		logging.info("uuid=\"{}\" action=\"create segment\" segment_name=\"{}\"".format(self.uuid,payload['name']))
		result = self.api("POST",'/lists/' + self.list_id + '/segments',payload)

		if 'id' in result:
			logging.info("uuid=\"{}\" action=\"create segment\" result=\"success\" segment_name=\"{}\" segment_id=\"{}\"".format(self.uuid,payload['name'],result['id']))
			return result['id']
		else:
			logging.info("uuid=\"{}\" action=\"create segment\" result=\"failure\" segment_name=\"{}\"".format(self.uuid,payload['name']))
			return None

	# Update a segment with a given JSON payload
	def update_segment(self,segment_id,payload):

		logging.info("uuid=\"{}\" action=\"update segment\" segment_id=\"{}\"".format(self.uuid,segment_id))
		result = self.api("PATCH",'/lists/' + self.list_id + '/segments/' + str(segment_id),payload)

		if 'id' in result:
			logging.info("uuid=\"{}\" action=\"update segment\" result=\"success\" segment_id=\"{}\"".format(self.uuid,segment_id))
			return result['id']
		else:
			logging.info("uuid=\"{}\" action=\"update segment\" result=\"failure\" segment_id=\"{}\"".format(self.uuid,segment_id))
			return None

	# Pull the members of a segment
	def get_segment_members_page(self,segment_id,count):

		payload = {
			'fields': 'members.id,members.email_address,members.status,members.merge_fields',
			'count': count,
			'offset': 0,
		}

		logging.info("uuid=\"{}\" action=\"get segment page\" segment_id=\"{}\"".format(self.uuid,segment_id))
		result = self.api("GET",'/lists/' + self.list_id + '/segments/' + str(segment_id) + '/members',payload)

		logging.info("uuid=\"{}\" action=\"get segment page\" result=\"success\" segment_id=\"{}\" count=\"{}\"".format(self.uuid,segment_id,len(result['members'])))
		return result

	def get_member_status(self,email_address):

		payload = {
			'fields': 'id,email_address,status',
		}

		logging.info("uuid=\"{}\" action=\"get member status\" email_address=\"{}\"".format(self.uuid,email_address))

		try:
			result = self.api("GET",'/lists/' + self.list_id + '/members/' + str(hashlib.md5(email_address).hexdigest()),payload)
			status = result['status']
		except requests.exceptions.HTTPError as err:
			status = "unknown"

		logging.info("uuid=\"{}\" action=\"get member status\" result=\"success\" email_address=\"{}\" status=\"{}\"".format(self.uuid,email_address,status))

		return status

	def update_member(self,subscriber_hash,ravcamp,ravcode):

		payload = {
			'merge_fields': {
				'RAVCAMP': ravcamp,
				'RAVCODE': ravcode
			}
		}

		logging.info("uuid=\"{}\" action=\"update member\" subscriber_hash=\"{}\" campaign=\"{}\" code=\"{}\"".format(self.uuid,subscriber_hash,ravcamp,ravcode))
		result = self.api("PATCH",'/lists/' + self.list_id + '/members/' + subscriber_hash,payload)

		return result

	### Petalbear Methods

	def create_autoload_segment(self,ravcamp):

		self.ravcamp = ravcamp

		logging.info("uuid=\"{}\" action=\"create autoload segment\" campaign=\"{}\"".format(self.uuid,self.ravcamp))
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

		logging.info("uuid=\"{}\" action=\"create autoload segment\" result=\"success\" campaign=\"{}\" segment_id=\"{}\"".format(self.uuid,self.ravcamp,segment_id))
		return segment_id

	def assign_ravcodes_to_segment(self,segment_id,count):

		logging.info("uuid=\"{}\" action=\"assign codes to segment\" segment_id=\"{}\"".format(self.uuid,segment_id))
		while True:

			result = self.get_segment_members_page(segment_id,count)

			if len(result['members']) == 0:
				logging.info("uuid=\"{}\" action=\"assign codes to segment\" result=\"success\" segment_id=\"{}\"".format(self.uuid,segment_id))
				break

			for member in result['members']:
				logging.info("uuid=\"{}\" action=\"process member\" email_address=\"{}\" subscriber_hash=\"{}\"".format(self.uuid,member['email_address'],member['id']))
				if member['status'] == 'subscribed':
					ravcode = self.get_ravcode()
					result = self.update_member(member['id'],self.ravcamp,ravcode)
					logging.info("uuid=\"{}\" action=\"process member\" result=\"success\" email_address=\"{}\" subscriber_hash=\"{}\" ravcode=\"{}\"".format(self.uuid,member['email_address'],member['id'],ravcode))
				else:
					logging.info("uuid=\"{}\" action=\"process member\" result=\"failure\" status=\"{}\" email_address=\"{}\"".format(self.uuid,member['status'],member['email_address']))

	def load_ravcodes(self,ravcodesfile):

		self.ravcodes = []

		logging.info("uuid=\"{}\" action=\"load ravcodes\" filename=\"{}\"".format(self.uuid,ravcodesfile))

		try:
			with open(ravcodesfile, 'r') as ravcodesfilehandle:
				ravcodestack = csv.reader(ravcodesfilehandle)
				# Skip header row
				next(ravcodesfilehandle)
				for code in ravcodestack:
					self.ravcodes.insert(0,code[0])
				logging.info("uuid=\"{}\" action=\"load ravcodes\" result=\"success\" filename=\"{}\" count=\"{}\"".format(self.uuid,ravcodesfile,len(self.ravcodes)))
		except:
			raise

	def get_ravcode(self):
		
		ravcode = self.ravcodes.pop()
		logging.debug("uuid=\"{}\" action=\"get ravcode\" result=\"success\" code=\"{}\" count=\"{}\"".format(self.uuid,ravcode,len(self.ravcodes)))
		return ravcode
