#!/usr/bin/env python3
# coding: utf-8

"""yt-dlp: A feature-rich command-line audio/video downloader.

Fork of yt-dlp with additional extractors and fixes.
"""

__license__ = 'Unlicense'
__version__ = '2024.01.01'

from .YoutubeDL import YoutubeDL
from .extractor import gen_extractors, list_extractors


def main(argv=None):
    """Main entry point for yt-dlp."""
    from .options import parseOpts
    from .utils import (
        DownloadError,
        ExistingVideoReached,
        MaxDownloadsReached,
        RejectedVideoReached,
        SameFileError,
        decodeOption,
        std_headers,
    )
    import sys

    compat_opts, opts, all_urls, ydl_opts = parseOpts(argv)

    # Batch file handling
    if opts.batchfile is not None:
        try:
            if opts.batchfile == '-':
                batchfd = sys.stdin
            else:
                batchfd = open(
                    opts.batchfile, 'r',
                    encoding='utf-8', errors='ignore')
            batch_urls = [
                x.strip() for x in batchfd
                if x.strip() and not x.strip().startswith('#')]
            if opts.batchfile != '-':
                batchfd.close()
        except IOError as e:
            sys.exit('ERROR: batch file could not be read')
        all_urls = batch_urls + all_urls

    if not all_urls and not ydl_opts.get('update_self'):
        sys.exit('ERROR: no URL provided')

    with YoutubeDL(ydl_opts) as ydl:
        # Update if requested
        actual_use = all_urls or opts.load_info_filename

        try:
            retcode = ydl.download(all_urls)
        except DownloadError:
            retcode = 1
        except MaxDownloadsReached:
            ydl.to_screen('[info] Maximum number of downloads reached')
            retcode = 0
        except ExistingVideoReached:
            ydl.to_screen('[info] Encountered a video that is already in the archive, stopping due to --break-on-existing')
            retcode = 0
        except RejectedVideoReached:
            ydl.to_screen('[info] Encountered a video that did not match filter, stopping due to --break-on-reject')
            retcode = 0
        except SameFileError as e:
            ydl.report_error(f'fixed output name but more than one file to download ({e})')
            retcode = 1
        except KeyboardInterrupt:
            # Print a newline so the next shell prompt appears on a clean line
            ydl.to_screen('\nInterrupted by user, exiting...')
            retcode = 130  # Standard exit code for SIGINT

    sys.exit(retcode)


if __name__ == '__main__':
    main()
