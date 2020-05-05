#!/usr/bin/env python3
#####
# process_mc2sn_queue.py - Move files from new to cur if the user is subscribed.
#####

import logging
import libpetalbear
import argparse
import os

queue_path = "/srv/data/www/violentlydomestic.com/mc2sn"
queue_path_new = queue_path+"/new"
queue_path_cur = queue_path+"/cur"

optarg = argparse.ArgumentParser(prog="process_mc2sn_queue",description="Move files from new to cur if the user is subscribed.")
optarg.add_argument('-d','--debug',help="Enable debug logging.",action="store_const",const="yes")
optarg.add_argument('-f','--config',help="Configuration file for petalbear, defaults to ~/.petalbearrc",default=os.path.expanduser("~/.petalbearrc"))
config = optarg.parse_args()
if config.debug == "yes":
	logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',level=logging.DEBUG,filename='./check_mailchimp_sub.log')
else:
	logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',level=logging.INFO,filename='./check_mailchimp_sub.log')

pb = libpetalbear.petalbear(config.config)

for file in os.listdir(queue_path+"/new"):
	filename = os.fsdecode(file)
	f = open(queue_path_new+"/"+filename,"r")
	email_address = f.readline().split(":")[1]
	status = pb.get_member_status(email_address.encode("ascii").lower())
	if status in ["subscribed"]:
		os.rename(queue_path_new+"/"+filename,queue_path_cur+"/"+filename)
