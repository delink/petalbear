#!/usr/bin/env python3

import libpetalbear

pb = libpetalbear.petalbear('/Users/brian/.petalbearrc')

list_id = pb.get_list_id_by_name('Test List')
segment_id = pb.create_autoload_segment(list_id,'petalbear')
pb.load_ravcodes_to_segment(list_id,segment_id)
