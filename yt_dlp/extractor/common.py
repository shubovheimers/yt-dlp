# coding: utf-8
from __future__ import unicode_literals

import re
import json
import time

from ..utils import (
    format_bytes,
    sanitize_filename,
    write_string,
)


class InfoExtractor:
    """
    Base class for information extractors (IE).

    Information extractors are the classes that, given a URL, extract
    information about the video or audio it refers to. This information
    gets collected as a dictionary and passed to a Downloader.

    The following fields are mandatory:
        id:         Video identifier.
        title:      Video title.

    The following fields are optional:
        url:            Final video URL.
        ext:            Video filename extension.
        description:    Full video description.
        uploader:       Nick or title of the video uploader.
        upload_date:    Video upload date (YYYYMMDD).
        uploader_id:    Nickname or id of the video uploader.
        thumbnail:      Full URL to a video thumbnail image.
        duration:       Length of the video in seconds.
        view_count:     How many users have watched the video on the platform.
        like_count:     Number of positive ratings of the video.
        formats:        A list of dictionaries for each format available.
    """

    _WORKING = True
    _NETRC_MACHINE = None
    IE_NAME = None
    IE_DESC = None
    _VALID_URL = None
    _TESTS = []

    def __init__(self, downloader=None):
        """Constructor. Receives an optional downloader (Ydl instance)."""
        self._downloader = downloader

    @classmethod
    def ie_key(cls):
        """A string for getting the InfoExtractor with get_info_extractor."""
        return cls.__name__[:-2]

    @classmethod
    def suitable(cls, url):
        """Checks whether the given URL is suitable for this IE."""
        if cls._VALID_URL is None:
            return False
        return re.match(cls._VALID_URL, url) is not None

    @classmethod
    def working(cls):
        """Getter method for _WORKING."""
        return cls._WORKING

    def initialize(self):
        """Initializes an instance (authentication, etc)."""
        pass

    def extract(self, url):
        """Extracts URL information and returns it in list_infos format."""
        self.initialize()
        return self._real_extract(url)

    def _real_extract(self, url):
        """Real extraction process. Redefine in subclasses."""
        raise NotImplementedError('IE must implement _real_extract()')

    def set_downloader(self, downloader):
        """Sets a YoutubeDL instance as the downloader for this IE."""
        self._downloader = downloader

    def _download_webpage(self, url, video_id, note=None, errnote=None):
        """Return the data of the page at the given URL."""
        if note is None:
            note = 'Downloading webpage'
        if errnote is None:
            errnote = 'Unable to download webpage'
        self.to_screen('%s: %s' % (video_id, note))
        # Actual HTTP fetching would be delegated to downloader
        raise NotImplementedError('HTTP fetching not yet implemented in base IE')

    def to_screen(self, msg):
        """Print msg to screen, prefixing it with '[ie_name]'."""
        write_string('[%s] %s\n' % (self.IE_NAME or self.ie_key(), msg))

    def _search_regex(self, pattern, string, name, default=None, fatal=True, flags=0):
        """
        Perform a regex search on the given string, using the given pattern.
        Returns the first matching group. If no match is found, returns
        default if specified, or raises an error if fatal is True.
        """
        mobj = re.search(pattern, string, flags)
        if mobj:
            return next(g for g in mobj.groups() if g is not None)
        elif default is not None:
            return default
        elif fatal:
            raise Exception('Unable to extract %s' % name)
        else:
            return None

    def _html_search_regex(self, pattern, string, name, **kwargs):
        """
        Like _search_regex, but strips HTML tags and unescapes entities.
        """
        res = self._search_regex(pattern, string, name, **kwargs)
        if res:
            res = re.sub(r'<[^>]+>', '', res).strip()
        return res
