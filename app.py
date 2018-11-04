from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from requests import get
from scapy.all import sr1, IP, ICMP
from forms import HostNameForm
import geojson
import json
import os

app = Flask(__name__)

# TODO: Rename file to 'app.py' and html file to 'index.html'

app.config.from_envvar('APP_CONFIG_FILE', silent=True)
app.secret_key = app.config['SECRET_KEY'] # TODO: Do I need a secret key? If not, get rid of 'session' in import
MAPBOX_ACCESS_KEY = app.config['MAPBOX_ACCESS_KEY']
IPINFO_APITOKEN = app.config['IPINFO_APITOKEN']

# print(app.config['SECRET_KEY'])

def get_ip_data(ip_addr):
    # TODO: get full API response: https://ipinfo.io/developers/responses#full-response
    # TODO: Ensure that everything fails gracefully
    resp = get('https://ipinfo.io/{}?token={}'.format(ip_addr, IPINFO_APITOKEN))
    if resp.status_code == 200:
        content = resp.content.decode('utf-8')
        print(content)
        if 'bogon' not in content:
            return json.loads(content)
        else:
            return 'bogon'
    else:
        print('An error occured. Status code: {}'.format(resp.status_code))

def get_lat_lng(json):
    # Separate lng and lat from json
    geo = str(json['loc'])
    geo_list = geo.split(',')
    lat = float(geo_list[0])
    lng = float(geo_list[1])
    return lat, lng

def to_geojson_point(json, lat, lng): 
    # TODO: This actually includes the lat & lng in the properties. This code should be re-written. Maybe use a class?
    
    # Create the feature with Point geometry
    point = geojson.Point((lng, lat)) # Mapbox requires lng, lat order
    # TODO: Use list comprehension instead (looks cooler)
    properties = {}
    for key, value in json.items():
        if key != 'loc':
            properties[key] = value
    feature = geojson.Feature(geometry=point, properties=properties)
    return feature

def to_geojson_line_string(geo_coords_list):
    line_string = geojson.LineString(geo_coords_list)
    properties = {}
    feature = geojson.Feature(geometry=line_string, properties=properties)
    return feature

def trace_route(hostname):
    # TODO: return FeatureCollection even if the signal is lost and the final destination never reached
    
    feature_list = []
    geo_coords_list = []
    
    for i in range(1, 64):
        pkt = IP(dst=hostname, ttl=i)/ICMP()
        resp = sr1(pkt, verbose=0, timeout=1)
        print(resp.src)
        if resp is None:
            print('resp is None: {}'.format(resp))
            break
        
        ip_data = get_ip_data(resp.src)
        print(ip_data)

        # Filter out bogon IP addresses
        if ip_data == 'bogon':
            continue
        lat, lng = get_lat_lng(ip_data)
        ip_data_geojson = to_geojson_point(ip_data, lat, lng)
        geo_coords_list.append([lng, lat]) # Mapbox requires lng, lat order
        feature_list.append(ip_data_geojson)

        # Checking for the ICMP echo-reply.
        if resp.type == 0: 
            # Dst reached
            print('Dst reached: {}'.format(resp.src))

            # Create LineString feature when all lng and lat values are collected and stored in a list
            line_string_feature = to_geojson_line_string(geo_coords_list)
            feature_list.append(line_string_feature)
            return geojson.FeatureCollection(feature_list)
          

@app.route('/')
def index():
    return render_template(
        'mapbox.html',
        ACCESS_KEY=MAPBOX_ACCESS_KEY
    )

# TODO: Rewrite this as an REST API
@app.route('/hostname', methods=['POST'])
def data():

    # TODO: Add proper input validation
    form = HostNameForm(request.form)
    if form.validate():
        hostname = str(request.form['hostname'])
        ip_data = trace_route(hostname)
        return jsonify(ip_data)

    # TODO: Handle this case better
    print('failed')
    return ''