# filename:     libgalaxy.py
# description:  Collection of functions directly related to the GoG Galaxy
#               game client.

import providers.libproviders as libproviders

import logging

# module specific sublogger to avoid duplicate log entries
liblogger = logging.getLogger('steamclean.libgalaxy')


def winreg_read():
    """ Get GoG galaxy installation path from reading registry data.
    If unable to read registry information prompt user for input. """

    install_path = libproviders.winreg_read(r'GoG.com\GalaxyClient\settings',
                                            'libraryPath')
    if install_path is not None:
        liblogger.info('GoG Galaxy installation path found at %s',
                       install_path)
    else:
        liblogger.warn('GoG Galaxy installation not found by registry check')

    return install_path
