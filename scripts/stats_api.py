
# coding: utf-8

# In[24]:

import numpy as np
import pandas as pd
import json
import time


# In[15]:

from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.endpoints import playerdashptshots
from nba_api.stats.endpoints import playerdashboardbyshootingsplits
from nba_api.stats.static import players
from nba_api.stats.endpoints import commonteamroster
from nba_api.stats.static import teams


# Get player career fgm and fga for each 5 foot range the NBA provides.

# In[4]:

def get_team_ids():
    '''get all teams in the nba'''
    nba_teams = teams.get_teams()
    teams_list = []
    for team in nba_teams:
        teams_list.append(team['id'])
    return teams_list


# In[25]:

def get_players(teams_list):
    '''get all players on each team in 2015-16 '''
    players_list = []
    for team_id in teams_list:
        roster = commonteamroster.CommonTeamRoster(team_id = team_id,season='2015-16')
        players_list.extend(list(roster.get_data_frames()[0]['PLAYER_ID'].values))
        time.sleep(5)
    return players_list


# In[41]:

def get_seasons(player_id):
    '''
    Get all the seasons a player played in (before 2015-16)
    '''
    career = playercareerstats.PlayerCareerStats(player_id=player_id)
    df = career.get_data_frames()[0]
    #we want all shots before this seasons
    df = df[df['SEASON_ID'] < '2015-16']
    seasons = list(df['SEASON_ID'].values)
    return seasons


# In[47]:

def all_player_seasons(players_list):
    '''
    Get all seasons played in for all players
    '''
    player_seasons = {}
    for player_id in players_list:
        seasons = get_seasons(player_id)
        player_seasons[player_id] = seasons
        #hvae to sleep or else the NBA shuts us down
        time.sleep(2)
    return player_seasons


# In[109]:

def player_shooting(player_id,seasons):
    '''
    Get player shootings stats for each of the shot ranges below
    
    '''
    player_shooting = {}
    print("Getting shots for player {}".format(player_id))
    shot_ranges = ['0-4','5-9','10-14','15-19','20-24','25-29','30-34','40+']
    player_shots = np.zeros((9,2))
    #loop through each season, adding shooting totals at each distance
    for season in seasons:
        pds = playerdashboardbyshootingsplits.PlayerDashboardByShootingSplits(player_id = player_id,season=season)
        shots = pds.get_data_frames()[1][['FGM','FGA']].values
        #sometimes data is missing, seems like it is always for the 40+ foot range (where they likely took no shots)
        #not missing = 9 rows, missing = 8 rows
        if shots.shape == (9,2):
            player_shots = player_shots + shots
        elif shots.shape == (8,2):
            #just add a column of 0s to the end, should not change much
            shots = np.concatenate((shots,np.zeros((1,2))),0)
            player_shots = player_shots + shots
        else:
            print("Player {} has weird shots in season {} ".format(player_id,season))
        #again, have to sleep or the NBA will shut us down
        #I blame Adam Silver
        time.sleep(2)
    #returning dictionary that maps player id to 9x2 np array
    player_shooting["player_id"] = player_id
    #create a dictionary mapping shot ranges to makes attempts
    for sr,row in zip(shot_ranges, player_shots):
        player_shooting[sr+"_fgm"] = row[0]
        player_shooting[sr+"_fga"] = row[1]
    return player_shooting


# In[9]:

#get all team ids
teams_list = get_team_ids()
#get all players from 2015-16 season
players_list = get_players(teams_list)
#get all the seasons prior to 2015-16 each player has played in, mapped to each player id
player_seasons = all_player_seasons(players_list)
#get shooting splits by distance for each player across their whole career
all_player_shots = []
num_players = len(players_list)
players_finished = 0
for player_id in player_seasons:
    all_player_shots.append(player_shooting(player_id,player_seasons[player_id]))
    players_finished += 1
    print("Got shots for {} / {} players".format(players_finished,num_players))  
    
    if players_finished % 20 == 0:
        player_shots_df = pd.DataFrame(all_player_shots,columns = ['player_id','0-4_fgm','0-4_fga','5-9_fgm','5-9_fga',
                                                      '10-14_fgm','10-14_fga','15-19_fgm','15-19_fga','20-24_fgm',
                                                      '20-24_fga','25-29_fgm','25-29_fga','30-34_fgm','30-34_fga',
                                                      '40+_fgm','40+_fga',])
        player_shots_df.to_csv("../data/player_shots.csv")


# Sometimes the API will straight up not work, rerun the program for the few players (~10) it didn't work for

# In[118]:

ps_players= player_shots_df['player_id'].values.astype("int64")


# In[123]:

redo =[]
for item in players_list:
    if item not in ps_players:
        redo.append(item)


# In[136]:

pkeys = list(player_seasons.keys())
redo_players = {}
for key in pkeys:
    if int(key) in redo:
        redo_players[key] = player_seasons[key]


# In[155]:

#get shooting splits by distance for each player across their whole career
all_player_shots_redo = []
num_players = len(redo)
players_finished = 0
for player_id in redo_players:
    all_player_shots_redo.append(player_shooting(player_id,redo_players[player_id]))
    players_finished += 1
    print("Got shots for {} / {} players".format(players_finished,num_players))  
    
    if players_finished % 4 == 0:
        redo_player_shots_df = pd.DataFrame(all_player_shots_redo,columns = ['player_id','0-4_fgm','0-4_fga','5-9_fgm','5-9_fga',
                                                      '10-14_fgm','10-14_fga','15-19_fgm','15-19_fga','20-24_fgm',
                                                      '20-24_fga','25-29_fgm','25-29_fga','30-34_fgm','30-34_fga',
                                                      '40+_fgm','40+_fga',])
        redo_player_shots_df.to_csv("../data/redo_player_shots.csv")


# In[163]:

#concatenate with other players shots, save to csv
pd.concat([player_shots_df,redo_player_shots_df]).to_csv("../data/player_shots.csv")


# In[ ]:



