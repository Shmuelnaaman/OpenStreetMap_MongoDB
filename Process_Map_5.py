
import xml.etree.ElementTree as ET
import re
import codecs
import json
from pymongo import MongoClient

files = ['map_5.osm']

"""
Your task is to wrangle the data and transform the shape of the data
into the model we mentioned earlier. The output should be a list of
dictionaries that look like this:

"""

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
CREATED = ["changeset", 'layer', "version", "timestamp", "user", "uid"]

SITE = ['amenity', 'brand', 'capacity', 'cuisine', 'denomination',
        'designation', 'dispensing', 'fee', 'historic', 'internet_access',
        'int_name', 'information', 'landuse', 'leisure', 'leader', 'military',
        'material', 'man_made', 'name', 'Name', 'natural', 'operator',
        'opening_hours', 'payment', 'population', 'place', 'religion',
        'recycling', 'stars', 'sport', 'smoking', 'shop', 'trees', 'tourism',
        'toilets', 'website']

ACCESS = ['bus', 'bridge', 'barrier', 'bicycle', 'border_type', 'boundary',
          'cycleway', 'cutting', 'entrance', 'enforcement', 'emergency',
          'electrified', 'from', 'frequency', 'foot', 'footway', 'fence_type',
          'foot', 'gauge', 'highway', 'horse', 'incline', 'junction', 'lit',
          'lanes', 'motorcar', 'motor_vehicle', 'motorcycle', 'maxspeed',
          'maxheight', 'network', 'public_transport', 'phone', 'parking',
          'park_ride', 'route', 'restriction', 'railway', 'surface', 'steps',
          'sign', 'service', 'two_sided', 'tunnel', 'tram', 'trail_visibility',
          'traffic_calming', 'tracktype', 'to', 'voltage', 'vehicle', 'width',
          'wheelchair', 'waterway']
POS = ["lat", "lon"]


def key_type(element, keys):
    if element.tag == "tag":
        if lower.search(element.attrib['k']):
            keys['lower'] += 1
        elif lower_colon.search(element.attrib['k']):
            keys['lower_colon'] += 1
        elif problemchars.search(element.attrib['k']):
            keys['problemchars'] += 1
        else:
            keys['other'] += 1
        pass
    return keys


def shape_element(element):
    creat = {}
    pos = {}
    node_refs = []
    node = {}
    others = {}
    site = {}
    access = {}
    addres = {}

    if element.tag == "node" or element.tag == "way":
        # make created, pos, type field

        for key in element.attrib.keys():
            if key in CREATED:
                creat[key] = element.attrib[key]
            elif key in POS:
                pos[key] = (float(element.attrib[key]))
                if len(pos) == 2:
                        node['pos'] = [pos['lat'], pos['lon']]
            else:
                node[key] = element.attrib[key]
        node['created'] = creat
        node['type'] = element.tag

        # procces tag field and agregate it to others, site, access
        for tag in element.iter("tag"):
                if tag.attrib['k'].split(':')[0] in SITE:
                    if len(tag.attrib['k'].split(':')) == 1:
                        site[tag.attrib['k']] = tag.attrib['v']
                        node['site'] = site

                    elif len(tag.attrib['k'].split(':')) == 2:
                        if (tag.attrib['k'].split(':')[1] ==
                            'en' or tag.attrib['k'].split(':')[1] == 'he'):
                            site[tag.attrib['k']] = tag.attrib['v']
                            node['site'] = site

                elif tag.attrib['k'].split(':')[0] in ACCESS:
                    access[tag.attrib['k'].split(':')[0]] = tag.attrib['v']
                    node['access'] = access

                if tag.attrib['k'].split(':')[0] == 'addr':
                    if len(tag.attrib['k'].split(':')) == 1:
                        addres[tag.attrib['k']] = tag.attrib['v']
                        node['addres'] = addres

                    elif len(tag.attrib['k'].split(':')) == 2:
                        addres[tag.attrib['k']] = tag.attrib['v']
                        node['addres'] = addres
                else:
                    others[tag.attrib['k']] = tag.attrib['v']
                    node['others'] = others

        # make nd field
        for nd in element.iter("nd"):
            node_refs.append(nd.attrib['ref'])
            if(len(node_refs) > 0):
                node['node_refs'] = node_refs
        return node
    else:
        return None


def process_map(file_in, pretty=False):
    # You do not need to change this file
    file_out = "{}.json".format('jeru_5')
    data = []
    ID = []
    client = MongoClient("mongodb://localhost:27017")
    db = client.examples

    # with io.open(file_out, 'a', encoding='utf8') as fo:
    with codecs.open(file_out, "a") as fo:
        # with codecs.open(file_out, "a", encoding="utf-8") as fo:

        for _, element in ET.iterparse(file_in):
            el = shape_element(element)

            if type(el) == {}:
                if el[id] in ID:
                    print el[id]
                else:
                    ID.append(el[id])
            if el:
                data.append(el)
                if pretty:
                    # fo.write(json.dumps(el,indent=2,ensure_ascii=False)+"\n")
                    fo.write(json.dumps(el, indent=2)+"\n")
                    db.JERU_5.insert(el)
                else:
                    # fo.write(json.dumps(el, ensure_ascii=False) + "\n")
                    fo.write(json.dumps(el) + "\n")
                    db.JERU_5.insert(el)
    fo.close()
    return data


def test():
    # db = client.examples
    with codecs.open('jeru.json', "w") as fo:
        fo.write(json.dumps('') + "\n")
    fo.close()
    # matching = [s for s in files if "jeru" in s]
    for file in files:
        print file
        # pprint.pprint(data)

if __name__ == "__main__":
    test()
