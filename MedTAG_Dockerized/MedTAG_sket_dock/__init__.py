from MedTAG_sket_dock_App.sket.sket.sket import SKET
import time
import json
import os
print('start sket initialization')
# workpath = os.path.dirname(os.path.abspath(__file__))  # Returns the Path your .py file is in
# # print(workpath)
# output_concepts_dir = os.path.join(workpath, '../sket_rest_App/config.json')
# f = open(output_concepts_dir,'r')
# data = json.load(f)

st = time.time()
# sket_pipe = SKET('colon', 'en', 'en_core_sci_sm', True, None, None, False, 0)
sket_pipe = SKET('colon', 'en', 'en_core_sci_sm', True, None, None, False, 0)
end = time.time()
print('sket initialization completed in: ',str(end-st), ' seconds')
