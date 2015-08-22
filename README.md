# steamclean #
Python 3 script to search for and remove extraneous redistributables and files from Steam game installations.

This script will search for and remove common redistributable files for DirectX, PhysX, XNA, and VisualC++ that are not needed after game installation. These files simply take up disk space and each game will install its own version of each library and not clean up after itself.

This was tested on my own library and I saw no ill effects. If you do encounter a game that will not launch, simply verify the game files and and removed files will be replaced. This may however affect any mods installed for any games that use them.

### Usage ###
```
usage: steamclean.py [-h] [-p] [--dryrun] [--nodir] [-l LIBRARY]

Find and clean extraneous files from game directories including various
Windows redistributables.

optional arguments:
  -h, --help            show this help message and exit
  -p, --preview         Preview the list of removable data.
  --dryrun              Run script without allowing any file removal.
  --nodir               Do not clean redistributable directories.
  -l LIBRARY, --library LIBRARY
                        Additional Steam libraries to examine (comma
                        separated).
```

### Sample Commands ###

-Default run (checks only default installation path)
```
python steamclean.py
```

-Check additional library (can be comma separated)
```
python steamclean.py -l "D:\Program Files (x86)\Steam"
```

### Troubleshooting
This was tested on my own system and I noticed no issues with my games. I took care to filter out as many files as possible and to limit the scope. 

If you encounter a crash please include the stack trace information from the terminal in your bug report and any details that may aid in correcting the code.

If a file is removed that should not have been do not panic. Simply verify the game files and it will be replaced. Let me know what the file name is and what game it belongs to so I can look into fine tuning the search algorithm.

### Known issues
Input prompts will continue to be displayed with each additional input. This has no effect on the running script other than cluttering up the terminal.

Using output redirection will not allow input to be sent to the script. If redirecting output use the preview option and simply end the script after a few seconds (Ctrl+C). You can them view the file in any plain text editor and rerun the script normally.

### Upcoming features
-Better exception handling
-Script logging
-Linux support