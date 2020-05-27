import requests  # handle requests
import numpy as np

def GetVenuesForCoord(nbh_name, latitude, longitude, radius, limit):
    CLIENT_ID = 'S5YYVFLWZLBENTFBHNOS13QTIMECBPKMO3NTUFD3TWFORM2I'
    CLIENT_SECRET = 'XLFGI2K4YCRFTVT55HVVAGSDQAO2FV0PFKDFES0RZYVXJRO5'
    VERSION = '20200101'
    
    url = 'https://api.foursquare.com/v2/venues/explore?client_id={}&client_secret={}&ll={},{}&v={}&radius={}&limit={}'.format(
            CLIENT_ID,
            CLIENT_SECRET,
            latitude,
            longitude,
            VERSION,
            radius,
            limit)

    req = requests.get(url).json()
    print(req)

    try:
        response = req['response']['groups'][0]['items']
    except:
        print(req)
    finally:
        return [(nbh_name, 'quota_exceeded', np.nan, np.nan, req)]

    venues = [(
        nbh_name,
        r['venue']['name'],
        r['venue']['location']['lat'],
        r['venue']['location']['lng'],
        r['venue']['categories'][0]['name']
    ) for r in response]

    return venues