#!/usr/bin/env python
# coding: utf-8
import glob
import os
import shutil
import subprocess


sevenz_files = glob.glob("../data/games_2/*.7z")
len(sevenz_files)
start = 0
for i in range(50,len(sevenz_files),50):
	
	#move 7z files from games_3 to data dir
	zip_to_move = sevenz_files[start:i]
	for sz in zip_to_move:
	    file_name = sz.split("games_2/")[1]
	    dest_name = "../data/{}".format(file_name)
	    shutil.move(sz,dest_name)

    
	#run setup.sh
	os.chdir("../data")
	subprocess.run(["bash","setup.sh"])
	os.chdir("../../movement")
	print(os.getcwd())
	#run json to csv
	print("CONVERTING JSON TO CSV")
	exec(open("json_to_csv.py").read())
	#delete .DS_Store, seems to mess up scripts
	subprocess.run(["rm","../data/csv/.DS_Store"]) 
	#run convert movement
	print("CONVERTING MOVEMENT")
	exec(open("convert_movement.py").read())
	#again delete .DS_Store
	subprocess.run(["rm", "../data/converted/.DS_Store"])
	#run fix_shots
	print("FIXING SHOTS")
	exec(open("fix_shot_times.py").read())
	#run game_df
	os.chdir("../scripts")
	print("CREATING GAME SHOTS")
	exec(open("game_df.py").read())

	print("Moving, removing files")
	#shot files should be generated, move all the 7z files
	sz_curr = glob.glob("../data/*.7z")
	for sz in sz_curr:
	    file_name = sz.split("data/")[1]
	    dest_name = "../data/games_1/{}".format(file_name)
	    shutil.move(sz,dest_name)
	#remove all the csv, converted files
	csv_to_remove = glob.glob("../data/csv/*.csv")
	converted_to_remove = glob.glob("../data/converted/*.csv")
	json_to_remove = glob.glob("../data/*.json")
	for csv in csv_to_remove:
	    os.remove(csv)
	for csv in converted_to_remove:
	    os.remove(csv)
	for json in json_to_remove:
		os.remove(json)    
	
	#start with next batch
	start = i




