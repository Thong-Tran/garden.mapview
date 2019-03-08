import sys
import traceback
from kivy.base import runTouchApp
from kivy.lang import Builder

# if __name__ == '__main__' and __package__ is None:
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import mapview
from mapview import MapMarker
from mapview.map_extra_api import create_point_goodle_maps
from kivy.factory import Factory
from kivy.logger import Logger

root = Builder.load_string("""
#:import sys sys
#:import MapSource mapview.MapSource

FloatLayout:

    MapView:
        id: maps
        lat: 10.794601
        lon: 106.672163
        zoom: 13
        map_source: MapSource()
        list_marker: []

    BoxLayout:
        size_hint: None, None
        size: dp(300), dp(40)
        pos_hint: { 'center_x': .2, 'center_y': .9}
        TextInput:
            id: search
            multiline: False
            on_text_validate: root.create_point_map(maps, search)
        Button:
            size_hint: None, 1
            width: dp(60)
            text: 'Search'
            on_release: root.create_point_map(maps, search)

<MyPoint@Bubble>:
    text: ''

    Label:
        text: root.text
        markup: True
        halign: "center"

""")

def create_point_map(root, search):
    if search.text == '':
        return

    try:
        for i in root.list_marker:
            i.detach()
        root.list_marker = []

        fi = True
        for i in create_point_goodle_maps(search.text, root.lon, root.lat):
            marker = MapMarker(**i)

            root.add_marker(marker)
            root.list_marker.append(marker)
            root.center_on(i['lat'], i['lon']) if fi else None
    except Exception as e:
        traceback.print_exc()

root.create_point_map = create_point_map

runTouchApp(root)
