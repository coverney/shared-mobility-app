import pandas as pd
import iso8601
from statsmodels.distributions.empirical_distribution import ECDF
import time
import datetime
from multiprocessing import Pool, cpu_count
from functools import partial
import numpy as np

def get_date(datetime):
    """ Return the date part of a datetime object
    """
    return datetime.date()

def get_minutes(datetime):
    """ Convert time part of a datetime object into minutes
    """
    return datetime.hour*60.0+datetime.minute+datetime.second/60.0

def get_cdf_data(df, start, end):
    """ Get valid pickup data from event data
    """
    df = df.copy()
    df['event_time'] = df['event_time'].apply(iso8601.parse_date) # convert strings to datetime objects
    # only get the rows with event_type_reason == "user_pick_up" and event_time between 6 am and 10 pm
    # also make sure dates are between the start and end period
    df = df[(df['event_type_reason'] == "user_pick_up") & (df['event_time'] >= iso8601.parse_date(start)) & (df['event_time'] <= iso8601.parse_date(end))]
    df['date'] = df['event_time'].apply(get_date).astype(str) # get date part of datetime object
    df['minute'] = df['event_time'].apply(get_minutes).astype(float)
    # consider only trips that began with operating hours
    df = df[(df['minute'] >= (6*60)) & (df['minute'] < (22*60))]
    return df[['date', 'minute']].reset_index(drop=True)

def calculate_cdf(df_events, start, end):
    """ Calculate CDF of pickup times
    """
    df_cdf = get_cdf_data(df_events, start, end)
    return ECDF(df_cdf['minute'])

def get_dates(start, end):
    """ Return dictionary of dates and their start and end times
    """
    start = iso8601.parse_date(start)
    end = iso8601.parse_date(end)
    time = start
    dates = {}
    while str(time) <= str(end):
        # get date of time and see if the end of the date is in the inputted interval
        time_date = time.date()
        time_end = datetime.datetime.combine(time_date+datetime.timedelta(days=1), datetime.time(0, 0, 0), start.tzinfo)
        if str(time_end) <= str(end):
            dates[str(time_date)] = (time, time_end)
            # move on to the start of the next date
            time = time_end
        else:
            dates[str(time_date)] = (time, end)
            break
    return dates

def calculate_avail_factors_per_tract(df, ecdf, start_date, end_date):
    """ Calculate additional avail factors within a single lat/long region by date
    """
    # TODO: make this function more efficient
    df_result = pd.DataFrame(index=pd.date_range(start_date, end_date, freq='d'), columns=['tract', 'date', 'avail_perc', 'count_time', 'cdf_sum', 'lat2', 'lng2'])
    df_result['tract'] = df['tract'].values[0]
    df_result['lat2'] = df['lat2'].values[0]
    df_result['lng2'] = df['lng2'].values[0]
    df_result['date'] = df_result.index
    df_result = df_result.fillna(0)
    # go through rows and distribute avail factors into the days that fall between start and end
    for index, row in df.iterrows():
        # get dictionary of dates and their start and end times
        dates = get_dates(row['start'], row['end'])
        # go through dates and calculate avail
        for date in dates:
            time_length = (dates[date][-1] - dates[date][0]).total_seconds()/(60.0) # in minutes
            # calculate amount of time (in minutes) that at least one scooter was available
            avail_time = (row['count'] > 0) * time_length
            # calculate amount of time (in minutes) that scooters were available for in total
            count_time = row['count'] * time_length
            # calculate percent of scooter usage for intervals that were > 0.1 min and had at least one scooter available
            cdf = 0
            if (row['count'] > 0) and (row['avail'] > 0.1):
                if get_minutes(dates[date][-1]) == 0:
                    cdf = ecdf(24*60) - ecdf(get_minutes(dates[date][0]))
                else:
                    cdf = ecdf(get_minutes(dates[date][-1])) - ecdf(get_minutes(dates[date][0]))
            # update values in df_result
            df_result.loc[date, 'avail_perc'] = min(24*60, df_result.loc[date, 'avail_perc'] + avail_time)
            df_result.loc[date, 'count_time'] += count_time
            df_result.loc[date, 'cdf_sum'] = min(1, df_result.loc[date, 'cdf_sum'] + cdf)

    # calculate percent of day that at least one scooter was available
    df_result['avail_perc'] = df_result['avail_perc'] / (24*60.0) # used to be (16*60.0)
    # calculate amount of time (in days) that scooters were available for in total
    df_result['count_time'] = df_result['count_time'] / (24*60.0) # used to be (16*60.0)
    # calculate percent of daily scooter usage that occurred
    df_result['cdf_sum'] = df_result['cdf_sum'] / (ecdf(24*60)-ecdf(1*60)) # used to be (ecdf(22*60)-ecdf(6*60))
    return df_result

def calculate_avail_factors(df, ecdf, start_date, end_date, func):
    """ Group by lat/long region and then call calculate_avail_factors_per_tract (using parallelization)
    """
    df = df.copy()
    df_grouped = df.groupby('tract', sort=False, as_index=False) # group df by tract
    assert len(df_grouped) == len(set(df['tract'].values))
    # print('Number of groups:', len(df_grouped))
    # df_sub_grouped = [g[1] for g in list(df_grouped)[:3]] # for testing only
    with Pool(cpu_count()) as p:
        # ret_list = p.map(partial(func, ecdf=ecdf, start_date=start_date, end_date=end_date), [group for group in df_sub_grouped]) # for testing only
        ret_list = p.map(partial(func, ecdf=ecdf, start_date=start_date, end_date=end_date), [group for name, group in df_grouped])
    return pd.concat(ret_list)

def min_demand(trips, avail_perc, cdf_sum):
    """ Calculate adjusted trips
    """
    return min(5*trips, np.float64(trips)/avail_perc, np.float64(trips)/cdf_sum)

def merge_demand_dfs(df_pickups, df_avail):
    """ Construct demand/pickup dataframe
    """
    # fix the date columns
    df_pickups['date'] = df_pickups['date'].astype('str')
    df_avail['date'] = df_avail['date'].astype('str')
    # merge pickups and avail factors
    df_result = df_avail.merge(df_pickups, how='left', on=['date', 'tract'])
    # drop rows with no trips
    df_result = df_result[df_result['trips'].notna()]
    df_result['adj_trips'] = df_result.apply(lambda x: min_demand(x.trips, x.avail_perc, x.cdf_sum), axis=1)
    return df_result

def estimate_demand(df_events, df_pickup, df_interval, start, end):
    """ Estimate demand using availability and pickup data
    """
    ecdf = calculate_cdf(df_events, start, end)
    assert (ecdf(24*60)-ecdf(1*60)) == 1
    timer_start = time.time()
    start_date = iso8601.parse_date(min(df_interval['start'])).date()
    end_date = iso8601.parse_date(max(df_interval['end'])).date()
    df_avail = calculate_avail_factors(df_interval, ecdf, start_date, end_date, calculate_avail_factors_per_tract)
    timer_end = time.time()
    print('Elapsed time to calculate avail factors with parallelization:', (timer_end - timer_start)/60.0, 'minutes')
    return merge_demand_dfs(df_pickup, df_avail)
