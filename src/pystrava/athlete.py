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
# pystrava.athlete -- a python library for interfacing with Strava Athletes

import api
from log import log

class StravaAthlete(object):
    """A class for working with Strava Athletes"""

    def __init__(self, athlete_id):
        """Create a StravaAPI instance

        :param athlete_id: Athlete ID to use
        :returns: Nothing
        """

        self.athlete_id = athlete_id
        return

    # Overload the getRides method as a short cut to add in our ID
    def get_rides(self, **args):
        """Get a listing of the rides based on provided criteria.  Rides
        returned will be limited to 50.

        :param clubId: Id of the Club for which to search for member's Rides.
        :param startDate: Day on which to start search for Rides. YYYY-MM-DD
        :param endDate: Day on which to end search for Rides.
        :param startId: Return Rides with an Id greater than or equal to the startId
        :param offset: Return Rides at offset
        """

        log.debug('Calling api.get_rides with extra args: %s' % args)
        return api.get_rides(athleteId=self.athlete_id, **args)

    def get_all_rides(self, **args):
        """Get a listing of ALL the rides based on provided criteria.

        :param clubId: Id of the Club for which to search for member's Rides.
        :param startDate: Day on which to start search for Rides. YYYY-MM-DD
        :param endDate: Day on which to end search for Rides.
        :param startId: Return Rides with an Id greater than or equal to the startId
        """

        # start with an offset of 0, then crank it up by 50 each time we loop
        offset = 0
        rides = []
        while True:
            log.debug('Getting a batch of new rides in get_all_rides')
            nrides = self.get_rides(offset=offset, **args)
            if nrides:
                rides.extend(nrides)
                offset += 50
                continue
            break
        return rides