import requests
import json

APP_ID='Xf6kJqi4LV3lJqyNy6cv'
APP_CODE='ku2ywCt2BHba1ycKJHggzA'

here_maps_route = (
    'https://route.api.here.com/routing/7.2/calculateroute.json?'
    'waypoint0={waypoint0}&waypoint1={waypoint1}'
    '&mode=fastest%3Bcar%3Btraffic%3Aenabled'
    '&app_id={app_id}&app_code={app_code}&departure=now')

def create_geojson(l: list):
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "LineString",
                    "coordinates": l
                }
            }
        ]
    }

def create_point(l: list):
    return {
        "type": "Feature",
        "properties": {},
        "geometry": {
            "type": "Point",
            "coordinates": l
        }
    }

def heremaps_to_geojson(data: dict):
    leg = data['response']['route'][0]['leg'][0]
    startpoint = leg['start']['mappedPosition']
    startpoint = create_point([startpoint['longitude'],startpoint['latitude']])

    endpoint = leg['end']['mappedPosition']
    endpoint = create_point([endpoint['longitude'],endpoint['latitude']])

    points = []
    for i in leg['maneuver']:
        points.append([i['position']['longitude'],i['position']['latitude']])

    geojs = create_geojson(points)
    geojs['features'].append(startpoint)
    geojs['features'].append(endpoint)

    return geojs

def create_route_here_maps(startpoint, endpoint, app_id=None, token=None):
    params = {
        'waypoint0': startpoint,
        'waypoint1': endpoint,
        'app_id': app_id or APP_ID,
        'app_code': token or APP_CODE
    }
    js = requests.get(here_maps_route.format(**params)).json()
    return heremaps_to_geojson(js)
