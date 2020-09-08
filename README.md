# nba-movement-data
Ever since the nba stopped public access of their movement data, I though it would be good to have a copy of @neilmj data repo incase he deletes his data repo.

Credit: [@neilmj](https://github.com/neilmj/BasketballData)
Credit[@sealneward](https://github.com/sealneaward)

# Instructions

### In movement/constant.py change the following line
```py 
import os
# change this data_dir for personal path
if os.environ['HOME'] == '/home/neil':
    data_dir = '/home/neil/projects/nba-movement-data'
else:
    raise Exception("Unspecified data_dir, unknown environment")
```
### Setting up directory 
In nba-movement-data run
```
python setup.py build
python setup.py install
```
### Convert raw game data to shot data
In scripts run
```
python run_files.py
```
This will take a long time, as it processes 50 games at a time and runs all the conversion scripts. This takes up 20-50gb per run (everything is removed after). 

### Gathering additional data
In scripts run
```
python stats_api.py
python player_shots_kmeans.py
python possessions_and_free_throws.py
```
These scripts will give you the data necessary when working through the train_model and xRatings notebooks.

## Or you can skip all those things since I have already computed these things
