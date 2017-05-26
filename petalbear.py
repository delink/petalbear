#!/usr/bin/env python3

import libpetalbear

pb = libpetalbear.petalbear('/Users/brian/.petalbearrc')

list_id = pb.get_list_id_by_name('Test List')
print(pb.get_segment_id_by_name(list_id,'petalbear'))
