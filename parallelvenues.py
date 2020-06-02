import requests  # handle requests
import json
import numpy as np
import concurrent.futures as cf
import time
import itertools
import pandas as pd
import geopandas
from shapely.geometry import Point

with open("./params.json", "r") as f:
    params = json.load(f)

def GetVenuesForCoord(nbh_name, latitude, longitude, radius, limit):
    CLIENT_ID = params['api']['client_id']
    CLIENT_SECRET = params['api']['client_secret']
    VERSION = params['api']['version']
    CATEGORIES = ','.join([c['id'] for c in params['api']['categories']])
    
    url = 'https://api.foursquare.com/v2/venues/search?client_id={}&client_secret={}&ll={},{}&v={}&intent=browse&categoryId={}&radius={}&limit={}'.format(
            CLIENT_ID,
            CLIENT_SECRET,
            latitude,
            longitude,
            VERSION,
            CATEGORIES,
            radius,
            limit)

    try:
        req = requests.get(url).json()
    except Exception as e:
        return [(nbh_name, str(e), 'quota_exceeded', np.nan, 'error')]
    
    try:
        venues = req['response']['venues']
    except:
        return [(nbh_name, req, 'error', np.nan, 'error')]

    venue_list = [(
        nbh_name,
        v['id'],
        v['name'],
        Point(v['location']['lng'], v['location']['lat']),
        v['categories'][0]['name']
    ) for v in venues]

    return venue_list

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
        
    venues_df = geopandas.GeoDataFrame([item for venue_lst in venue_lst for item in venue_lst])

    venues_df.columns = ['Neighbourhood',
                         'Venue ID',
                         'Venue', 
                         'geometry', 
                         'Venue Category']
    
    end = time.time()
    print('Total time for neighbourhood ', nbh_name, ':', end - start, '\n')

    return venues_df
