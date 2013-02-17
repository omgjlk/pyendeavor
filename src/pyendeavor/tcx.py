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
# pyendeavor.tcx -- code to work with TCX formats

import xml.etree.ElementTree as ET
import os

# Some static bits that go with garmin TCX files
GARMINEXT = 'http://www.garmin.com/xmlschemas/ActivityExtension/v2'
_attribs = {
'xsi:schemaLocation': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 ' +
                      'http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd',
'xmlns:ns5': 'http://www.garmin.com/xmlschemas/ActivityGoals/v1',
'xmlns:ns4': 'http://www.garmin.com/xmlschemas/ProfileExtension/v1',
'xmlns:ns3': 'http://www.garmin.com/xmlschemas/ActivityExtension/v2',
'xmlns:ns2': 'http://www.garmin.com/xmlschemas/UserProfile/v2',
'xmlns': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2',
'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
}

# Create an indent funciton to help with pretty printing
def _indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            _indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

# Create a decorator function to make sure the xml is indented before display
def _do_indent(func):
    def wrapper(self, *args, **kwargs):
        _indent(self.root)
        return func(self, *args, **kwargs)
    return(wrapper)

class TCX(object):
    """A class to create TCX objects and manipulate them

    :param starttime: Timestamp in Garmin format for the start of the ride
    """

    def __init__(self, starttime):
        # Create a root element to use within our tree
        self.root = ET.Element(tag='TrainingCenterDatabase', attrib=_attribs)
        # Everything falls under Activities -- We don't use it after this so
        # doesn't need self.
        activites = ET.Element(tag='Activities')
        # A Biking activity is the only thing we handle now
        activity = ET.SubElement(activites, 'Activity',
                                 attrib={'sport': 'Biking'})
        activity_id = ET.SubElement(activity, 'Id')
        activity_id.text = str(starttime)
        self.lap = ET.SubElement(activity, 'Lap', {'StartTime': str(starttime)})
        self.track = ET.SubElement(self.lap, 'Track')

        # Set up some common things about laps
        intense = ET.SubElement(self.lap, 'Intensity')
        intense.text = 'Active'
        trig = ET.SubElement(self.lap, 'TriggerMehtod')
        trig.text = 'Manual'
        cals = ET.SubElement(self.lap, 'Calories')
        cals.text = '0' # Should we set this?
        
        # Put our activity block into the root
        self.root.append(activites)
        # Bundle these things up into a tree
        self.tree = ET.ElementTree(self.root)
        # Define some psuedo properties that lets us set xml data easily
        self._distance = None
        self._duration = None

    # Define some properties to set things
    @property
    def distance(self):
        """Ride distance in meters"""
        return self._distance

    @distance.setter
    def distance(self, value):
        delem = ET.SubElement(self.lap, 'DistanceMeters')
        delem.text = str(value)
        self._distance = value

    @property
    def duration(self):
        """Ride duration in seconds"""
        return self._duration

    @duration.setter
    def duration(self, value):
        delem = ET.SubElement(self.lap, 'TotalTimeSeconds')
        delem.text = str(value)
        self._duration = value

    def add_point(self, time=0, latitude=0, longitude=0, altitude=0,
                  distance=0, speed=0, heartrate=0, cadence=0):
        """Add a trackpoint to the ride

        :param time: GPS timestamp
        :param latitude: latitude degrees
        :param longitude: longitude degrees
        :param altitude: altitude meters
        :param distance: distance meters
        :param speed: speed
        :param heartrate: heartrate bpm (optional)
        :param cadence: cadence rpm (optional)
        :returns: Nothing
        """

        # Create the trackpoint element
        tp = ET.SubElement(self.track, 'Trackpoint')
        # Fill in data
        timeEP = ET.SubElement(tp, 'Time')
        timeEP.text = str(time)
        pos = ET.SubElement(tp, 'Position')
        latEP = ET.SubElement(pos, 'LatitudeDegrees')
        latEP.text = str(latitude)
        lonEP = ET.SubElement(pos, 'LongitudeDegrees')
        lonEP.text = str(longitude)
        altEP = ET.SubElement(tp, 'AltitudeMeters')
        altEP.text = str(altitude)
        distEP = ET.SubElement(tp, 'DistanceMeters')
        distEP.text = str(distance)
        extten = ET.SubElement(tp, 'Extensions')
        texten = ET.SubElement(extten, 'TPX', attrib={'xmlns': GARMINEXT})
        speedEP = ET.SubElement(texten, 'Speed')
        speedEP.text = str(speed)
        if heartrate:
            hr = ET.SubElement(tp, 'HeartRateBpm')
            hrEP = ET.SubElement(hr, 'Value')
            hrEP.text = str(heartrate)
        if cadence:
            cadEP = ET.SubElement(tp, 'Cadence')
            cadEP.text = str(cadence)

    @_do_indent
    def dump(self):
        """Dump the TCX content to stdout"""

        ET.dump(self.root)

    @_do_indent
    def write(self, path, force=False):
        """Write the tcx content to the file at path

        :param path: absolute path name to the file
        :param force: force overwrite of existing file (defaults to False)
        :returns: nothing
        """

        if os.path.exists(path) and not force:
            raise IOError('file %s exists' % path)
        # Open the file and add our header
        fileobj = open(path, 'w')
        fileobj.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        # now dump in our tcx xml
        self.tree.write(fileobj)
