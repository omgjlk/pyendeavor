# Copyright (c) 2013 Jesse Keating <jkeating@j2solutions.net>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# pystrava.api -- API functions


import logging
import requests

# Create a logging facility
class NullHandler(logging.Handler):
    """Class to do nothing with logging output"""
    def emit(self, record):
        pass

# This logging setup will allow clients of pystrava to handle log
# output however they want, with a default of nothing.
h = NullHandler()
log = logging.getLogger('pystrava')
log.addHandler(h)


# Set the URL -- class attribute, does not change per-instance
# Use the v1 API for now, it has more capability
APIURL = 'http://www.strava.com/api/v1'
LOGIN = '%s/authentication/login' % APIURL
RIDES = '%s/rides' % APIURL

def login(usermail, password):
    """Login to Strava to obtain a token and ID

    :param usermail: Strava user email
    :param password: Strava user password
    :returns: Auth Token string
    """

    resp = requests.post(LOGIN, data={'email': usermail,
                                           'password': password})
    # Catch this on our own someday
    resp.raise_for_status()
    data = resp.json()
    return data['token']

def get(url):
    """Issue a http get request to the provided url

    :param url: Constructed URL to GET against
    :returns: json data
    """

    log.debug('Sending GET for %s' % url)
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()

def post(url, data=None):
    """Issue an http post request to the provided url

    :param url: Constructed URL to POST against
    :param data: Optional dict to pass in the POST
    :returns: json data
    """

    log.debug('Sending POST for %s with data %s' % (url, data))
    resp = requests.post(url, data)
    resp.raise_for_status()
    return resp.json()

def get_rides(clubId=None, athleteId=None, athleteName=None,
              startDate=None, endDate=None, startId=None, offset=None):
    """Get a listing of the rides based on provided criteria.  Rides
    returned will be limited to 50.

    :param clubId: Id of the Club for which to search for member's Rides.
    :param athleteId: Id of the Athlete for which to search for Rides.
    :param athleteName: Username of the Athlete for which to search for Rides.
    :param startDate: Day on which to start search for Rides. YYYY-MM-DD
    :param endDate: Day on which to end search for Rides.
    :param startId: Return Rides with an Id greater than or equal to the startId
    :param offset: Return Rides at offset
    """

    params = locals()
    log.debug('Getting rides with params: %s' % params)
    # Build up a url chunk based on the parameters we got.
    data = '&'.join(['%s=%s' % (p, params[p]) for p in params
                     if params[p]])
    url = RIDES + '?' + data
    rides = get(url)['rides']
    return rides

def get_ride_data(rideId):
    """Get data about a specific ride

    :param id: ID (string) of the ride to fetch data from
    :returns: json data about the ride
    """

    url = RIDES + '/' + int(rideId)
    resp = get(url)
    return resp['ride']
