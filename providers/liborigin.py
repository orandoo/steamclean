# filename:     liborigin.py
# description:  Collection of functions directly related to the EA Origin
#               game client.

import providers.libproviders as libproviders

import logging

# module specific sublogger to avoid duplicate log entries
liblogger = logging.getLogger('steamclean.liborigin')


def winreg_read():
    """ Get GoG galaxy installation path from reading registry data.
    If unable to read registry information prompt user for input. """

    install_path = libproviders.winreg_read(r'Electronic Arts\EA Core',
                                            'EADM6InstallDir')
    if install_path is not None:
        liblogger.info('EA Origin installation path found at %s', install_path)
    else:
        liblogger.warn('EA Origin installation not found by registry check')

    return install_path
