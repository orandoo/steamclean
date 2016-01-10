#!/usr/bin/env python3

# Filename:         steamclean.py
# Version:          0.6.0
# Description:      Script to find and remove extraneous files from
#                   Steam game installation directories.

from codecs import StreamReader
from datetime import datetime
from platform import architecture as pa
from platform import platform as pp
import argparse
import logging
import os
import re

if (os.name == 'nt'):
    import winreg

VERSION = '0.6.0'   # Global version number as string

# build sclogger and its configuration to write script data to specified log
sclogger = logging.getLogger('steamclean')
sclogger.setLevel(logging.INFO)
logformatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s',
                                 datefmt='%Y-%m-%d %H:%M:%S')
# use current date and time for log file name for clarity
timenow = datetime.now().strftime('%Y%m%d-%H%M')
fh = logging.FileHandler('steamclean_' + timenow + '.log')
fh.setFormatter(logformatter)
sclogger.addHandler(fh)


def print_header(filename=None):
    """ Clear terminal window and print script name and release date.
        This is only run if running the script file directly, built
        binaries will fail this step. """

    if not filename:
        filename = os.path.basename(__file__)

    header = filename + ' v' + VERSION

    if __name__ == '__main__':
        if os.name == 'nt':
            os.system('cls')
        elif os.name == 'posix':
            os.system('clear')

    # Attempt to write log data and skip upon exception
    try:
        sclogger.info('Starting %s', header)
        sclogger.info('Current operating system: ' + pp() + ' ' + pa()[0])
    except:
        pass

    print('Starting %s' % (header))
    print('Current operating system: %s %s\n' % (pp(), pa()[0]))


def win_reg_check():
    """ Get Steam installation path from reading registry data.
        If unable to read registry information prompt user for input. """

    arch = pa()[0]
    regbase = 'HKEY_LOCAL_MACHINE\\'
    regkey = None

    # use architecture returned to evaluate appropriate registry key
    if arch == '64bit':
        regpath = r'SOFTWARE\Wow6432Node\Valve\Steam'
        regopts = (winreg.KEY_WOW64_64KEY + winreg.KEY_READ)
    elif arch == '32bit':
        sclogger.info('32 bit operating system detected')

        regpath = r'SOFTWARE\Valve\Steam'
        regopts = winreg.KEY_READ
    else:
        sclogger.error('Unable to determine system architecture.')
        raise ValueError('ERROR: Unable to determine system architecture.')

    try:
        regkey = winreg.OpenKeyEx(winreg.HKEY_LOCAL_MACHINE, regpath, 0,
                                  regopts)
        # Save installation path value and close open registry key.
        ipath = winreg.QueryValueEx(regkey, 'InstallPath')[0]

    except PermissionError:
        sclogger.error('Unable to read registry data at %s due to insufficient \
                 privileges.', regbase + regpath)
        sclogger.error('Run this script as administrator to resolve.')
        print('Permission denied to read registry data at %s.', regpath)

        ipath = input('Please enter the Steam installation directory: ')

    finally:
        # Ensure registry key is closed after reading as applicable.
        if regkey is not None:
            sclogger.info('Registry data at %s used to determine ' +
                          'installation path', regbase + regpath)
            sclogger.info('Steam installation path found at %s', ipath)

            winreg.CloseKey(regkey)

        return ipath.strip()


def fix_game_path(dir):
    """ Fix path to include proper directory structure if needed. """

    if 'SteamApps' not in dir:
        dir = os.path.join(dir, 'SteamApps', 'common')
    # normalize path before returning
    return os.path.abspath(dir)


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

        sclogger.info('Attempting to read libraries from %s', libfile)
        with open(libfile) as file:
            for line in file:
                dir = libregex.search(line)
                if dir:
                    # Normalize directory path which is the second match group
                    ndir = os.path.normpath(dir.group(2))
                    sclogger.info('Library found at %s', ndir)
                    libdirs.append(ndir.strip('"'))

        # Return list of any directories found, directories are checked
        # outside of this function for validity and are ignored if invalid.
        return libdirs
    except FileNotFoundError:
        sclogger.error('Unable to find file %s', libfile, steamdir)
        print('Unable to find file %s' % (libfile, steamdir))
    except PermissionError:
        sclogger.error('Permission denied to %s', libfile)
        print('Permission denied to %s' % (libfile))


def find_redist(steamdir, autolib=False, nodir=False, library=None):
    """ Find all redistributable files and read .vdf files to determine
        all files which can be safely removed. Always check .vdf file
        for removable data but include standard redistributable paths. """

    gamedirs = {}   # list of all valid game directories found
    cleanable = {}  # list of all files to be removed
    liblist = []    # list to hold any provided libraries

    # validate steamdirectory or prompt for input when invalid or missing
    while not os.path.isdir(steamdir) or not os.path.exists(steamdir):
        sclogger.warning('Invalid or missing directory at %s', steamdir)
        steamdir = os.path.abspath(
            input('Invalid or missing directory, ' +
                  'please re-enter the directory: '))

    # Validate Steam installation path.
    if os.path.isdir(steamdir):
        if autolib:
            for lib in get_libraries(steamdir):
                liblist.append(lib)
        steamdir = fix_game_path(steamdir)
        sclogger.info('Game installations located at %s', steamdir)

    # Gather game directories from default path.
    sclogger.info('Checking %s', steamdir)
    print('Checking %s' % (steamdir))

    # ensure the path provided exists and is a valid directory
    try:
        if os.path.exists(steamdir) and os.path.isdir(steamdir):
            for dir in os.listdir(steamdir):
                # if path is a directory and not already in list add it
                if os.path.isdir(os.path.join(steamdir, dir)):
                    if dir not in gamedirs:
                        # add new key matching game directories found
                        gamedirs[os.path.join(steamdir, dir)] = ''
    # print directory to log if it is not found or invalid
    except FileNotFoundError:
        sclogger.error('Directory %s is missing or invalid, skipping',
                       steamdir)
        print('Directory %s is missing or invalid, skipping' % (steamdir))

    if library is not None:
        # split list is provided via cli application as a string
        if type(library) is str:
            for lib in library.lower().split(','):
                liblist.append(lib)
        else:
            for lib in library:
                liblist.append(lib)
    else:
        sclogger.info('No additional libraries provided.')

    if len(liblist) > 0:
        # Check all provided libraries.
        for lib in liblist:
            # correct path issues and validate path
            lib = fix_game_path(lib)
            # Verify library path exists and is a directory
            if not os.path.exists(lib) or not os.path.isdir(lib):
                sclogger.warning('Ignoring invalid directory at %s', lib)
                continue

            sclogger.info('Checking library at %s', lib)
            print('Checking library at %s' % (lib))

            # build list of all valid game directories in each library
            if os.path.exists(lib) and os.path.isdir(lib):
                for dir in os.listdir(lib):
                    libsubdir = os.path.join(lib, dir)
                    if os.path.exists(libsubdir) and os.path.isdir(libsubdir):
                        if libsubdir not in gamedirs:
                            # add key for each located directory
                            gamedirs[libsubdir] = ''

    # nodir option to skip cleaning redistributable subdirectories
    if not nodir:
        # build list of redist files from subdirectories when applicable
        redistfiles = []
        # check each subdirectory for matching values to determine valid files
        for gamedir in gamedirs:
            for subdir in os.listdir(gamedir):
                sdpath = os.path.abspath(os.path.join(gamedir, subdir))
                # regex for common redist subdirectory names
                dirregex = re.compile(r'(.*)(directx|redist|miles)(.*)',
                                      re.IGNORECASE)
                if dirregex.match(sdpath):
                    # build list of all subdirectories and files from
                    # root (game subdirectory) that are valid for removal
                    for (root, dirs, files) in os.walk(sdpath):
                        for file in files:
                            # build path to each found file and verify
                            # extension is a valid installation file
                            filepath = os.path.join(root, file)
                            extregex = re.compile(r'(cab|exe|msi)',
                                                  re.IGNORECASE)
                            if extregex.search(filepath):
                                if os.path.exists(filepath) and \
                                   os.path.isfile(filepath):
                                    redistfiles.append(filepath)

        # Add filename and size to cleanable list.
        for rfile in redistfiles:
            cleanable[rfile] = ((os.path.getsize(rfile) / 1024) / 1024)

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
                                    cleanable[fpath] = (
                                        (os.path.getsize(fpath) / 1024) / 1024)
            except UnicodeDecodeError:
                sclogger.error('Invalid characters found in file %s',
                               vdffile)
            except IndexError:
                sclogger.error('Invalid data in file %s', vdffile)

    # log all detected files and their size
    for file in cleanable:
        sclogger.info('File %s found with size %s MB',
                      file, format(cleanable[file], '.2f'))

    # Return the list of cleanable files and their approximate size.
    return cleanable


def get_excludes():
    """ Read lines from excludes.txt to build a list of files to ignore. """

    if os.path.exists('excludes.txt'):
        excludes = []       # list of data to exclude from excludes.txt
        excluderegex = ''   # pattern to use for regex matching

        # use StreamReader to automatically create excludes list
        with open('excludes.txt', 'r') as excludesfile:
            excludes = StreamReader.readlines(excludesfile)

        if excludes:
            # if items are excluded for the regex pattern with
            # case insensitive matches for all items
            return re.compile('|'.join(excludes), re.IGNORECASE)
    else:
        return None


def clean_data(filelist, confirm=''):
    """ Function to remove found data from installed game directories.
        Will prompt user for a list of files to exclude with the proper
        options otherwise all will be deleted."""

    filecount, totalsize = print_stats(filelist)

    excludes = get_excludes()   # compiled regex pattern

    # check if confirm is empty to determine if running from gui or cli
    # only prompt if running from cli, cannot respond when running from gui
    if confirm == '':
        # Print a warning that files will be permanantly deleted and
        # inform user they can exclude files with the -p option.
        print('\nWARNING: All files will be permanantly deleted!\n'
              'Please see the log file for specific file information.\n')
        while True:
            confirm = input('Do you wish to remove extra files [y/N]: ')
            confirm.lower()
            if confirm == '':
                break
            elif confirm != 'y' and confirm != 'n':
                continue
            else:
                break

    # Confirm removal of all found files. Print list of files not removed and
    # count of removed items.
    if confirm == 'y':
        removed = 0
        excluded = 0

        for index, file in enumerate(filelist):
            try:
                if os.path.isfile(file) and os.path.exists(file):
                    if excludes and excludes.search(file):
                        # skip removal for excluded files
                        excluded += 1
                        sclogger.info('%s excluded, skipping...', file)
                    else:
                        # only remove files which are not excluded
                        os.remove(file)
                        removed += 1
                        sclogger.info('File %s removed successfully', file)

            except FileNotFoundError:
                sclogger.error('File %s not found, skipping...', file)
                print('File %s not found, skipping.' % (file))

            except PermissionError:
                sclogger.error('Permission denied to file %s skipping...',
                               file)
                print('Permission denied to file %s skipping...' % (file))

        sclogger.info('%s file(s) removed successfully', removed)
        sclogger.info('%s file(s) excluded and not removed', excluded)
        sclogger.info('%s MB saved', format(totalsize, '.2f'))
        print('\n%s file(s) removed successfully' % (removed))
        print('%s file(s) excluded and not removed' % (excluded))
        print('%s MB saved' % (format(totalsize, '.2f')))

    return filecount, totalsize


def print_stats(cleanable):
    """ Print a report of removable files and their estimated size. """

    filecount = len(cleanable)
    totalsize = 0
    for cfile in cleanable:
        totalsize += float(cleanable[cfile])

    sclogger.info('Total number of files marked for removal: %s', filecount)
    sclogger.info('Estimated disk space saved after removal: %s MB',
                  format(totalsize, '.2f'))

    print('\nTotal number of files marked for removal: %s' % filecount)
    print('Estimated disk space saved after removal: %s MB' %
          format(totalsize, '.2f'))

    return filecount, totalsize


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Find and clean extraneous files from game directories '
                    'including various Windows redistributables.')
    parser.add_argument('--dryrun',
                        help='Run script without allowing any file removal.',
                        action='store_true')
    parser.add_argument('--nodir',
                        help='Do not clean redistributable directories.',
                        action='store_true')
    parser.add_argument('--autolib',
                        help='Attempt to auto detect Steam libraries in use.',
                        action='store_true')
    parser.add_argument('-l', '--library',
                        help='Additional Steam libraries to examine '
                        '(comma separated).')
    args = parser.parse_args()

    print_header()

    if os.name == 'nt':
        cleanable = find_redist(win_reg_check(), args.autolib, args.nodir,
                                args.library)

        if len(cleanable) > 0:
            if args.dryrun:
                print_stats(cleanable)
            else:
                clean_data(cleanable)
        else:
            print('\nCongratulations! No files were found for removal. ')
    else:
        print('Invalid operating system detected, or not currently supported')

    input('\nPress Enter to exit...')
