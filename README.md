# nba-movement-data
Serious credit for hosting the tracking data goes to:
[@neilmj](https://github.com/neilmj/BasketballData)
[@sealneward](https://github.com/sealneaward)

# Instructions
These instructions will let you run the project "from scratch" as I did
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

## Or you can skip all that since I have already computed these things, and just run the notebooks
The notebooks will train models on the data and spit out some nice charts. So far, accuracy is around 63%. 
