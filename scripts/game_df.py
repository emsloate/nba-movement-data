
# coding: utf-8

# In[5]:

import pandas as pd
import os
import glob
import numpy as np
# In[6]:

#get game data
def get_game(path):
    game = pd.read_json(path)
    #get ids from events, home team and visiting team info
    game['event_id'] = game['events'].apply(lambda x: int(x['eventId']))
    game['visitor_name'] = game['events'].apply(lambda x: x['visitor']['name'])
    game['visitor_id'] = game['events'].apply(lambda x: int(x['visitor']['teamid']))
    game['home_name'] = game['events'].apply(lambda x: x['home']['name'])
    game['home_id'] = game['events'].apply(lambda x: int(x['home']['teamid']))
    return game


# In[7]:

def get_home_visitor_players(game):
    #get all players on visiting team
    visitor = pd.DataFrame(game['events'][0]['visitor'])
    visitor['firstname'] = visitor['players'].apply(lambda x: x['firstname'])
    visitor['lastname'] = visitor['players'].apply(lambda x: x['lastname'])
    visitor['playerid'] = visitor['players'].apply(lambda x: int(x['playerid']))
    visitor['jersey'] = visitor['players'].apply(lambda x: int(x['jersey']))
    visitor['position'] = visitor['players'].apply(lambda x: x['position']).astype('category')
    #get all players on home team
    home = pd.DataFrame(game['events'][0]['home'])
    home['firstname'] = home['players'].apply(lambda x: x['firstname'])
    home['lastname'] = home['players'].apply(lambda x: x['lastname'])
    home['playerid'] = home['players'].apply(lambda x: int(x['playerid']))
    home['jersey'] = home['players'].apply(lambda x: int(x['jersey']))
    home['position'] = home['players'].apply(lambda x: x['position']).astype('category')
    return home, visitor


# In[8]:

#return the moment dictionary corresponding to the time of the shot
def right_moment(event,game_clock):
    moments = event['moments']
    for moment in moments:
        if moment[2] == game_clock:
            return moment
        
    return None


# In[22]:

def get_game_shots(game,shots_fixed,game_id):
    #get only shots that happened in this game
    game_shots = shots_fixed[shots_fixed['GAME_ID'] == game_id]
    #merge shots with events
    this_game_shots = pd.merge(game_shots,game,left_on=['GAME_EVENT_ID'],right_on=['event_id'])
    #get the moment where the shot occured, moment here is an array
    this_game_shots['moment'] = this_game_shots.apply(lambda x: right_moment(x.events,x.SHOT_TIME),axis = 1)
    return this_game_shots


# In[27]:

#some shots will not be able to find the moment, this appears to be because the shot occured before the event started
#this happens because actual shot time is 2-3 seconds before the recorded shot time
def get_missing_shots(this_game_shots,game):
    no_moment = this_game_shots[this_game_shots['moment'].isna()]
    #solution, get previous event and check for time of shot in that event
    no_moment['previous_id'] = no_moment['GAME_EVENT_ID'] - 1
    
    #remerging to get previous event data
    #this will remove some rows- event numbers seem to skip
    #TODO: find way to get these rows, perhaps then merge with event id -2, +1 ?? 
    no_moment = pd.merge(no_moment,game,left_on=['previous_id'],right_on=['event_id'],suffixes=['_x',''])
    #hopefully shot time will be in this event
    no_moment['moment'] = no_moment.apply(lambda x: right_moment(x.events,x.SHOT_TIME),axis = 1)
    #drop duplicate columns so we can add this back to tgs dataframe
    no_moment.drop(no_moment.filter(regex='_x$').columns.tolist(),axis=1, inplace=True)
    no_moment.drop('previous_id',axis = 1,inplace=True)
    
    #re add shots that did not have an inital moment back to the dataframe of shot moments
    #getting shots that originally did not have na moments
    tgs_mom = this_game_shots[~this_game_shots['moment'].isna()]
    #add shots from no_moments
    new_tgs = pd.concat([tgs_mom,no_moment])
    #may still have na moments, have to discard these for now
    new_tgs = new_tgs[~new_tgs['moment'].isna()]
    
    return new_tgs


# In[11]:

#get player id, x & y location for each player. home players are always first 5
def get_xy(new_tgs):
    for i in range(1,6):
        #home players are in spots 1-5 in 5th element of a moment array
        #spot 0 is the ball
        new_tgs['home_p{}'.format(i)] = new_tgs['moment'].apply(lambda x: x[5][i][1])
        new_tgs['home_p{}_x'.format(i)] = new_tgs['moment'].apply(lambda x: x[5][i][2])
        new_tgs['home_p{}_y'.format(i)] = new_tgs['moment'].apply(lambda x: x[5][i][3])
        
        #visitors are 6-10
        new_tgs['visitor_p{}'.format(i)] = new_tgs['moment'].apply(lambda x: x[5][i+5][1])
        new_tgs['visitor_p{}_x'.format(i)] = new_tgs['moment'].apply(lambda x: x[5][i+5][2])
        new_tgs['visitor_p{}_y'.format(i)] = new_tgs['moment'].apply(lambda x: x[5][i+5][3])
    
    return new_tgs


# In[12]:

# def convert_locations(df):
#     # first force all points above 47 to their half court counterparts
#     # keep all original points for furhter limitations to single court
#     for i in range(1,6):
#         df['home_p{}_x_loc_original'.format(i)] = df['home_p{}_x'.format(i)]
#         df['home_p{}_y_loc_original'.format(i)] = df['home_p{}_y'.format(i)]

#         #locations on other side of court are chnaged so they reflect the same location on 1st half of court
#         df.loc[df['home_p{}_x'.format(i)] > 47,'home_p{}_y'.format(i)] = df.loc[df.x_loc > 47, 'home_p{}_y'.format(i)].apply(lambda y: 50 - y)
#         df.loc[df['home_p{}_x'.format(i)] > 47,'home_p{}_x'.format(i)] = df.loc[df.x_loc > 47, 'home_p{}_x'.format(i)].apply(lambda x: 94 - x)

#     # convert to half court scale
#     # note the x_loc and the y_loc are switched in shot charts from movement data (charts are perpendicular)
#     for i in range(1,6):
#     data['x_loc_copy'] = data['x_loc']
#     data['y_loc_copy'] = data['y_loc']

#     # Range conversion formula
#     # http://math.stackexchange.com/questions/43698/range-scaling-problem

#     data['x_loc'] = data['y_loc_copy'].apply(lambda y: 250 * (1 - (y - 0)/(50 - 0)) + -250 * ((y - 0)/(50 - 0)))
#     data['y_loc'] = data['x_loc_copy'].apply(lambda x: -47.5 * (1 - (x - 0)/(47 - 0)) + 422.5 * ((x - 0)/(47 - 0)))
#     data = data.drop(['x_loc_copy', 'y_loc_copy'], axis=1, inplace=False)
    
#     return df


# In[13]:

def get_home_vis_shots(new_tgs,home,visitor):#using shooter id & team id, get defender distances & angles
    home_id = home.teamid[0]
    visitor_id = visitor.teamid[0]
    #divide shots into those taken by home, away teams
    new_tgs['home_shot'] = new_tgs.apply(lambda x: 1 if x.TEAM_ID == home_id else 0,axis = 1)
    home_tgs = new_tgs[new_tgs['home_shot'] == 1]
    visitor_tgs = new_tgs[new_tgs['home_shot'] == 0]
    
    return home_tgs,visitor_tgs


# In[31]:

def get_shooter_loc(shooter_id,ids,locs):
    for pid,loc in zip(ids,locs):
            if shooter_id == pid:
                return loc


# In[32]:

#get shooter x, y coordinates
def get_shooter_coords(df,h_v):
    '''
    df: DataFrame
    h_v: string, either 'home' or 'visitor', indicates which df we are working with and thus which players we want to search for to get shooter
    
    returns: dataframe with two new columns which are x & y coordinate of the shooter at the time of the shot
    '''
    #long line of code here - takes player ids of each player and their coordinate, selects the one that matches shooter id and returns that coordinate
    df['shooter_x'] = df.apply(lambda x: get_shooter_loc(x.PLAYER_ID,
                                                         [x['{}_p1'.format(h_v)],x['{}_p2'.format(h_v)],x['{}_p3'.format(h_v)],x['{}_p4'.format(h_v)],x['{}_p5'.format(h_v)]],
                                                         [x['{}_p1_x'.format(h_v)],x['{}_p2_x'.format(h_v)],x['{}_p3_x'.format(h_v)],x['{}_p4_x'.format(h_v)],x['{}_p5_x'.format(h_v)]]),
                                                           axis = 1)
    
    df['shooter_y'] = df.apply(lambda x: get_shooter_loc(x.PLAYER_ID,
                                                         [x['{}_p1'.format(h_v)],x['{}_p2'.format(h_v)],x['{}_p3'.format(h_v)],x['{}_p4'.format(h_v)],x['{}_p5'.format(h_v)]],[x['{}_p1_y'.format(h_v)],
                                                         x['{}_p2_y'.format(h_v)],x['{}_p3_y'.format(h_v)],x['{}_p4_y'.format(h_v)],x['{}_p5_y'.format(h_v)]]),
                                                           axis = 1)    
    
    return df


# In[39]:

#get defender distances, angles
def get_defender_distances(df,defender,h_v):
    '''
    df: dataframe
    defender: integer, defender #
    h_v: which team *defenders* are on, either 'home' or 'visitor'
    
    returns: numpy array of distance between shooter and defender
    '''
    shooter_locs = df[['shooter_x','shooter_y']].values
    def_locs = df[['{}_p{}_x'.format(h_v,defender),'{}_p{}_y'.format(h_v,defender)]].values
    #norm of differences  = distance
    diff = shooter_locs - def_locs
    return np.linalg.norm(diff,axis = 1)

def get_defender_angles(df,defender,h_v):
    '''
    df: dataframe
    defender: integer, defender #
    h_v: which team *defenders* are on, either 'home' or 'visitor'
    
    returns: numpy array of angle between shooter and defender (in degrees)
    '''
    shooter_locs = df[['shooter_x','shooter_y']].values
    def_locs = df[['{}_p{}_x'.format(h_v,defender),'{}_p{}_y'.format(h_v,defender)]].values
    #substract shooter location from each coordinate so shooter is at the origin
    diff = def_locs - shooter_locs
    #use inverse tangent to get angle between shooter, defender
    return np.degrees(np.arctan(diff[:,1] / diff[:,0]))


# In[35]:

#add defender locs, distances to dataframe
def defender_dist_angles(df,is_home):
    '''
    df: dataframe of shots & player locs & loc of shooter
    is_home: boolean, tells us if df is home or away team
    
    returns: df with distances, angles of each defender from shooter
    '''
    if is_home:
        for i in range(1,6):
            #since we want info about defenders, if we are the home team we pass visitor to the functions here
            df['defender_{}_dist'.format(i)] = get_defender_distances(df,i,'visitor')
            df['defender_{}_angle'.format(i)] = get_defender_angles(df,i,'visitor')
    else:
        for i in range(1,6):
            #since we want info about defenders, if we are the visiting team we pass home to the functions here
            df['defender_{}_dist'.format(i)] = get_defender_distances(df,i,'home')
            df['defender_{}_angle'.format(i)] = get_defender_angles(df,i,'home')
    return df


# In[43]:

#sort defenders by distance to shooter, select top 3 to add as features
def get_closest_defenders(df):
    df['defender_prox'] = df.apply(lambda x: np.argsort([x.defender_1_dist,x.defender_2_dist,x.defender_3_dist,x.defender_4_dist,x.defender_5_dist]),axis = 1)

    #defender prox is array of defender indices (starting at 0, so add 1 for each defender)
    #also want to get angles for the 3 closest defenders
    df['1st_closest_defender_dist'] = df.apply(lambda x: x['defender_{}_dist'.format(x['defender_prox'][0] + 1)], axis = 1)
    df['1st_closest_defender_angle'] = df.apply(lambda x: x['defender_{}_angle'.format(x['defender_prox'][0] + 1)], axis = 1)

    df['2nd_closest_defender_dist'] = df.apply(lambda x: x['defender_{}_dist'.format(x['defender_prox'][1] + 1)], axis = 1)
    df['2nd_closest_defender_angle'] = df.apply(lambda x: x['defender_{}_angle'.format(x['defender_prox'][1] + 1)], axis = 1)

    df['3rd_closest_defender_dist'] = df.apply(lambda x: x['defender_{}_dist'.format(x['defender_prox'][2] + 1)], axis = 1)
    df['3rd_closest_defender_angle'] = df.apply(lambda x: x['defender_{}_angle'.format(x['defender_prox'][2] + 1)], axis = 1)

    #these are the columns we want for now
    df_final = df[['GAME_ID', 'GAME_EVENT_ID', 'PLAYER_ID', 'PLAYER_NAME',
       'TEAM_ID', 'TEAM_NAME', 'PERIOD', 'MINUTES_REMAINING',
       'SECONDS_REMAINING', 'EVENT_TYPE', 'ACTION_TYPE', 'SHOT_TYPE',
       'SHOT_ZONE_BASIC', 'SHOT_ZONE_AREA', 'SHOT_ZONE_RANGE', 'SHOT_DISTANCE',
       'LOC_X', 'LOC_Y', 'SHOT_ATTEMPTED_FLAG', 'SHOT_MADE_FLAG', 'GAME_DATE',
       'HTM', 'VTM', 'EVENTTIME', 'QUARTER', 'SHOT_TIME','visitor_name', 'visitor_id', 'home_name',
       'shooter_x','shooter_y','home_id','1st_closest_defender_dist',
       '1st_closest_defender_angle', '2nd_closest_defender_dist',
       '2nd_closest_defender_angle', '3rd_closest_defender_dist',
       '3rd_closest_defender_angle']]
    
    return df_final


# In[37]:

def gather_data(game_num):
    #get shot data
    shots_fixed = pd.read_csv("../data/shots/shots_fixed.csv")
    
    #get "raw" game data
    game = get_game("../data/{}.json".format(game_num))
    
    #get home, visitor players as dfs
    home,visitor = get_home_visitor_players(game)
    
    #get all shots from this game
    this_game_shots = get_game_shots(game,shots_fixed,int(game_num))
    
    #add moment data for each shot
    new_tgs = get_missing_shots(this_game_shots,game)
    
    #get x&y coordingates of each players
    new_tgs = get_xy(new_tgs)
    
    #seperate shots for home team and visiting team
    home_tgs,visitor_tgs = get_home_vis_shots(new_tgs,home,visitor)
    
    ##get the shooter coordinates for each shot
    home_tgs = get_shooter_coords(home_tgs,'home')
    visitor_tgs = get_shooter_coords(visitor_tgs,'visitor')
    
    #get distances, angles (to shooter) of each defender on the court
    home_tgs = defender_dist_angles(home_tgs,True)
    visitor_tgs = defender_dist_angles(visitor_tgs,False)
    
    #choose 3 closest defenders as features, remove extra column
    home_final = get_closest_defenders(home_tgs)
    visitor_final = get_closest_defenders(visitor_tgs)
    
    home_final.to_csv('../data/game_shots/{}_home.csv'.format(game_num))
    visitor_final.to_csv('../data/game_shots/{}_visitor.csv'.format(game_num))



files = glob.glob("../data/*.json")
num_files = len(files)
num_processed = 0
for f in files:
    fnum = f.split(".json")[0]
    fnum = fnum.split("data/")[1]
    print("Processing file : {}".format(fnum))
    try:
        gather_data(fnum)
        num_processed += 1
        print("Processed {}  / {} files".format(num_processed,num_files))
    except:
        print("Could not process ",fnum)

