import requests
import json
from kivy.logger import Logger
from .types import MarkerContent
from re import match

HERE_APP_ID='Xf6kJqi4LV3lJqyNy6cv'
HERE_TOKEN='ku2ywCt2BHba1ycKJHggzA'
GOOGLE_TOKEN='AIzaSyDimTjQBe9a6xTlSBTW68KRup5IwQ4p-V4'

here_maps_route = (
    'https://route.api.here.com/routing/7.2/calculateroute.json?'
    'waypoint0={waypoint0}&waypoint1={waypoint1}'
    '&mode=fastest%3Bcar%3Btraffic%3Aenabled'
    '&app_id={app_id}&app_code={token}&departure=now'
)

here_maps_search = (
    'http://autocomplete.geocoder.api.here.com/6.2/suggest.json?'
    'query={searchtext}&country={country}'
    '&app_id={app_id}&app_code={token}'
)

here_maps_geocoder = (
    'https://geocoder.api.here.com/6.2/geocode.json?'
    'locationid={locationid}&gen=8'
    '&app_id={app_id}&app_code={token}'
)

google_maps_route = (
    'https://maps.googleapis.com/maps/api/directions/json?'
    'origin={waypoint0}&destination={waypoint1}&key={token}')

google_maps_search = (
    'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?'
    'input={searchtext}&inputtype=textquery&'
    'fields=photos,formatted_address,name,opening_hours,rating&'
    'locationbias=circle:{distance}@{lat},{lon}&key={token}'
)

google_maps_search_nearby = (
    'https://maps.googleapis.com/maps/api/place/nearbysearch/json?'
    'location={lat},{lon}&radius={distance}&'
    'keyword={searchtext}&key={token}'
)

def create_geojson(l, properties={}):
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": properties,
                "geometry": {
                    "type": "LineString",
                    "coordinates": l
                }
            }
        ]
    }

def create_point(l, properties={}):
    return {
        "type": "Feature",
        "properties": properties,
        "geometry": {
            "type": "Point",
            "coordinates": l
        }
    }

def heremaps_to_geojson(data):
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
        'app_id': app_id or HERE_APP_ID,
        'token': token or HERE_TOKEN
    }
    r = requests.get(here_maps_route.format(**params))
    if r.status_code != 200:
        Logger.warning('Here maps routing: \n'+r.text)
        return
    js = r.json()
    return heremaps_to_geojson(js)

def create_route_google_maps(startpoint, endpoint, token=None):
    params = {
        'waypoint0': startpoint,
        'waypoint1': endpoint,
        'token': token or GOOGLE_TOKEN
    }
    r = requests.get(google_maps_route.format(**params))
    if r.status_code != 200:
        Logger.warning('Google maps routing: \n'+r.text)
        return
    js = r.json()
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

def create_point_here_maps(searchtext, country='VNM', app_id=None, token=None):
    params = {
        'app_id': app_id or HERE_APP_ID,
        'token': token or HERE_TOKEN
    }
    r = requests.get(here_maps_search.format(searchtext=searchtext,
                                                country=country,
                                                **params))

    if r.status_code != 200:
        Logger.warning('Here maps search: \n'+r.text)
        return
    js = r.json()
    if len(js['suggestions']) == 0:
        raise RuntimeError('No result found!')

    for i in js['suggestions']:
        locationid = i['locationId']
        r = requests.get(
                    here_maps_geocoder.format(locationid=locationid,**params))
        if r.status_code != 200:
            Logger.warning('Here maps search: \n'+r.text)
            continue
        geocode = r.json()

        lonlat = geocode['Response']['View'][0]['Result'][0]['Location']['DisplayPosition']
        yield {
                'extra_content': MarkerContent(name=i['label']),
                'lon': lonlat['Longitude'],
                'lat': lonlat['Latitude']
        }

def create_point_goodle_maps(searchtext, lon, lat, distance=5000, token=None):
    params = {
        'searchtext': searchtext,
        'distance': distance,
        'lon': lon,
        'lat': lat,
        'token': token or GOOGLE_TOKEN
    }
    r = requests.get(google_maps_search_nearby.format(**params))

    if r.status_code != 200:
        Logger.warning('Google maps search: \n'+r.text)
        return
    js = r.json()
    if len(js['results']) == 0:
        raise RuntimeError('No result found!')

    for i in js['results']:
        content = {
            'icon': i['icon'],
            'name': i['name'],
            'rating': i['rating'],
            'types': i['types'],
            'vicinity': i['vicinity']
        }
        if i.get('photos'):
            content['glink'] = match(r'^<a href="(.*)">$',
                        i['photos'][0]['html_attributions'][0]).groups()[0]
        if i.get('plus_code'):
            content['plus_code'] = i['plus_code']

        yield {
                'extra_content': MarkerContent(**content),
                'lon': i['geometry']['location']['lng'],
                'lat': i['geometry']['location']['lat']
        }
    print(content)
