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
import tcx
from log import log
import datetime

class StravaRide(object):
    """A class for working with Strava Rides"""

    # We use this to convert from strava's time stamp to a datetime object
    _tstampformat = '%Y-%m-%dT%H:%M:%SZ'

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
        self._tcx = None

    # Put all the property stubs here.
    @property
    def athlete(self):
        """A dict representation of the athlete who performed the ride"""
        if not self._athlete:
            self._get_ride_details()
        return self._athlete

    @property
    def elapsedTime(self):
        """Total time in seconds for the ride"""
        if not self._elapsedTime:
            self._get_ride_details()
        return self._elapsedTime

    @property
    def startDate(self):
        """Timestamp in UTC of when the ride started"""
        if not self._startDate:
            self._get_ride_details()
        return self._startDate

    @property
    def name(self):
        """Name of the ride"""
        if not self._name:
            self._get_ride_details()
        return self._name

    @property
    def distance(self):
        """Distance of the ride"""
        if not self._distance:
            self._get_ride_details()
        return self._distance

    @property
    def movingTime(self):
        """Total time in seconds spent moving on the ride"""
        if not self._movingTime:
            self._get_ride_details()
        return self._movingTime

    @property
    def bike(self):
        """A dict representing bike data used for the ride"""
        if not self._bike:
            self._get_ride_details()
        return self._bike

    @property
    def location(self):
        """A string of closest known Location to the ride start"""
        if not self._location:
            self._get_ride_details()
        return self._location

    @property
    def stream(self):
        """A dict collection of data points for the ride"""
        if not self._stream:
            self._get_ride_stream()
        return self._stream

    @property
    def tcx(self):
        """A tcx representation of the ride data points"""
        if not self._tcx:
            self._stream_to_tcx()
        return self._tcx

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

    # This is a really expensive call, so much meat and awesomeness
    def _stream_to_tcx(self):
        # Get a useful time object of our start time
        starttime = datetime.datetime.strptime(self.startDate,
                                               self._tstampformat)
        # Create a new blank tcx object
        _tcx = tcx.TCX(self.startDate)
        # Set various attributes
        _tcx.distance = self.distance
        _tcx.duration = self.elapsedTime
        try:
            _tcx.maxhr = max(self.stream['heartrate'])
        except KeyError:
            # We might not have heartrate data in the stream
            pass
        # Figure out how long our stream is
        pointcount = len(self.stream['latlng'])
        # Loop through the data in our stream and create gpx points
        for snapshot in range(pointcount):
            # Save some typing by referencing bits of data by name
            args = {}
            # Convert the time which is seconds from start to a timestamp
            secs = self.stream['time'][snapshot]
            tstamp = starttime + datetime.timedelta(seconds=float(secs))
            args['time'] = tstamp
            args['latitude'] = self.stream['latlng'][snapshot][0]
            args['longitude'] = self.stream['latlng'][snapshot][1]
            args['altitude'] = self.stream['altitude'][snapshot]
            args['distance'] = self.stream['distance'][snapshot]
            args['speed'] = self.stream['velocity_smooth'][snapshot]
            # Try to get a couple optional extension data points
            try:
                args['heartrate'] = self.stream['heartrate'][snapshot]
            except KeyError:
                pass
            try:
                args['cadence'] = self.stream['cadence'][snapshot]
            except KeyError:
                pass
            # Create the point with the above gathered data
            _tcx.add_point(**args)
        self._tcx = _tcx

