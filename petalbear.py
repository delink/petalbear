#!/usr/bin/env python3

import libpetalbear

pb = libpetalbear.petalbear('/Users/brian/.petalbearrc')

print(pb.get_list_id_by_name('Test List'))
