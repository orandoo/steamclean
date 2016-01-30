# filename:     libproviders.py
# description:  Common functions for provider library usage.

from platform import machine as pm
import logging
import os
import winreg

liblogger = logging.getLogger('steamclean.libproviders')


def winreg_read(keypath, subkeyname):
    """ Get provider installation path from reading registry data.
    If unable to read registry information prompt user for input. """

    system_type = pm()
    regbase = 'HKEY_LOCAL_MACHINE\\'
    regkey = None

    # use architecture returned to evaluate appropriate registry key
    if system_type == 'AMD64':
        regpath = 'SOFTWARE\Wow6432Node\\' + keypath
        regopts = (winreg.KEY_WOW64_64KEY + winreg.KEY_READ)
    elif system_type == 'i386':
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
        ipath = winreg.QueryValueEx(regkey, subkeyname)[0]

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
