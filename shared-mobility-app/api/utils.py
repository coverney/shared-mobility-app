import pandas as pd
import numpy as np
import datetime
from math import radians, cos, sin, asin, degrees, sqrt
from scipy.stats import norm
import iso8601

_AVG_EARTH_RADIUS_KM = 6371.0088
DIRECTIONS = ['up', 'down', 'left', 'right', 'left-down', 'left-up', 'right-down', 'right-up']

def sig_diff_from_zero(mean, var, alpha=0.1):
    """ Determine if a value (probability scooter is available) is significantly
        different from 0 based on it mean and variance. Returns true if it is
        and false if it's not
    """
    # Get t-statistic
    alpha = 0.1
    t_q = norm.ppf(1-alpha/2)
    # check to see whether variance==0
    # if var == 0:
    #     print(f"variance is 0 and mean is {mean}")
    if mean==0 or mean**2/var <= t_q**2:
        return False
    return True

def haversine(p1, p2):
    """ Find distance in km between two lat/lng coordinates
    """
    # unpack latitude/longitude
    lat1, lng1 = p1
    lat2, lng2 = p2

    # convert all latitudes/longitudes from decimal degrees to radians
    lat1 = radians(lat1)
    lng1 = radians(lng1)
    lat2 = radians(lat2)
    lng2 = radians(lng2)

    # calculate haversine
    lat = lat2 - lat1
    lng = lng2 - lng1
    d = sin(lat * 0.5) ** 2 + cos(lat1) * cos(lat2) * sin(lng * 0.5) ** 2

    return 2 * _AVG_EARTH_RADIUS_KM * asin(sqrt(d))

def add_distance(distance, coord, direction):
    """ Add distance to inputted coordinate in a particular direction and return new coordinate.
        Diagonal directions means we go up/down and left/right for the inputted distance

        distance: in meters
        coord: (lat, lng)
        direction: up, down, left, right, left-down, left-up, right-down, right-up
    """
    if direction not in DIRECTIONS:
        print("invalid direction inputted")
        return None
    lat, lng = coord
    distance = float(distance / 1000) # convert to KM
    if direction == "up" or direction == "down":
        delta_lat = degrees(distance/_AVG_EARTH_RADIUS_KM)
        return (lat+delta_lat, lng) if direction == "up" else (lat-delta_lat, lng)
    elif direction == "left" or direction == "right":
        numerator = sin(distance / (2 * _AVG_EARTH_RADIUS_KM))
        denominator = cos(radians(lat))
        delta_lng = degrees(2 * asin(numerator/denominator))
        return (lat, lng-delta_lng) if direction == "left" else (lat, lng+delta_lng)
    else:
        # find new lat first
        delta_lat = degrees(distance/_AVG_EARTH_RADIUS_KM)
        lat2 = lat+delta_lat if "up" in direction else lat-delta_lat
        # find delta lng using lat2
        numerator = sin(distance / (2 * _AVG_EARTH_RADIUS_KM))
        denominator = cos(radians(lat2))
        delta_lng = degrees(2 * asin(numerator/denominator))
        return (lat2, lng-delta_lng) if "left" in direction else (lat2, lng+delta_lng)

def remove_time_zone(time_stamp):
    """ Remove utc offset from time zone within time_stamp
    """
    return str(iso8601.parse_date(time_stamp).replace(tzinfo=datetime.timezone.utc))

def clean_locations_data(df, start, end):
    """ Prepare locations data to process
    """
    df = df.copy()
    df = df.dropna() # remove Nans
    df = df[(df['vehicle_status'] == "available") & (df['provider'] != "JUMP")] # select providers that aren't jump and are available
    df = df.drop(['provider', 'vehicle_status', 'vehicle_status_reason', 'device_type', 'areas'], axis=1) # remove unneeded columns
    df = df[((df['start_time'] >= start) & (df['start_time'] <= end)) |
            ((df['end_time'] >= start) & (df['end_time'] <= end))] # filter out times out of the inputted range
    df_subset = df.drop(['start_time', 'end_time'], axis=1) # drop start_time and end_time
    # duplicate the dataframe because we are separating the start and end times
    df_repeated_subset = pd.DataFrame(np.repeat(df_subset.values, 2, axis=0))
    df_repeated_subset.columns = df_subset.columns
    df_repeated_subset['time'] = df[['start_time', 'end_time']].stack().reset_index(level=[0,1], drop=True) # stack the start and end time into one column
    # df_repeated_subset['time'] = df_repeated_subset['time'].apply(remove_time_zone)
    df_repeated_subset['time_type'] = pd.Series(['start_time', 'end_time']*int(df_repeated_subset.shape[0]/2)) # create time_type column
    return df_repeated_subset

def clean_events_data(df, start, end):
    """ Clean events data to just obtain relevant info
    """
    df = df.copy()
    df['time'] = df['event_time']
    # df['time'] = df['event_time'].apply(remove_time_zone)
    df['time_type'] = 'trip'
    # only get the rows with event_type_reason == "user_pick_up" and event_time between 6 am and 10 pm
    # also make sure dates are between the start and end period
    df = df[(df['event_type_reason'] == "user_pick_up") & (df['time'] >= start) & (df['time'] <= end)]
    return df[['lat', 'lng', 'time', 'time_type']].reset_index(drop=True)

def get_relevant_demand_cols(df_demand):
    """ Returns the subset of df_demand that we want to save to a CSV
        file if the user clicks on the download data button
    """
    # select for cols we want
    df = df_demand[["date", "left_lng", "right_lng", "lower_lat",
                            "upper_lat", "avail_count", "avail_mins",
                            "trips", "prob_scooter_avail", "adj_trips"]]
    return df

def is_valid_df_demand(df_demand):
    """ Check to make sure df_demand is valid in terms of its columns
    """
    cols = ["date", "left_lng", "right_lng", "lower_lat", "upper_lat",
            "avail_count", "avail_mins", "trips", "prob_scooter_avail", "adj_trips"]
    for col in cols:
        if col not in df_demand.columns:
            return False
    return True
