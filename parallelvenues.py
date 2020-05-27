import requests  # handle requests
import json
import numpy as np
import concurrent.futures as cf
import time
import itertools
import pandas as pd

with open("./params.json", "r") as f:
    params = json.load(f)

def GetVenuesForCoord(nbh_name, latitude, longitude, radius, limit):
    CLIENT_ID = params['API_PARAMS']['CLIENT_ID']
    CLIENT_SECRET = params['API_PARAMS']['CLIENT_SECRET']
    VERSION = params['API_PARAMS']['VERSION']
    
    url = 'https://api.foursquare.com/v2/venues/explore?client_id={}&client_secret={}&ll={},{}&v={}&radius={}&limit={}'.format(
            CLIENT_ID,
            CLIENT_SECRET,
            latitude,
            longitude,
            VERSION,
            radius,
            limit)

    try:
        req = requests.get(url).json()
        response = req['response']['groups'][0]['items']
    except:
        return [(nbh_name, 'NA', 'quota_exceeded', latitude, longitude, 'error')]

    venues = [(
        nbh_name,
        r['venue']['id'],
        r['venue']['name'],
        r['venue']['location']['lat'],
        r['venue']['location']['lng'],
        r['venue']['categories'][0]['name']
    ) for r in response]

    return venues

def GetVenuesForNbh(nbh_name, latitudes, longitudes, radius, max_threads, limit=100):
    start = time.time()

    nbh_names = []
    lats = []
    lngs = []
    radii = []
    limits = []
    for nbh, lat, lng, r in zip(nbh_name, latitudes, longitudes, radius):
        nbh_names.extend([nbh] * len(lat))
        lats.extend(lat)
        lngs.extend(lng)
        radii.extend([r] * len(lat))
        limits.extend([limit] * len(lat))
    
    # parallelize API calls to improve run time
    with cf.ThreadPoolExecutor(max_workers=max_threads) as pool:
        venue_lst = list(pool.map(GetVenuesForCoord, nbh_names, lats, lngs, radii, limits))
        
    venues_df = pd.DataFrame([item for venue_lst in venue_lst for item in venue_lst])

    venues_df.columns = ['Neighbourhood',
                         'Venue ID',
                         'Venue', 
                         'Venue Latitude', 
                         'Venue Longitude', 
                         'Venue Category']
    
    end = time.time()
    print('Total time for neighbourhood ', nbh_name, ':', end - start, '\n')

    return venues_df
