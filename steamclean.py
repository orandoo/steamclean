#!/usr/bin/env python3

# Filename:         steamclean.py
# Version:          0.8.1
# Description:      Script to find and remove extraneous files from
#                   Steam game installation directories.

import providers.libsteam as libsteam
import providers.libgalaxy as libgalaxy
import providers.liborigin as liborigin

from codecs import StreamReader
from datetime import datetime
from platform import machine as pm
from platform import platform as pp
import argparse
import logging
import os
import re

if os.name == 'nt':
    import winreg

VERSION = '0.8.1'   # Global version number as string

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
        sclogger.info('Current operating system: ' + pp() + ' ' + pm())
    except:
        sclogger.exception('Unknown exception raised')
        pass

    print('Starting %s' % (header))
    print('Current operating system: %s %s\n' % (pp(), pm()))


def timef(timediff):
    """ Return a formatted string of given time difference.
        timediff is of 'datetime.timedelta' type. """
    minutes, seconds = divmod(timediff.total_seconds(), 60)
    hours = 0
    while minutes >= 60:
        hours += 1
        minutes -= 60
    timestr = '%02d:%02d:%02d' % (hours, minutes, seconds)
    return timestr

def get_provider_dirs():
    """ Build a list of all provider directories that are auto discovered. """
    providerdirs = []
    if os.name == 'nt':
        providerdirs.append(libsteam.winreg_read())
        providerdirs.append(libgalaxy.winreg_read())
        providerdirs.append(liborigin.winreg_read())

    # Remove all invalid provider directories if not found via registry check
    return [p for p in providerdirs if p is not None]


def find_redist(dirlist=None):
    """ Create list and scan all directories for removable data. """

    start_time = datetime.now() # Start time of scanning

    if dirlist:
        if type(dirlist) is str:
            dirlist = [dir for dir in dirlist.lower().split(',')]
            dirlist += get_provider_dirs()
        else:
            dirlist = [dir for dir in dirlist] + get_provider_dirs()
    else:
        dirlist = get_provider_dirs()

    gamedirs = {}       # list of all valid game directories
    cleanable = {}      # list of all files to be removed

    for pdir in dirlist:
        # Validate provider installation path.
        if os.path.isdir(pdir) and 'Steam' in pdir:
            if libsteam.get_libraries(pdir):
                for subdir in libsteam.get_libraries(pdir):
                    dirlist.append(subdir)
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
        except:
            sclogger.exception('Unknown exception raised')

    else:
        sclogger.info('No additional directories will be scanned.')

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

    # Log time taken to scan 
    end_time = datetime.now()
    time_taken = timef(end_time - start_time)
    sclogger.info("Time taken to scan = %s", time_taken)
    print("Time taken to scan = %s" % time_taken)

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

    # check if confirm is empty to determine if running from gui or cli
    # only prompt if running from cli, cannot respond when running from gui
    if confirm == '':
        # Print a warning that files will be permanently deleted and
        # inform user they can exclude files with the -p option.
        print('\nWARNING: All files will be permanently deleted!\n'
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
        start_time = datetime.now() # Start time of cleanup

        removed = 0
        excluded = 0

        filecount, totalsize = print_stats(filelist)
        excludes = get_excludes()   # compiled regex pattern

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
            except:
                sclogger.exception('Unknown exception raised')

        sclogger.info('%s file(s) removed successfully', removed)
        sclogger.info('%s file(s) excluded and not removed', excluded)
        sclogger.info('%s MB saved', format(totalsize, '.2f'))
        print('\n%s file(s) removed successfully' % (removed))
        print('%s file(s) excluded and not removed' % (excluded))
        print('%s MB saved' % (format(totalsize, '.2f')))

        # Log time taken to clean 
        end_time = datetime.now()
        time_taken = timef(end_time - start_time)
        sclogger.info("Time taken to clean = %s", time_taken)
        print("Time taken to clean = %s" % time_taken)

        return filecount, totalsize

    else:
        # Return sign that no cleanup took place.
        return -1, -1


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
        start_time = datetime.now() # Start time of session.

        cleanable = find_redist(dirlist=args.dir)

        if len(cleanable) > 0:
            if args.dryrun:
                print_stats(cleanable)
            else:
                clean_data(cleanable)
        else:
            print('\nCongratulations! No files were found for removal. ')

        # Log session time 
        end_time = datetime.now()
        time_taken = timef(end_time - start_time)
        sclogger.info("Time taken by this session = %s", time_taken)
        print("Time taken by this session = %s" % time_taken)
    else:
        print('Invalid operating system detected, or not currently supported')

    input('\nPress Enter to exit...')
