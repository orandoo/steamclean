#!/usr/bin/env python3

# Filename:         steamclean.py
# Version:          0.6.0
# Description:      Script to find and remove extraneous files from
#                   Steam game installation directories.

from providers import libsteam

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
# # use current date and time for log file name for clarity
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
            for lib in libsteam.get_libraries(steamdir):
                liblist.append(lib)
        steamdir = libsteam.fix_game_path(steamdir)
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
            lib = libsteam.fix_game_path(lib)
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

    # Check all game directories for valid .vdf files and check for additional
    # files for removal.
    cleanable.update(libsteam.check_vdf(gamedirs))

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
        ipath_steam = libsteam.winreg_read()    # Steam installation path
        cleanable = find_redist(ipath_steam, args.autolib,
                                args.nodir, args.library)

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
