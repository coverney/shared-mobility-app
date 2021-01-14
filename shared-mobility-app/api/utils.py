import pandas as pd

def round_any(x, accuracy):
    """ Round x with a certain accuracy
    """
    return round(x / accuracy) * accuracy

def round_lat_long(df):
    """ Round the lat and long columns of df to hundredths place
    """
    df['lat'] = df['lat'].apply(round_any, accuracy=0.01)
    df['lng'] = df['lng'].apply(round_any, accuracy=0.01)
    return df

def create_fake_tract(df):
    """ Create fake tract number for rounded lat lng
    """
    df = df.copy()
    # get decimal portions of lat and long
    lat_dec = round_any(abs(df['lat']) % 1, 0.01)
    lng_dec = round_any(abs(df['lng']) % 1, 0.01)
    # combine the decimals
    df['tract'] = ((lat_dec * 100) + lng_dec).map('{:,.2f}'.format) # string
    return df

def undo_fake_tract(df):
    """ Undo fake tract into seperate columns again
    """
    df = df.copy()
    # re-compute decimal portions of lat and long
    lat_dec = df['tract'].astype(float).astype(int)/100.0
    lng_dec = round_any(abs(df['tract'].astype(float)) % 1, 0.01)
    # put lat/long together
    df['lat2'] = (41 + lat_dec)
    df['lng2'] = (-1*(71+lng_dec))
    return df
