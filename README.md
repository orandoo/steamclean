# steamclean #
Python 3 script to search for delete leftover files used by Steam game installations.

On Windows systems this will remove files such as DirectX, PhysX, XNA, and VisualC++ installers which are not required after the game is launched for the first time. Each game download its own versions of these files for installation and leaves the setup files on disk rather than remove them.

Future support is planned for Linux and Mac operating systems. If you have suggestions for files to be cleaned on these platforms and can aid in testing please let me know.

While I have done my best to ensure this script operates as intended bugs will be present as in any software. In the event you encounter a bug or incorrectly removed file please let me know. Simply create an issue on the scripts GitHub page and I will address it as efficiently as possible.

*Note: If a file is incorrectly removed for a specific game simply verify the game files. While this may interfere with game mods it will reacquire the missing files.*

Please include the following when creating an issue for it to be addressed as efficiently as possible:
- Script version
- Operating system
- Full path including filename of files removed which led to issues *if applicable

### Usage ###
```
usage: steamclean.py [-h] [--dryrun] [--nodir] [-l LIBRARY]

Find and clean extraneous files from game directories including various
Windows redistributables.

optional arguments:
  -h, --help            show this help message and exit
  --dryrun              Run script without allowing any file removal.
  --nodir               Do not clean redistributable directories.
  -l LIBRARY, --library LIBRARY
                        Additional Steam libraries to examine (comma
                        separated).
```

### Sample Commands ###

* Default run (checks only default installation path)
```
python steamclean.py
```

* Check additional library (can be comma separated)
```
python steamclean.py -l "D:\Program Files (x86)\Steam"
```

To exclude files from removal, simply create a file called excludes.txt in the same directory as this script with one line per item to exclude. Excludes are not case sensitive but must be on individual lines to be valid.

### Troubleshooting
This was tested on my own system and I noticed no issues with my games. I took care to filter out as many files as possible and to limit the scope. 

If you encounter a crash please include the stack trace information from the terminal in your bug report and any details that may aid in correcting the code.

If a file is removed that should not have been do not panic. Simply verify the game files and it will be replaced. Let me know what the file name is and what game it belongs to so I can look into fine tuning the search algorithm.

### Known issues
Input prompts will continue to be displayed with each additional input. This has no effect on the running script other than cluttering up the terminal.

Using output redirection will not allow input to be sent to the script. If redirecting output use the preview option and simply end the script after a few seconds (Ctrl+C). You can them view the file in any plain text editor and rerun the script normally.

### License

Copyright (c) 2015 evitalis

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, and/or distribute copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.