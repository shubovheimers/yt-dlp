import optparse
import os
import sys


def parseOpts(overrideArguments=None):
    def _readOptions(filename_bytes, default=[]):
        try:
            optionf = open(filename_bytes)
        except IOError:
            return default
        try:
            contents = optionf.read()
            res = contents.split()
        finally:
            optionf.close()
        return res

    def _readUserConf(package_name, default=[]):
        # Look for config in standard locations
        xdg_config_home = os.environ.get('XDG_CONFIG_HOME') or os.path.expanduser('~/.config')
        userconffile = os.path.join(xdg_config_home, package_name, 'config')
        if os.path.isfile(userconffile):
            return _readOptions(userconffile, default=default)

        appdata_dir = os.environ.get('APPDATA')
        if appdata_dir:
            userconffile = os.path.join(appdata_dir, package_name, 'config')
            if os.path.isfile(userconffile):
                return _readOptions(userconffile, default=default)

        return default

    parser = optparse.OptionParser(
        usage='%prog [OPTIONS] URL [URL...]',
        conflict_handler='resolve',
    )

    general = optparse.OptionGroup(parser, 'General Options')
    general.add_option(
        '-v', '--verbose',
        action='store_true', dest='verbose', default=False,
        help='Print various debugging information',
    )
    general.add_option(
        '--no-warnings',
        dest='no_warnings', action='store_true', default=False,
        help='Ignore warnings',
    )
    general.add_option(
        '-i', '--ignore-errors',
        action='store_true', dest='ignoreerrors', default=False,
        help='Continue on download errors',
    )
    general.add_option(
        '--version',
        action='store_true', dest='version', default=False,
        help='Print program version and exit',
    )

    network = optparse.OptionGroup(parser, 'Network Options')
    network.add_option(
        '--proxy',
        dest='proxy', default=None, metavar='URL',
        help='Use the specified HTTP/HTTPS/SOCKS proxy',
    )
    network.add_option(
        '--socket-timeout',
        dest='socket_timeout', type=float, default=None, metavar='SECONDS',
        help='Time to wait before giving up, in seconds',
    )
    network.add_option(
        '--source-address',
        metavar='IP', dest='source_address', default=None,
        help='Client-side IP address to bind to',
    )

    selection = optparse.OptionGroup(parser, 'Video Selection')
    selection.add_option(
        '--playlist-start',
        dest='playliststart', metavar='NUMBER', default=1, type=int,
        help='Playlist video to start at (default is %default)',
    )
    selection.add_option(
        '--playlist-end',
        dest='playlistend', metavar='NUMBER', default=None, type=int,
        help='Playlist video to end at (default is last)',
    )
    selection.add_option(
        '--max-downloads',
        dest='max_downloads', metavar='NUMBER', type=int, default=None,
        help='Abort after downloading NUMBER files',
    )

    filesystem = optparse.OptionGroup(parser, 'Filesystem Options')
    filesystem.add_option(
        '-o', '--output',
        dest='outtmpl', metavar='TEMPLATE', default='%(title)s [%(id)s].%(ext)s',
        help='Output filename template',
    )
    filesystem.add_option(
        '-P', '--paths',
        metavar='[TYPES:]PATH', dest='paths', default=None, action='append',
        help='The paths where the files should be downloaded',
    )
    filesystem.add_option(
        '--restrict-filenames',
        action='store_true', dest='restrictfilenames', default=False,
        help='Restrict filenames to only ASCII characters',
    )

    parser.add_option_group(general)
    parser.add_option_group(network)
    parser.add_option_group(selection)
    parser.add_option_group(filesystem)

    if overrideArguments is not None:
        opts, args = parser.parse_args(overrideArguments)
    else:
        # Read config files
        userConf = _readUserConf('yt-dlp')
        argv = sys.argv[1:]
        opts, args = parser.parse_args(userConf + argv)

    return parser, opts, args
