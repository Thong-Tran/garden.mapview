from kivy.base import runTouchApp
import sys

from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from kivy.uix.bubble import Bubble
from kivy.uix.label import Label
from mapview import MapView, MapMarker, MapSource, MapMarkerPopup
from mapview.geojson import GeoJsonMapLayer
from mapview.utils import haversine, get_zoom_for_radius
from  mapview.create_geojson import create_route_here_maps
from  mapview.create_geojson import create_route_google_maps

# local test
# source = "/Users/vulequoc/Downloads/Test.json"
# options = {'map_source': MapSource.from_provider('here')}
# layer = GeoJsonMapLayer(source = source)

# online test
geojson = create_route_here_maps('10.784577,106.678545','10.790697,106.688480')
# geojson = create_route_google_maps('Hà Nội','TP. Hồ Chí Minh', token='AIzaSyDimTjQBe9a6xTlSBTW68KRup5IwQ4p-V4')
options = {'map_source': MapSource.from_provider('here')}
layer = GeoJsonMapLayer(geojson=geojson)


if layer.geojson:
    # try to auto center the map on the source
    lon, lat = layer.center
    options["lon"] = lon
    options["lat"] = lat
    min_lon, max_lon, min_lat, max_lat = layer.bounds
    radius = haversine(min_lon, min_lat, max_lon, max_lat)
    zoom = get_zoom_for_radius(radius)
    options["zoom"] = options['map_source'].max_zoom-2

view = MapView(**options)
view.add_layer(layer)

if layer.geojson:
    # create marker if they exists
    count = 0

    def create_marker(feature):
        global count
        geometry = feature["geometry"]
        if geometry["type"] != "Point":
            return
        lon, lat = geometry["coordinates"]
        marker = MapMarkerPopup(lon=lon, lat=lat)
        b=Bubble()
        l=Label()
        l.text=str(marker.pos)
        b.add_widget(l)
        marker.add_widget(b)
        marker.bind(pos=lambda *x: setattr(l, 'text', str(marker.pos)))
        view.add_marker(marker)
        count += 1

    layer.traverse_feature(create_marker)
    if count:
        print("Loaded {} markers".format(count))

runTouchApp(view)