
# coding: utf-8

# In[1]:

import pandas as pd
import sklearn
import numpy as np


# Clustering players by shooting ability across our 4 defined shot intervals

# In[2]:

#get all players and their fgm & fga at the 5 foot intervals
players_shots = pd.read_csv("./data/player_shots.csv")
players_shots.drop("Unnamed: 0",axis = 1,inplace=True)
players_shots


# In[3]:

#get each player's fga & fgm at the following intervals
#0-4 feet
rim_shots = players_shots.iloc[:,1:3].values
#5-9 feet
close_shots = players_shots.iloc[:,3:5].values
#10 -1 9 feet
mid_shots = players_shots.iloc[:,5:9].values
#20+ feet
long_shots = players_shots.iloc[:,9:].values


# In[4]:

from sklearn.cluster import KMeans
#get cluster for each player for each shot distance cluster
kmeans_short = KMeans(n_clusters = 3,random_state =42).fit(rim_shots)
kmeans_close = KMeans(n_clusters = 3,random_state =42).fit(close_shots)
kmeans_mid = KMeans(n_clusters = 4,random_state =42).fit(mid_shots)
kmeans_long = KMeans(n_clusters = 3,random_state =42).fit(long_shots)


# In[5]:

players_shots['short_cluster'] = kmeans_short.labels_
players_shots['close_cluster'] = kmeans_close.labels_
players_shots['mid_cluster'] = kmeans_mid.labels_
players_shots['long_cluster'] = kmeans_long.labels_


# In[6]:

ps_clusters = players_shots[['player_id','short_cluster','close_cluster','mid_cluster','long_cluster']]
#save cluster information on its own
ps_clusters.to_csv("../data/player_shot_clusters.csv")


# In[7]:

#add player clusters to each shot in database
ps_clusters = pd.read_csv("../data/player_shot_clusters.csv")
all_shots = pd.read_csv("../data/all_shots.csv")
all_shots = all_shots.merge(ps_clusters,left_on='PLAYER_ID',right_on='player_id')
all_shots.to_csv("../data/all_shots_players.csv")


# In[ ]:



