# steamclean
Python 3 script to search for and remove extraneous redistributables and files from Steam game installations.

This script will search for and remove common redistributable files for DirectX, PhysX, XNA, and VisualC++ that are not needed after game installation. These files simply take up disk space and each game will install its own version of each library and not clean up after itself.

### Usage
```
usage: steamclean.py [-h] [-p] [-s] [-d] [-l LIBRARY]

Find and clean extraneous files from game directories including various
Windows redistributables.

optional arguments:
  -h, --help            show this help message and exit
  -p, --preview         Preview the list of removable data.
  -s, --summary         Summary of number of files and total size.
  -d, --dirclean        Clean redistributable directories if found.
  -l LIBRARY, --library LIBRARY
                        Additional Steam libraries to examine (comma
                        separated).
```

### Known issues
Input prompts will continue to be displayed with each additional input. This has no effect on the running script other than cluttering up the terminal.

Using output redirection will not allow input to be sent to the script. If redirecting output use the preview option and simply end the script after a few seconds (Ctrl+C). You can them view the file in any plain text editor and rerun the script normally.

### Upcoming features
Better exception handling

Script logging

Linux support