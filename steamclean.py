#!/usr/bin/env python3

# Filename:     steamclean.py
# Version:      0.2.2
# Release Date: 2014.02.02
# Description:  Script to find and remove extraneous files from
#               Steam game installations.

from linecache import clearcache, getline
from platform import architecture as pa
import argparse
import os

if (os.name == 'nt'):
    import winreg


def print_header():
    """ Clear terminal window and print script name and version. """

    if os.name == 'nt':
        os.system('cls')
    elif os.name == 'posix':
        os.system('clear')

    # Attempt to read filename and version from cache and print if found,
    # otherwise print no header information.
    try:
        filename = getline(__file__, 3).split(':')[1].strip()
        version = getline(__file__, 4).split(':')[1].strip()
        clearcache()

        print('%s v%s \n' % (filename, version))
    except:
        pass


def win_reg_check():
    """ Get Steam installation path from reading registry data.
        If unable to read registry information prompt user for input. """

    regkey = None

    try:
        # Open key based on architecture returned from platform.
        if '64' in pa()[0]:
            regkey = winreg.OpenKeyEx(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Wow6432Node\Valve\Steam', 0, (winreg.KEY_WOW64_64KEY + winreg.KEY_READ))
        elif '32' in pa()[0]:
            regkey = winreg.OpenKeyEx(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Valve\Steam', 0, (winreg.KEY_WOW64_64KEY + winreg.KEY_READ))
        # else block should never be reached under normal conditions.
        else:
            raise ValueError('Invalid or missing architecture.')

        # Save installation path value and close open registry key.
        ipath = winreg.QueryValueEx(regkey, 'InstallPath')[0]

    except:
        print('Unable to read registry data.')
        ipath = input('Please enter the Steam installation directory: ')

    finally:
        # Ensure key is closed if it was opened at any point in time.
        if regkey is not None:
            winreg.CloseKey(regkey)

        return ipath.strip()


def analyze_vdf(steamdir, dirclean=False, library=None):
    """ Find all .vdf files in provided locations and
    extract file locations of redistributable data. """

    sappscommon = r'\steamapps\common'

    gamedir = {}
    cleanable = {}

    # Ensure that the provided path for steamdir is valid.
    while os.path.isdir(steamdir) and 'Steam' not in steamdir:
        steamdir = os.path.abspath(input('Invalid Steam directory, please re-enter the directory: '))

    # Validate Steam installation path.
    if os.path.isdir(steamdir) and 'Steam' in steamdir:
        # Append steamapps directory if required.
        if sappscommon not in steamdir:
            steamdir += sappscommon

    # Gather game directories from default path.
    print('Checking default installation directory. Please wait...')
    for d in os.listdir(steamdir):
        if os.path.isdir(os.path.join(steamdir, d)):
            if d not in gamedir:
                gamedir[os.path.join(steamdir, d)] = ''

    if library is not None:
        # Normalize casing for case insensitivity.
        library = library.lower()

        # Verify library path exists and append games directory if nessesary.
        if os.path.isdir(library) and 'Steam' in library:
            if sappscommon not in library:
                library += sappscommon

        # Append game directories found in specified library if present.
        print('Checking library directories. Please wait...')
        if library is not None and sappscommon in library and os.path.isdir(library):
            for d in os.listdir(library):
                if os.path.isdir(os.path.join(library, d)):
                    if d not in gamedir:
                        gamedir[os.path.join(library, d)] = ''

    if dirclean:
        # Build a list of redistributable files found in common folders.
        redistfiles = []
        for game in gamedir:
            for item in os.listdir(game):
                pathlist = os.path.abspath(game + '\\' + item)
                if os.path.isdir(pathlist) and os.path.exists(pathlist):
                    # Verify the files being added are valid and exist.
                    if ('directx' in item or 'redist' in item or 'Redist' in item) and 'Miles' not in item:
                        # Check subdirectories or applicable files.
                        for (path, dirs, files) in os.walk(game + '\\' + item):
                            for file in files:
                                filepath = os.path.abspath(path + '\\' + file)
                                if os.path.isfile(filepath) and os.path.exists(filepath):
                                    redistfiles.append(filepath)

        # Add filename and size to cleanable list.
        for rfile in redistfiles:
            cleanable[rfile] = ((os.path.getsize(rfile) / 1024) / 1024)

    for game in gamedir:
        files = os.listdir(game)
        for file in files:
            if '.vdf' in file:
                gamedir[game] = os.path.abspath(game + '\\' + file)

    # Scrub dictionary of entries that do not have a valid .vdf file.
    cleangamedir = {}
    for game in gamedir:
        if gamedir[game] != '':
            cleangamedir[game] = gamedir[game]

    # Substitute game path for %INSTALLDIR% within .vdf file.
    for game in cleangamedir:
        # Use with to close files when done reading for easy cleanup.
        with open(cleangamedir[game]) as vdffile:
            for line in vdffile:
                # Only read lines with an installation specified.
                if 'INSTALLDIR' in line:
                    # Replace %INSTALLDIR% with path and make it valid.
                    splitline = line.split('%')
                    newline = splitline[1].replace('INSTALLDIR', game) + splitline[2][0: splitline[2].find('.') + 4]

                    # Sanitize path and append only existing files to clean list.
                    filepath = os.path.abspath(newline)
                    if os.path.isfile(filepath) and os.path.exists(filepath):
                        filepath = filepath.lower()
                        # Check filename to determine if it is a redistributable before adding to cleanable to ensure a required file is not removed.
                        for rc in ['setup', 'redist']:
                            if rc in filepath:
                                cleanable[filepath] = ((os.path.getsize(filepath) / 1024) / 1024)

    # Return the list of cleanable files and their approximate size.
    return cleanable


def clean_data(filelist, printlist=False):
    """ Function to remove found data from installed game directories.
        Will prompt user for a list of files to exclude with the proper options otherwise all will be deleted."""

    summary_report(filelist)
    confirm = ''
    excludes = []

    # Print a list of all files found and their index for user review.
    if printlist:
        for index, file in enumerate(filelist):
            print(index, file, '\n')

        # Request index of all files that should be excluded from deletion and ensure it is valid for the number of files present.
        if len(filelist) > 0:
            while True:
                userinput = input('Enter file number to exclude from deletion (no input to continue): ')
                if userinput != '' and int(userinput) <= len(filelist) and int(userinput) >= 0:
                    if int(userinput) not in excludes:
                        excludes.append(int(userinput))
                    continue
                else:
                    break

    # Print a warning that files will be permanantly deleted and inform user they can exclude files with the -p option.
    print('\nWARNING: All files will be permanantly deleted! If you wish to review the list of files to be removed please re-run this script with the -p option.\n')
    while True:
        confirm = input('Do you wish to remove all found files [y/N]: ').lower()
        if confirm != 'y' and confirm != 'n':
            continue
        else:
            break

    # Confirm removal of all found files. Print list of files not removed and count of removed items.
    if confirm == 'y':
        removed = 0

        for index, file in enumerate(filelist):
            if index not in excludes:
                if os.path.isfile(file) and os.path.exists(file):
                    os.remove(file)
                    removed += 1
                else:
                    print('Error removing file: %s' % (file))

        print('\n%s files successfully removed.' % (removed))


def summary_report(cleanable, printlist=False):
    """ Print a report of the number of files that can be cleaned and estimated size. """

    filecount = len(cleanable)
    totalsize = 0
    for cfile in cleanable:
        totalsize += cleanable[cfile]

    print('\nTotal number of files to be cleaned', filecount)
    print('Estimated disk space saved %s MB' % format(totalsize, '.2f'), '\n')

    if printlist:
        for cfile in cleanable:
            print('File path: %s' % cfile)
            print('File size: %s MB' % format(cleanable[cfile], '.2f'))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Find and clean unneeded files from Steam game installation directories.')
    parser.add_argument('-d', '--dirclean', help='Clean redistributable directories if found.', action='store_false')
    parser.add_argument('-l', '--library', help='Additional Steam library to examine.')
    parser.add_argument('-p', '--printlist', help='Print list of removable data in clean and summary actions.', action='store_true')
    parser.add_argument('-s', '--summary', help='Print summary of total number of files and estimated size only. Will print list of files if -p is also specified.', action='store_true')
    args = parser.parse_args()

    print_header()

    if os.name == 'nt':
        cleanable = analyze_vdf(win_reg_check(), args.dirclean, args.library)

        if len(cleanable) > 0:
            if args.summary:
                summary_report(cleanable, args.printlist)
            else:
                clean_data(cleanable, args.printlist)
        else:
            print('\nCongratulations! No files were found for removal. This script will now exit.')
    elif os.name == 'posix':
        print('No Linux support at this time. Please report files you believe can be cleaned for consideration.')
    else:
        print('Invalid operating system detected.')
