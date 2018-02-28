"""
The photo module contains the :class:`Photo` class, which is used to track
image objects (JPG, DNG, etc.).

.. moduleauthor:: Jaisen Mathai <jaisen@jmathai.com>
"""
from __future__ import print_function
from __future__ import absolute_import

import imghdr
import os
import re
import time
from datetime import datetime
from re import compile


from elodie import log
from elodie import constants
from .media import Media


class Photo(Media):

    """A photo object.

    :param str source: The fully qualified path to the photo file
    """

    __name__ = 'Photo'

    #: Valid extensions for photo files.
    #extensions = ('arw', 'cr2', 'dng', 'gif', 'jpeg', 'jpg', 'nef', 'rw2', 'png', 'tiff')
    extensions = ('arw', 'cr2', 'dng', 'gif', 'jpeg', 'jpg', 'nef', 'rw2', 'png', 'tiff', 'heic')

    def __init__(self, source=None):
        super(Photo, self).__init__(source)

        # We only want to parse EXIF once so we store it here
        self.exif = None

    def get_date_taken(self):
        """Get the date which the photo was taken.

        The date value returned is defined by the min() of mtime and ctime.

        :returns: time object or None for non-photo files
        """
        if(not self.is_valid()):
            return None

        source = self.source

        seconds_since_epoch = 0
        exif = self.get_exiftool_attributes()
        if exif:
            # We need to parse a string from EXIF into a timestamp.
            # EXIF DateTimeOriginal and EXIF DateTime are both stored
            #   in %Y:%m:%d %H:%M:%S format
            # we split on a space and then r':|-' -> convert to int -> .timetuple()
            #   the conversion in the local timezone
            # EXIF DateTime is already stored as a timestamp
            # Sourced from https://github.com/photo/frontend/blob/master/src/libraries/models/Photo.php#L500  # noqa
            for key in self.exif_map['date_taken']:
                try:
                    if(key in exif):
                        if(re.match('\d{4}(-|:)\d{2}(-|:)\d{2}', exif[key]) is not None):  # noqa
                            dt, tm = exif[key].split(' ')
                            dt_list = compile(r'-|:').split(dt)
                            dt_list = dt_list + compile(r'-|:').split(tm)
                            dt_list = map(int, dt_list)
                            time_tuple = datetime(*dt_list).timetuple()
                            seconds_since_epoch = time.mktime(time_tuple)
                            break
                except BaseException as e:
                    log.error(e)
                    pass

        if seconds_since_epoch == 0:
            # Check is timestamp available in filename
            try:
                timestamp = os.path.basename(source).split('-')[0]
                seconds_since_epoch = time.mktime(time.strptime(timestamp, constants.default_timestamp_definition))
            except:
                seconds_since_epoch = 0
                pass

        if seconds_since_epoch == 0:
            seconds_since_epoch = min(os.path.getmtime(source), os.path.getctime(source))  # noqa

        if not seconds_since_epoch:
            return None

        if seconds_since_epoch == 0:
            return None

        return time.gmtime(seconds_since_epoch)
        #return seconds_since_epoch

    def is_valid(self):
        """Check the file extension against valid file extensions.

        The list of valid file extensions come from self.extensions. This
        also checks whether the file is an image.

        :returns: bool
        """
        source = self.source

        # asc Hack to allow .heic files to bypass imghdr check
        if os.path.splitext(source)[1][1:].lower() in ['heic']:
            return True

        # gh-4 This checks if the source file is an image.
        # It doesn't validate against the list of supported types.
        if(imghdr.what(source) is None):
            return False

        return os.path.splitext(source)[1][1:].lower() in self.extensions
