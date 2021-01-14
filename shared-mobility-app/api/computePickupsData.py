import pandas as pd
import iso8601
import utils
import time

def get_date(datetime):
    """ Extract the date from a datetime object
    """
    return datetime.date()

def clean_events_data(df, start, end):
    """ Clean events data to just obtain relevant info
    """
    df = df.copy()
    df['event_time'] = df['event_time'].apply(iso8601.parse_date) # convert strings to datetime objects
    df['date'] = df['event_time'].apply(get_date).astype(str) # get date part of datetime object
    # only get the rows with event_type_reason == "user_pick_up" and event_time between 6 am and 10 pm
    # also make sure dates are between the start and end period
    df = df[(df['event_type_reason'] == "user_pick_up") & (df['event_time'] >= iso8601.parse_date(start)) & (df['event_time'] <= iso8601.parse_date(end))]
    return df[['date', 'lat', 'lng', 'tract']].reset_index(drop=True)

def count_pickups(df):
    """ Group df by tract and date and count
    """
    df = df.copy()
    return df.groupby(['tract', 'date', 'lat', 'lng']).size().reset_index(name="trips")

def compute_pickups(df_events, start, end):
    """ Compute pickups data, which is the number of trips a day within
    a lat/long region
    """
    df_events_latlng = utils.round_lat_long(df_events)
    df_events_tracts = utils.create_fake_tract(df_events_latlng)
    df_pickup_raw = clean_events_data(df_events_tracts, start, end)
    return count_pickups(df_pickup_raw)
