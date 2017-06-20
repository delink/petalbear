#!/usr/bin/env python3
#####
# check_mailchimp_sub.py - Check the subscription status of a Mailchimp user.
#####

import logging
import libpetalbear
import argparse
import os

optarg = argparse.ArgumentParser(prog="check_mailchimp_sub",description="Check Mailchimp subscription status of one email address using libpetalbear.")
optarg.add_argument('-d','--debug',help="Enable debug logging.",action="store_const",const="yes")
optarg.add_argument('-f','--config',help="Configuration file for petalbear, defaults to ~/.petalbearrc",default=os.path.expanduser("~/.petalbearrc"))
optarg.add_argument('email_address',metavar='email',type=str,nargs=1,help="Email address to check in Mailchimp.")
config = optarg.parse_args()
if config.debug == "yes":
	logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',level=logging.DEBUG,filename='./check_mailchimp_sub.log')
else:
	logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',level=logging.INFO,filename='./check_mailchimp_sub.log')

pb = libpetalbear.petalbear(config.config)

print('{}'.format(pb.get_member_status(config.email_address[0].encode("ascii").lower())))
