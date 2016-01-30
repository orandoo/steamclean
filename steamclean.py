#!/usr/bin/env python3

# Filename:         steamclean.py
# Version:          0.7.0
# Description:      Script to find and remove extraneous files from
#                   Steam game installation directories.

from providers import libsteam, libgalaxy

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

VERSION = '0.7.0'   # Global version number as string

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


def find_redist(provider_dirs=None, customdirs=None):
    """ Create list and scan all directories for removable data. """

    providerdirs = []
    if os.name == 'nt':
        providerdirs.append(libsteam.winreg_read())
        providerdirs.append(libgalaxy.winreg_read())

    gamedirs = {}       # list of all valid game directories
    cleanable = {}      # list of all files to be removed
    customlist = []     # list to hold any provided custom directories

    if len(providerdirs) == 0:
        # For non-Windows OS prompt for directory input if needed
        while not os.path.isdir(inputdir) or not os.path.exists(inputdir):
            sclogger.warning('Invalid or missing directory at %s', inputdir)
            inputdir = os.path.abspath(
                input('Invalid or missing directory, ' +
                      'please re-enter the directory: '))
            providerdirs.append(inputdir)

    for pdir in providerdirs:
        # Validate provider installation path.
        if os.path.isdir(pdir) and 'Steam' in pdir:
            for subdir in libsteam.get_libraries(pdir):
                customlist.append(subdir)
            pdir = libsteam.fix_game_path(pdir)
            sclogger.info('Game installations located at %s', pdir)

        # Gather game directories from default path.
        sclogger.info('Checking %s', pdir)
        print('Checking %s' % (pdir))

        # ensure the path provided exists and is a valid directory
        try:
            if os.path.exists(pdir) and os.path.isdir(pdir):
                for subdir in os.listdir(pdir):
                    # if path is a directory and not already in list add it
                    if os.path.isdir(os.path.join(pdir, subdir)):
                        if subdir not in gamedirs:
                            # add new key matching game directories found
                            gamedirs[os.path.join(pdir, subdir)] = ''
        # print directory to log if it is not found or invalid
        except FileNotFoundError:
            sclogger.error('Directory %s is missing or invalid, skipping',
                           pdir)
            print('Directory %s is missing or invalid, skipping' % (pdir))

    if customdirs:
        # split list is provided via cli application as a string
        if type(customdirs) is str:
            for subdir in customdirs.lower().split(','):
                customlist.append(subdir)
        else:
            for subdir in customdirs:
                customlist.append(subdir)
    else:
        sclogger.info('No additional directories will be scanned.')

    if len(customlist) > 0:
        # Check all provided libraries.
        for subdir in customlist:
            # correct path issues and validate path
            subdir = libsteam.fix_game_path(subdir)
            # Verify customdir path exists and is a directory
            if not os.path.exists(subdir) or not os.path.isdir(subdir):
                sclogger.warning('Ignoring invalid directory at %s', subdir)
                continue

            sclogger.info('Checking additional directory at %s', subdir)
            print('Checking additional directory at %s' % (subdir))

            # build list of all valid game directories in each customdir
            if os.path.exists(subdir) and os.path.isdir(subdir):
                for dir in os.listdir(subdir):
                    libsubdir = os.path.join(subdir, dir)
                    if os.path.exists(libsubdir) and os.path.isdir(libsubdir):
                        if libsubdir not in gamedirs:
                            # add key for each located directory
                            gamedirs[libsubdir] = ''

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
                        help='Run script without allowing any file removal',
                        action='store_true')
    parser.add_argument('-d', '--dir',
                        help='Additional directories to scan '
                        '(comma separated)')
    args = parser.parse_args()

    print_header()

    if os.name == 'nt':
        cleanable = find_redist(args.dir)

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
