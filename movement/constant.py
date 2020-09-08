import os
# change this data_dir for personal path
if os.environ['HOME'] == '/Users/home':
    data_dir = '/Users/home/path/to/nba-movement-data'
else:
    raise Exception("Unspecified data_dir, unknown environment")