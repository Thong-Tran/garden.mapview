import requests
import json

APP_ID='Xf6kJqi4LV3lJqyNy6cv'
APP_CODE='ku2ywCt2BHba1ycKJHggzA'
GOOGLE_APP_CODE='AIzaSyDimTjQBe9a6xTlSBTW68KRup5IwQ4p-V4'

here_maps_route = (
    'https://route.api.here.com/routing/7.2/calculateroute.json?'
    'waypoint0={waypoint0}&waypoint1={waypoint1}'
    '&mode=fastest%3Bcar%3Btraffic%3Aenabled'
    '&app_id={app_id}&app_code={app_code}&departure=now')

google_maps_route = (
    'https://maps.googleapis.com/maps/api/directions/json?'
    'origin={waypoint0}&destination={waypoint1}&key={app_code}')

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

def googlemaps_to_geojson(data: dict):
    raw = data['routes'][0]['overview_polyline']['points']
    points = parsePoly(raw)
    geojs = create_geojson(points)
    
    start = points[0]
    end = points[len(points) - 1]
    geojs['features'].append(create_point([start[0], start[1]]))
    geojs['features'].append(create_point([end[0], end[1]]))
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

def create_route_google_maps(startpoint, endpoint, token=None):
    params = {
        'waypoint0': startpoint,
        'waypoint1': endpoint,
        'app_code': token or GOOGLE_APP_CODE
    }
    js = requests.get(google_maps_route.format(**params)).json()
    return googlemaps_to_geojson(js)

# utils function
def parsePoly(str_input):
    poly = [] #new ArrayList<GeoPoint>();
    index = 0 
    lenE = len(str_input)  
    lat, lng = 0, 0

    while index < lenE:
        b, shift, result = None, 0, 0
        while True:
            b = ord(str_input[index]) - 63
            index += 1
            result |= (b & 0x1f) << shift
            shift += 5
            if b < 0x20:
                break

        dlat = ~(result >> 1) if (result & 1) != 0 else (result >> 1)
        lat += dlat

        shift = 0
        result = 0
        while True:
            b = ord(str_input[index]) - 63
            index += 1
            result |= (b & 0x1f) << shift
            shift += 5
            if b < 0x20:
                break
        dlng = ~(result >> 1) if (result & 1) != 0  else (result >> 1)
        lng += dlng
        # p = [lat, lng]
        p = [float(lng / 1e5), float(lat / 1e5)]
        poly.append(p)
    return poly  