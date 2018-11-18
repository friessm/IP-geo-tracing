from flask import Flask, render_template, request, session, redirect, url_for
from flask_restful import Resource, Api
from requests import get
from scapy.all import sr1, IP, ICMP
from forms import DomainNameForm
import geojson
import json
import os

# Create Flask app instance and RESTful API
app = Flask(__name__)
api = Api(app)

app.config.from_envvar('APP_CONFIG_FILE', silent=True)

MAPBOX_ACCESS_KEY = app.config['MAPBOX_ACCESS_KEY']
IPINFO_APITOKEN = app.config['IPINFO_APITOKEN']

@app.route('/')
def index():
    return render_template(
        'index.html',
        ACCESS_KEY=MAPBOX_ACCESS_KEY
    )

def get_ip_data(ip_addr):
    """ Use the ipinfo.io API to get data on each ip address. """

    resp = get('https://ipinfo.io/{}?token={}'.format(ip_addr, IPINFO_APITOKEN))
    if resp.status_code == 200:
        content = resp.content.decode('utf-8')
        if 'bogon' not in content:
            return json.loads(content)
        else:
            return False
    else:
        print('An error occured. Status code: {}'.format(resp.status_code))

def get_lat_lng(json):
    """ Separate lng and lat from json """
    geo = str(json['loc'])
    geo_list = geo.split(',')
    lat = float(geo_list[0])
    lng = float(geo_list[1])
    return lat, lng

def to_geojson_point(json, lat, lng): 
    """ Create the feature with Point geometry. """
    point = geojson.Point((lng, lat)) # Mapbox requires lng, lat order

    properties = {}
    for key, value in json.items():
        if key != 'loc':
            properties[key] = value

    feature = geojson.Feature(geometry=point, properties=properties)
    return feature

def to_geojson_line_string(geo_coords_list):
    """ Create a feature with a LineString geometry and store all 
        lat and lng values of the ip addresses in there. Required 
        to draw a line between each hop on the map.
    """
    line_string = geojson.LineString(geo_coords_list)
    properties = {}
    feature = geojson.Feature(geometry=line_string, properties=properties)
    return feature

def trace_route(domain_name):
    """ Main function. Takes the domain name and finds all the ip addresses
        (hops) on the way to the finale destination, the domain name, using
        the traceroute logic (TTL). 
        
        Returns a geojson FeatureCollection with Point and LineString geometry
        features for drawing on the map. If trace unsuccessful, it returns False.
    """
    
    feature_list = []
    geo_coords_list = []
    
    for i in range(1, 64):
        
        try:
            pkt = IP(dst=domain_name, ttl=i)/ICMP()
        except:
            return False

        resp = sr1(pkt, verbose=0, timeout=1)

        if resp is None:
            return False
        
        ip_data = get_ip_data(resp.src)

        # Filter out bogon IP addresses
        if not ip_data:
            continue

        lat, lng = get_lat_lng(ip_data)
        ip_data_geojson = to_geojson_point(ip_data, lat, lng)
        
        # Mapbox requires lng, lat order
        geo_coords_list.append([lng, lat]) 
        feature_list.append(ip_data_geojson)

        # Checking for the ICMP echo-reply. Destination reached.
        if resp.type == 0: 
            # Create LineString feature when all lng and lat values are collected and stored in a list
            line_string_feature = to_geojson_line_string(geo_coords_list)
            feature_list.append(line_string_feature)
            return geojson.FeatureCollection(feature_list)
          

class IpMetaData(Resource):
    def post(self):
        domain_name = str(request.form['domainName'])
        form = DomainNameForm(domain_name=domain_name)

        if form.validate():
            domain_name = str(request.form['domainName'])
            ip_data = trace_route(domain_name)
            
            if ip_data == False:
                return '', 404
            return ip_data, 200

        return '', 400

api.add_resource(IpMetaData, '/domain_name')