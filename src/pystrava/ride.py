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
# pystrava.ride -- code to work with Strava Rides

import api
import athlete
from log import log

class StravaRide(object):
    """A class for working with Strava Rides"""

    def __init__(self, id):
        """Create a StravaAPI instance

        :param id: Ride ID to use
        :returns: Nothing
        """

        self.id = id
        # Define some placeholders for ride properties
        self._athlete = None
        self._elapsedTime = None
        self._startDate = None
        self._name = None
        self._distance = None
        self._movingTime = None
        self._bike = None
        self._location = None
        self._stream = None
        return

    # Put all the property stubs here.
    @property
    def athlete(self):
        if not self._athlete:
            self._get_ride_details()
        return self._athlete

    @property
    def elapsedTime(self):
        if not self._elapsedTime:
            self._get_ride_details()
        return self._elapsedTime

    @property
    def startDate(self):
        if not self._startDate:
            self._get_ride_details()
        return self._startDate

    @property
    def name(self):
        if not self._name:
            self._get_ride_details()
        return self._name

    @property
    def distance(self):
        if not self._distance:
            self._get_ride_details()
        return self._distance

    @property
    def movingTime(self):
        if not self._movingTime:
            self._get_ride_details()
        return self._movingTime

    @property
    def bike(self):
        if not self._bike:
            self._get_ride_details()
        return self._bike

    @property
    def location(self):
        if not self._location:
            self._get_ride_details()
        return self._location

    @property
    def stream(self):
        if not self._stream:
            self._get_ride_stream()
        return self._stream

    # This is something of an internal function that just populates data
    def _get_ride_details(self):
        url = api.RIDES + '/' + self.id
        resp = api.get(url)
        data = resp['ride']
        self._athlete = athlete.StravaAthlete(data['athlete']['id'])
        self._elapsedTime = data['elapsedTime']
        self._startDate = data['startDate']
        self._name = data['name']
        self._distance = data['distance']
        self._movingTime = data['movingTime']
        self._bike = data['bike']
        self._location = data['location']

    # Another internal function to populate an attribute
    def _get_ride_stream(self):
        url = api.STREAMS + self.id
        data = api.get(url)
        self._stream = data
