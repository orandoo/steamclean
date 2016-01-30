# filename:     libproviders.py
# description:  Common functions for provider library usage.

from platform import architecture as pa
import logging
import os
import winreg

liblogger = logging.getLogger('steamclean.libproviders')

def winreg_read(keypath):
    """ Get provider installation path from reading registry data.
    If unable to read registry information prompt user for input. """

    arch = pa()[0]
    regbase = 'HKEY_LOCAL_MACHINE\\'
    regkey = None

    # use architecture returned to evaluate appropriate registry key
    if arch == '64bit':
        regpath =  'SOFTWARE\Wow6432Node\\' + keypath
        #regpath = r'SOFTWARE\Wow6432Node\Valve\Steam'
        regopts = (winreg.KEY_WOW64_64KEY + winreg.KEY_READ)
    elif arch == '32bit':
        liblogger.info('32 bit operating system detected')

        regpath = 'SOFTWARE\\' + keypath
        regopts = winreg.KEY_READ
    else:
        liblogger.error('Unable to determine system architecture.')
        raise ValueError('ERROR: Unable to determine system architecture.')

    try:
        regkey = winreg.OpenKeyEx(winreg.HKEY_LOCAL_MACHINE, regpath, 0,
                                  regopts)
        # Save installation path value and close open registry key.
        ipath = winreg.QueryValueEx(regkey, 'InstallPath')[0]

    except PermissionError:
        liblogger.error('Permission denied to read registry key',
                        regbase + regpath)
        liblogger.error('Run this script as administrator to resolve.')
        print('Permission denied to read registry data at %s.', regpath)

    finally:
        # Ensure registry key is closed after reading as applicable.
        if regkey is not None:
            liblogger.info('Registry data at %s used to determine ' +
                           'installation path', regbase + regpath)

            winreg.CloseKey(regkey)

        installpath = os.path.abspath(ipath.strip())
        return installpath