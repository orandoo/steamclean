# steamclean #
Python 3 script to search for delete leftover files used by Steam game installations.

On Windows systems this will remove files such as DirectX, PhysX, XNA, and VisualC++ installers which are not required after the game is launched for the first time. Each game download its own versions of these files for installation and leaves the setup files on disk rather than remove them.

While I have done my best to ensure this script operates as intended bugs will be present as in any software. In the event you encounter a bug or incorrectly removed file please let me know. Simply create an issue on the scripts GitHub page and I will address it as efficiently as possible.

*Note: If a file is incorrectly removed for a specific game simply verify the game files. While this may interfere with game mods it will reacquire the missing files.*

Please include the following when creating an issue for it to be addressed as efficiently as possible:
- Script version
- Operating system
- Full path including filename of files removed which led to issues *if applicable

There are two versions of this application, gsteamclean and steamclean. The first is the graphical version and the second is CLI. Both perform the same function and utilize the same backend code.

### Usage: gsteamclean ###

![Alt gsteamclean gui](https://github.com/evitalis/steamclean/blob/dev/screenshot.jpg)

- Click the ellipses (...) button if your default Steam directory is not found and choose it here.
- If you wish to add additonal libraries click the 'Add dir' button to select additional directory to check.
- Click the 'Scan' button to begin scanning selected directories for cleanable files.

The 'Clean all' button will remove all files displayed in the detected files list.

*Note: If you wish to exclude files simply create a file named 'excludes.txt in the same directory as this script. Include one line per item. Exclusions are not case sensitive.*

### Usage: steamclean ###
```
usage: steamclean.py [-h] [--dryrun] [-d DIR]

Find and clean extraneous files from game directories including various
Windows redistributables.

optional arguments:
  -h, --help         show this help message and exit
  --dryrun           Run script without allowing any file removal
  -d DIR, --dir DIR  Additional directories to scan (comma separated)
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
**Executable will not start**

Install either this [VisualC++ Runtime](https://download.microsoft.com/download/C/E/5/CE514EAE-78A8-4381-86E8-29108D78DBD4/VC_redist.x64.exe) or the full [Python 3 runtime](https://www.python.org/)

**Application crashes or errors**

Run the executable from a command prompt in order to see the cause of the error, or attempt to run the Python script directly.

*Note: Running the script directly does require the Python interpreter be installed*

**A particular game will not start**

Simply verify the game files using the specific provider's recommended method.

*Steam:*

1. Right click the game in your Steam client
2. Select 'Properties'
3. Navigate to the 'Local Files' tab
4. Click 'Verify integrity of game cache'

*GoG Galaxy:*

1. Select the game from the library view
2. Click the 'More' button
3. Click 'Verify/Repair' from the 'Manage...' option

### Known issues
See issues list on the application's GitHub page

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