#!/usr/bin/env python3
# coding: utf-8

"""Utility functions and classes for yt-dlp."""

import os
import re
import sys
import json
import contextlib
import urllib.error
import urllib.request
from datetime import datetime


def write_string(s, out=None, encoding=None):
    """Write a string to stdout or a given stream, handling encoding issues."""
    if out is None:
        out = sys.stderr
    if encoding is None:
        encoding = getattr(out, 'encoding', 'utf-8') or 'utf-8'
    if hasattr(out, 'buffer'):
        out.buffer.write(s.encode(encoding, 'ignore'))
    else:
        out.write(s)
    out.flush()


def sanitize_filename(s, restricted=False, is_id=False):
    """Sanitize a string so it can be used as a filename."""
    def replace_insane(char):
        if restricted and char in '\\|^<>"':
            return '_'
        if char == '\0':
            return ''
        if char in '/?*':
            return '_'
        return char

    s = re.sub(r'[^\w\s\-.]', replace_insane, s)
    s = re.sub(r'\s+', ' ', s).strip()
    s = s.strip('.')
    if not s:
        return '_'
    return s


def timeconvert(timestr):
    """Convert a string representation of a date/time into a Unix timestamp."""
    if not timestr:
        return None
    try:
        dt = datetime.strptime(timestr, '%Y-%m-%dT%H:%M:%S%z')
        return int(dt.timestamp())
    except (ValueError, TypeError):
        return None


def format_bytes(bytes_val):
    """Format a byte count into a human-readable string."""
    if bytes_val is None:
        return 'N/A'
    if bytes_val == 0:
        return '0B'
    units = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB']
    i = 0
    while bytes_val >= 1024 and i < len(units) - 1:
        bytes_val /= 1024.0
        i += 1
    return f'{bytes_val:.2f}{units[i]}'


def try_get(src, getter, expected_type=None):
    """Safely retrieve a value using a getter callable."""
    try:
        v = getter(src)
    except (AttributeError, KeyError, TypeError, IndexError):
        return None
    if expected_type is None or isinstance(v, expected_type):
        return v
    return None


def url_or_none(url):
    """Return the URL if it looks valid, otherwise None."""
    if not url or not isinstance(url, str):
        return None
    url = url.strip()
    if re.match(r'https?://', url):
        return url
    return None


def parse_duration(s):
    """Parse a human-readable duration string into seconds."""
    if s is None:
        return None
    s = s.strip()
    m = re.match(
        r'(?:(?P<hours>\d+):)?(?P<minutes>\d+):(?P<seconds>\d+)$', s)
    if m:
        hours = int(m.group('hours') or 0)
        minutes = int(m.group('minutes'))
        seconds = int(m.group('seconds'))
        return hours * 3600 + minutes * 60 + seconds
    m = re.match(r'(?P<value>[\d.]+)\s*(?P<unit>s|sec|m|min|h|hr)?$', s, re.I)
    if m:
        value = float(m.group('value'))
        unit = (m.group('unit') or 's').lower()
        multipliers = {'s': 1, 'sec': 1, 'm': 60, 'min': 60, 'h': 3600, 'hr': 3600}
        return int(value * multipliers.get(unit, 1))
    return None


class YtDlpError(Exception):
    """Base exception class for yt-dlp errors."""
    def __init__(self, msg=None):
        super().__init__(msg)
        self.msg = msg


class DownloadError(YtDlpError):
    """Raised when a download fails."""
    pass


class ExtractorError(YtDlpError):
    """Raised when an extractor encounters an error."""
    def __init__(self, msg, expected=False):
        super().__init__(msg)
        self.expected = expected
