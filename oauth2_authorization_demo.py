import logging
import os
import sys
import urlparse
import webbrowser
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import requests
import json

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

logging.basicConfig(level=logging.DEBUG)

# Store your client ID and secret in your OS's environment using these keys, or
# redefine these values here.
CLIENT_ID = 'b6s556bhm7j3qjbx5gts3p5z2jempf35'
CLIENT_SECRET = 'CBKdcuhVVerTmPJZAyMM84H2PW9MnxcNg3gNhpdFKTY'

if CLIENT_ID is None or CLIENT_SECRET is None:
    print 'Please ensure $MMF_CLIENT_ID and $MMF_CLIENT_SECRET environment ' \
          'variables are set.'
    sys.exit(1)

# As a convenience, localhost.mapmyapi.com redirects to localhost.
redirect_uri = 'http://localhost.mapmyapi.com:12345/callback'
authorize_url = 'https://www.mapmyfitness.com/v7.1/oauth2/authorize/?' \
                'client_id={0}&response_type=code&redirect_uri={1}'.format(CLIENT_ID, redirect_uri)

print 'authurl = ' + authorize_url


# Set up a basic handler for the redirect issued by the MapMyFitness 
# authorize page. For any GET request, it simply returns a 200.
# When run interactively, the request's URL will be printed out.
class AuthorizationHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200, 'OK')
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.server.path = self.path


parsed_redirect_uri = urlparse.urlparse(redirect_uri)
server_address = parsed_redirect_uri.hostname, parsed_redirect_uri.port

print 'server_address:', server_address

# NOTE: Don't go to the web browser just yet...
webbrowser.open(authorize_url)

# Start our web server. handle_request() will block until a request comes in.
httpd = HTTPServer(server_address, AuthorizationHandler)
print 'Now waiting for the user to authorize the application...'
httpd.handle_request()

# At this point a request has been handled. Let's parse its URL.
httpd.server_close()
callback_url = urlparse.urlparse(httpd.path)
authorize_code = urlparse.parse_qs(callback_url.query)['code'][0]

print 'Got an authorize code:', authorize_code

access_token_url = 'https://api.mapmyfitness.com/v7.1/oauth2/access_token/'
access_token_data = {'grant_type': 'authorization_code',
                     'client_id': CLIENT_ID,
                     'client_secret': CLIENT_SECRET,
                     'code': authorize_code}

response = requests.post(url=access_token_url,
                         data=access_token_data,
                         headers={'Api-Key': CLIENT_ID})

print 'Request details:'
print 'Content-Type:', response.request.headers['Content-Type']
print 'Request body:', response.request.body

# retrieve the access_token from the response
try:
    access_token = response.json()
    print 'Got an access token:', access_token
except:
    print 'Did not get JSON. Here is the response and content:'
    print response
    print response.content

# Use the access token to request a resource on behalf of the user
activity_type_url = 'https://api.ua.com/v7.1/activity_type/'
response = requests.get(url=activity_type_url, verify=False,
                        headers={'api-key': CLIENT_ID, 'authorization': 'Bearer %s' % access_token['access_token']})

print 'response: ', response

# Refresh a client's credentials to prevent expiration
refresh_token_url = 'https://api.ua.com/v7.1/oauth2/access_token/'
refresh_token_data = {'grant_type': 'refresh_token',
                      'client_id': CLIENT_ID,
                      'client_secret': CLIENT_SECRET,
                      'refresh_token': access_token['refresh_token']}

response = requests.post(url=refresh_token_url, data=refresh_token_data,
                         headers={'api-key': CLIENT_ID, 'authorization': 'Bearer %s' % access_token['access_token']})

print 'Request details:'
print 'Content-Type:', response.request.headers['Content-Type']
print 'Request body:', response.request.body

try:
    access_token = response.json()
    print 'Got an access token:', access_token
except:
    print 'Did not get JSON. Here is the response and content:'
    print response
    print response.content

# Attempt another request on the user's behalf using the token
refresh_token = response.json()
response = requests.get(url=activity_type_url, verify=False,
                        headers={'api-key': CLIENT_ID, 'authorization': 'Bearer %s' % access_token['access_token']})





# Custom successful request:
activity_type_url = 'https://api.ua.com/v7.1/workout/?started_after=2014&user=889861'
response = requests.get(url=activity_type_url, verify=False,
                        headers={'api-key': CLIENT_ID, 'authorization': 'Bearer %s' % access_token['access_token']})

##print the json-formatted response:
#print(response.json())

activity_type_url = 'https://api.ua.com/v7.1/workout/'

testData = json.dumps({'start_datetime': '2016-12-11T20:32:33.768863Z','name': 'Sample Workout JSON','privacy': '/v7.1/privacy_option/1/','aggregates': {'active_time_total': 10.7,'torque_min': 10.7,'power_min': 10.7,'distance_total': 10.7,'cadence_max': 10.7,'speed_max': 10.7,'speed_min': 10.7,'heartrate_min': 100,'cadence_min': 10.7,'speed_avg': 10.7,'torque_max': 10.7,'cadence_avg': 10.7,'power_avg': 10.7,'heartrate_max': 160,'power_max': 10.7,'elapsed_time_total': 10.7,'heartrate_avg': 10.7,'metabolic_energy_total': 10.7,'torque_avg': 10.7},'time_series': {'distance': [[0, 65], [1, 54], [2, 35]],'heartrate': [[0, 100], [1, 120], [2, 110]],'power': [[0, 123], [1, 120], [2, 115]],'timer_stop': [[1, 1], [3, 4], [8, 20]],'torque': [[0, 21], [1, 64], [2, 98]],'steps': [[0, 21], [1, 32], [2, 31]],'position': [[0, {'lat': 30.2672, 'lng': -97.7431, 'elevation': 5}],[1, {'lat': 30.2672, 'lng': -97.6431, 'elevation': 5.2}],[2, {'lat': 30.2672, 'lng': -97.5431, 'elevation': 5.3}]],'speed': [[0, 7.5], [1, 8.5], [2, 8.2]],'cadence': [[0, 32], [1, 36], [2, 34]]},'start_locale_timezone': 'US/Central','activity_type': '/v7.1/activity_type/11/'})

#print "dict'start_datetime' = ", testData['start_datetime']

testToken = 'Bearer %s' % access_token['access_token']

testHeaders = {'api-key': CLIENT_ID, 'authorization': testToken}

#print "dict'access_token' = ", testHeaders['authorization']

#postThis = json.dumps({'url': activity_type_url, 'verify': False, 'headers': testHeaders, 'data': testData})
#
#print postThis
#this MIGHT work. Was getting a 500, which means it might be webserver-side issue
# POST A WORKOUT

response = requests.post(url = activity_type_url, headers = testHeaders, data = testData)

#print the json-formatted response:
print(response.json())




#{
#    "start_datetime": "2016-12-12T23:32:33.768863Z",
#    "name": "Sample Workout JSON",
#    "privacy": "/v7.1/privacy_option/1/",
#    "aggregates": {
#        "active_time_total": 10.7,
#        "torque_min": 10.7,
#        "power_min": 10.7,
#        "distance_total": 10.7,
#        "cadence_max": 10.7,
#        "speed_max": 10.7,
#        "speed_min": 10.7,
#        "heartrate_min": 100,
#        "cadence_min": 10.7,
#        "speed_avg": 10.7,
#        "torque_max": 10.7,
#        "cadence_avg": 10.7,
#        "power_avg": 10.7,
#        "heartrate_max": 160,
#        "power_max": 10.7,
#        "elapsed_time_total": 10.7,
#        "heartrate_avg": 10.7,
#        "metabolic_energy_total": 10.7,
#        "torque_avg": 10.7
#    },
#    "time_series": {
#        "distance": [[0, 65], [1, 54], [2, 35]],
#        "heartrate": [[0, 100], [1, 120], [2, 110]],
#        "power": [[0, 123], [1, 120], [2, 115]],
#        "timer_stop": [[1, 1], [3, 4], [8, 20]],
#        "torque": [[0, 21], [1, 64], [2, 98]],
#        "steps": [[0, 21], [1, 32], [2, 31]],
#        "position": [
#                     [0, {"lat": 31.2672, "lng": -97.743, "elevation": 5}],
#                     [1, {"lat": 31.2672, "lng": -97.643, "elevation": 5.2}],
#                     [2, {"lat": 31.2672, "lng": -97.543, "elevation": 5.3}]
#                     ],
#                     "speed": [[0, 7.5], [1, 8.5], [2, 8.2]],
#                     "cadence": [[0, 32], [1, 36], [2, 34]]
#},
#    "start_locale_timezone": "US/Central",
#    "activity_type": "/v7.1/activity_type/11/"
#}
