#!/usr/bin/python
import cgi
import logging
import urllib2
import simplejson
import os
import sys

loglevel = sys.argv[1]
if loglevel == '-d':
  logging.basicConfig(level=logging.DEBUG)
  logging.debug('set logging lvl to debug')

icon_mapping = {
'tourism:picnic_site': 'tourist_picnic',
'tourism:theme_park': 'tourist_theme_park',
'tourism:viewpoint': 'tourist_view_point',
'tourism:zoo': 'tourist_zoo',
'traffic_calming:yes': 'transport_speedbump',
}

def determine_icon(tags):
  icon = 'vegan'
  for kv in icon_mapping:
    k,v = kv.split(':')
    t = tags.get(k)
    if not t:
        continue
    t = t.split(';')[0]
    if t == v:
      icon = icon_mapping[kv]
      break
  icon = icon.replace('-', '_')
  return icon

scriptdir = os.path.dirname(os.path.abspath(__file__))

f = urllib2.urlopen('http://overpass-api.de/api/interpreter?data=[out:json];(node["drink:club-mate"~"."];>;way["drink:club-mate"~"."];>;);out;')
json = simplejson.load(f)
f.close()

nodes = {}
cnt = 0

with open(scriptdir + '/js/club-mate-data.js', 'w') as f:
  logging.debug('enter file loop')
  f.write('function veganmap_populate(markers) {\n')
  for e in json['elements']:
    lat = e.get('lat', None)
    lon = e.get('lon', None)
    typ = e['type']
    tags = e.get('tags', {})
    logging.debug('Element id=%s type=%s tags=%s', e['id'], typ, tags)
    for k in tags.keys():
        tags[k] = cgi.escape(tags[k]).replace('"', '\\"')
    ide = e['id']

    if typ == 'node':
      nodes[ide] = (lat,lon)

    if typ == 'way':
      lat, lon = nodes[e['nodes'][0]] # extract coordinate of first node

    logging.debug('Element id=%s lat=%s or lon=%s', e['id'], lat, lon)

    if not lat or not lon:
      logging.warn('Element id=%s has missing lat=%s or lon=%s', e['id'], lat, lon)

    cnt += 1

    if 'name' in tags:
      name = tags['name']
    else:
      name = '%s %s' % (typ, ide)

    icon = determine_icon(tags)

    if tags.get('diet:vegetarian', '') != "" and tags.get('diet:vegan', '') == "":
      icon += "_veggie"
    else:
      icon += "_vegan"

    popup = '<b>%s</b> <a href=\\"http://openstreetmap.org/browse/%s/%s\\" target=\\"_blank\\">*</a><hr/>' % (name, typ, ide)
    if 'addr:street' in tags:
      popup += '%s %s<br/>' % (tags.get('addr:street', ''), tags.get('addr:housenumber', ''))
    if 'addr:city' in tags:
      popup += '%s %s<br/>' % (tags.get('addr:postcode', ''), tags.get('addr:city', ''))
    if 'addr:country' in tags:
      popup += '%s<br/>' % (tags.get('addr:country', ''))
    popup += '<hr/>'
    if 'contact:website' in tags:
      popup += 'website: <a href=\\"%s\\" target=\\"_blank\\">%s</a><br/>' % (tags['contact:website'], tags['contact:website'])
    elif 'website' in tags:
      popup += 'website: <a href=\\"%s\\" target=\\"_blank\\">%s</a><br/>' % (tags['website'], tags['website'])
    if 'contact:email' in tags:
      popup += 'email: <a href=\\"mailto:%s\\" target=\\"_blank\\">%s</a><br/>' % (tags['contact:email'], tags['contact:email'])
    elif 'email' in tags:
      popup += 'email: <a href=\\"mailto:%s\\" target=\\"_blank\\">%s</a><br/>' % (tags['email'], tags['email'])
    if 'contact:phone' in tags:
      popup += 'phone: %s<br/>' % (tags['contact:phone'])
    elif 'phone' in tags:
      popup += 'phone: %s<br/>' % (tags['phone'])
    f.write('  L.marker([%s, %s], {"title": "%s", icon: icon_%s}).bindPopup("%s").addTo(markers);\n' % (lat, lon, name.encode('utf-8'), icon, popup.encode('utf-8')))
  f.write('}\n')
