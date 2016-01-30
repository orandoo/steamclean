# filename:     libgalaxy.py
# description:  Collection of functions directly related to the GoG Galaxy
#               game client.

from providers import libproviders

import logging
import winreg

# module specific sublogger to avoid duplicate log entries
liblogger = logging.getLogger('steamclean.libgalaxy')


def winreg_read():
    """ Get GoG galaxy installation path from reading registry data.
    If unable to read registry information prompt user for input. """

    install_path = libproviders.winreg_read(r'GoG.com\GalaxyClient\settings',
                                            'libraryPath')
    liblogger.info('GoG Galaxy installation path found at %s', install_path)

    return install_path
