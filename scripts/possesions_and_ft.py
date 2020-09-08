
# coding: utf-8

# In[17]:

import numpy as np
import pandas as pd
import json
import time


# In[18]:

from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.endpoints import ScoreboardV2
from nba_api.stats.endpoints import BoxScoreAdvancedV2
from nba_api.stats.endpoints import BoxScoreTraditionalV2
from nba_api.stats.endpoints import playerdashptshots
from nba_api.stats.endpoints import playerdashboardbyshootingsplits
from nba_api.stats.static import players
from nba_api.stats.endpoints import commonteamroster
from nba_api.stats.static import teams


# Getting player career ft percentages, merging with free throw box score stats from games to get expected points from free throws
# Also get net ratings, number of possesions for each team in each game

# In[15]:

#these are all the games in the last quarter of the dataset
games = [21500483, 21500479, 21500482, 21500478, 21500475, 21500476,
       21500480, 21500481, 21500474, 21500489, 21500488, 21500487,
       21500486, 21500485, 21500484, 21500490, 21500492, 21500493,
       21500494, 21500491, 21500496, 21500495, 21500505, 21500498,
       21500497, 21500500, 21500501, 21500504, 21500499, 21500503,
       21500502, 21500509, 21500506, 21500507, 21500508, 21500510,
       21500513, 21500517, 21500516, 21500515, 21500520, 21500518,
       21500514, 21500511, 21500512, 21500519, 21500521, 21500522,
       21500524, 21500523, 21500528, 21500535, 21500527, 21500531,
       21500533, 21500532, 21500534, 21500529, 21500526, 21500530,
       21500525, 21500538, 21500537, 21500539, 21500536, 21500547,
       21500543, 21500540, 21500548, 21500542, 21500545, 21500549,
       21500546, 21500541, 21500544, 21500555, 21500552, 21500553,
       21500556, 21500554, 21500550, 21500551, 21500563, 21500560,
       21500557, 21500564, 21500561, 21500559, 21500565, 21500558,
       21500562, 21500568, 21500566, 21500567, 21500576, 21500572,
       21500570, 21500574, 21500569, 21500575, 21500571, 21500573,
       21500577, 21500584, 21500578, 21500586, 21500585, 21500580,
       21500582, 21500581, 21500579, 21500592, 21500591, 21500598,
       21500599, 21500593, 21500597, 21500595, 21500594, 21500601,
       21500596, 21500617, 21500619, 21500618, 21500622, 21500615,
       21500616, 21500621, 21500624, 21500620, 21500623, 21500627,
       21500625, 21500628, 21500626, 21500635, 21500636, 21500633,
       21500639, 21500631, 21500632, 21500638, 21500637, 21500634,
       21500630, 21500629, 21500653, 21500652, 21500649, 21500645,
       21500646, 21500650, 21500648, 21500651, 21500647, 21500663,
       21500660, 21500657, 21500655, 21500662, 21500658, 21500661]
str_games = []
#game ids have 00 to start in the NBA Api 
for game in games:
    str_game = str(game)
    str_game = "00" + str_game
    str_games.append(str_game)


# In[41]:

game_ratings = []
#get offensive ratings and # of possessions for each team in each game
for game_id in str_games:
    bsa = BoxScoreAdvancedV2(game_id=game_id)
    ratings= bsa.get_data_frames()[1][['GAME_ID','TEAM_ID','POSS','NET_RATING']].values
    team1 = ratings[0]
    team2 = ratings[1]
    game_ratings.append(team1)
    game_ratings.append(team2)


# In[48]:

#save rating data
pd.DataFrame(game_ratings,columns = ['GAME_ID','TEAM_ID','POSSESIONS','NET_RATING']).to_csv("possesions_ratings.csv")


# In[19]:

game_fta = []
#get free throw attempts for each player in the games we are examining
for game_id in str_games:
    bsa = BoxScoreTraditionalV2(game_id=game_id)
    game_fta.append(bsa.get_data_frames()[0][['GAME_ID', 'TEAM_ID','PLAYER_ID','FTA']])
#save box score free throw stats to a csv
pd.concat(game_fta).to_csv("../data/free_throw_attemps.csv")


# In[20]:

#the fta csv contains all players on each roster in the games we care about, so only need to get player ids from here
fta_df = pd.read_csv("../data/free_throw_attemps.csv")
players = fta_df['PLAYER_ID'].unique()


# In[39]:

player_fts = {}
for player_id in players:
    #get career ft % for each player before 2015-16
    pcs = playercareerstats.PlayerCareerStats(player_id=player_id)
    df = pcs.get_data_frames()[0]
    df = df[df['SEASON_ID'] < '2015-16']
    ftm = df['FTM'].sum()
    fta = df['FTA'].sum()
    #"regression to the mean". really basic, average ft% is 75%. This probably could be done better
    if fta > 0:
        if fta < 20:
            ftm += 15
            fta += 20
        ftp = ftm / fta
    else:
        ftp = 0.75
    #data saved in dictionary mapping player ft% to player id
    player_fts[player_id] = ftp
    time.sleep(2)


# In[41]:

#get data from player_fts dictionary
fta_df['player_ft%'] = fta_df['PLAYER_ID'].apply(lambda x: player_fts[x])
#get expected points from FT
fta_df['xFTP'] = fta_df['FTA'] * fta_df['player_ft%']


# In[45]:

#save expected free throw points to csv
fta_df.to_csv("../data/free_throw_points.csv")


# In[ ]:



