# filename:     libsteam.py
# description:  Collection of functions directly related to the Steam client
#               handling within steamclean.py

import providers.libproviders as libproviders

import logging
import os
import re

# module specific sublogger to avoid duplicate log entries
liblogger = logging.getLogger('steamclean.libsteam')


def winreg_read():
    """ Get Steam installation path from reading registry data.
    If unable to read registry information prompt user for input. """

    install_path = libproviders.winreg_read(r'Valve\Steam', 'InstallPath')
    if install_path is not None:
        liblogger.info('Steam installation path found at %s', install_path)
    else:
        liblogger.warn('Steam installation not found by registry check')

    return install_path


def get_libraries(steamdir):
    """ Attempt to automatically read extra Steam library directories by
        checking the libraryfolders.vdf file. """

    libfiledir = os.path.join(steamdir, 'steamapps')
    # Build the path to libraryfolders.vdf which stores configured libraries.
    libfile = os.path.abspath(os.path.join(libfiledir, 'libraryfolders.vdf'))
    # This regex checks for lines starting with the number and grabs the
    # path specified in that line by matching anything within quotes.
    libregex = re.compile('(^\t"[1-8]").*(".*")')

    try:
        libdirs = []

        liblogger.info('Attempting to read libraries from %s', libfile)
        with open(libfile) as file:
            for line in file:
                dir = libregex.search(line)
                if dir:
                    # Normalize directory path which is the second match group
                    ndir = os.path.normpath(dir.group(2))
                    liblogger.info('Library found at %s', ndir)
                    libdirs.append(ndir.strip('"'))

        # Return list of any directories found, directories are checked
        # outside of this function for validity and are ignored if invalid.
        return libdirs
    except FileNotFoundError:
        liblogger.error('Unable to find file %s', libfile, steamdir)
        print('Unable to find file %s' % (libfile, steamdir))
    except PermissionError:
        liblogger.error('Permission denied to %s', libfile)
        print('Permission denied to %s' % (libfile))


def fix_game_path(dir):
    """ Fix path to include proper directory structure if needed. """

    if 'SteamApps' not in dir:
        dir = os.path.join(dir, 'SteamApps', 'common')
    # normalize path before returning
    return os.path.abspath(dir)


def check_vdf(gamedirs):
    """ Read .vdf files for additional content for removal. """

    vdfcleanable = {}

    # get all vdf files from game directories for review
    for game in gamedirs:
        files = os.listdir(game)
        for file in files:
            if '.vdf' in file:
                gamedirs[game] = os.path.abspath(os.path.join(game, file))

    # Scrub dictionary of entries that do not have a valid .vdf file.
    cleangamedirs = {}
    for game in gamedirs:
        if gamedirs[game] != '':
            cleangamedirs[game] = gamedirs[game]

    # Substitute game path for %INSTALLDIR% within .vdf file.
    for game in cleangamedirs:
        with open(cleangamedirs[game]) as vdffile:
            try:
                for line in vdffile:
                    # Only read lines with an installation specified.
                    if 'INSTALLDIR' in line:
                        # Replace %INSTALLDIR% with path and make it valid.
                        splitline = line.split('%')
                        newline = splitline[1].replace('INSTALLDIR', game) + \
                            splitline[2][0: splitline[2].find('.') + 4]

                        # Build list of existing and valid files
                        fpath = os.path.abspath(newline).lower()
                        if os.path.isfile(fpath) and os.path.exists(fpath):
                            # Check filename to determine if it is a
                            # redistributable before adding to cleanable to
                            # ensure a required file is not removed.
                            for rc in ['setup', 'redist']:
                                if rc in fpath:
                                    vdfcleanable[fpath] = (
                                        (os.path.getsize(fpath) / 1024) / 1024)
            except UnicodeDecodeError:
                sclogger.error('Invalid characters found in file %s',
                               vdffile)
            except IndexError:
                sclogger.error('Invalid data in file %s', vdffile)

    return vdfcleanable
