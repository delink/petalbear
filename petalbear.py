#!/usr/bin/env python3
#####
# petalbear - Load ravelry codes into Mailchimp merge fields
#####

import logging
import libpetalbear
import argparse
import os

optarg = argparse.ArgumentParser(prog="petalbear")
optarg.add_argument('-d','--debug',help="Enable debug logging.",action="store_const",const="yes")
optarg.add_argument('-f','--config',help="Configuration file for petalbear, defaults to ~/.petalbearrc",default=os.path.expanduser("~/.petalbearrc"))
optarg.add_argument('-r','--ravcodes',help="CSV file from ravlery containing codes. No default.",required=True)
optarg.add_argument('-c','--campaign',help="Name of ravelry campaign. No default.",required=True)
config = optarg.parse_args()
if config.debug == "yes":
	logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',level=logging.DEBUG,filename='./petalbear.log')
else:
	logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',level=logging.INFO,filename='./petalbear.log')

pb = libpetalbear.petalbear(config.config)

pb.load_ravcodes(config.ravcodes)

segment_id = pb.create_autoload_segment(config.campaign)
pb.assign_ravcodes_to_segment(segment_id,50)
