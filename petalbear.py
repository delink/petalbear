#!/usr/bin/env python3

import libpetalbear

pb = libpetalbear.petalbear('/Users/brian/.petalbearrc')

pb.load_ravcodes('/Users/brian/Desktop/Tacit.csv')

list_id = pb.get_list_id_by_name('Test List')
segment_id = pb.create_autoload_segment(list_id,'testravcodes2')
pb.assign_ravcodes_to_segment(list_id,segment_id)
