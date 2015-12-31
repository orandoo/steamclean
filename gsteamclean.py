from tkinter import *
from tkinter import filedialog
from tkinter import ttk

from sys import path as syspath


class SdirFrame:
    ''' Top UI frame to hold data for the default Steam directory. '''

    def __init__(self, parent):
        self.sdir_frame = ttk.Frame(parent, padding=4)

        self.sdir_label = ttk.Label(self.sdir_frame, text='Steam directory:')
        self.sdir_label.grid(column=0, row=0, padx=4, sticky='w')

        # create a readonly entry field for the Steam directory,
        # this is to be selected via a dialog to ensure it is valid
        # utilize a StringVar in order to set the text is the 'disabled' widget
        self.sdir = StringVar()
        self.sdir_entry = ttk.Entry(self.sdir_frame, width=48,
                                    textvariable=self.sdir, state='readonly')
        self.sdir_entry.grid(column=1, row=0, padx=4, sticky='w')

        # create a select button which will open a select directory dialog
        self.sdir_button = ttk.Button(self.sdir_frame, text='...', width=4,
                                      command=self.set_sdir)
        self.sdir_button.grid(column=2, row=0, padx=4, sticky='w')

        self.sdir_frame.pack(side='top')

    def set_sdir(self):
        ''' Simply set the Steam directory from the dialog.'''

        self.sdir.set(gSteamclean.get_dir())


class LibraryFrame:
    ''' UI frame to hold information regarding selected libraries to scan. '''

    def __init__(self, parent):
        self.lib_frame = ttk.Frame(parent, padding=4)

        self.lib_label = ttk.Label(self.lib_frame, text='Library list:')
        self.lib_label.grid(column=0, row=0, padx=4, sticky='n')

        self.lib_list = Listbox(self.lib_frame, width=46, height=4,
                                selectmode=SINGLE)
        self.lib_list.grid(column=1, row=0, padx=4, sticky='w')

        self.lib_button = ttk.Button(self.lib_frame, text='Add dir...',
                                     width=8, command=self.add_library)
        self.lib_button.grid(column=3, row=0, padx=4, sticky='w')

        self.lib_frame.pack(side='top')

    def add_library(self):
        ''' Insert every selected directory chosen from the dialog.'''

        self.lib_list.insert(END, gSteamclean.get_dir())


class gSteamclean():
    ''' Main application class to hold all internal frames for the UI. '''

    def __init__(self):
        self.app = Tk()
        self.app.title('steamclean')
        self.app.resizable(height=FALSE, width=FALSE)

        self.sdir_frame = SdirFrame(self.app)
        self.lib_frame = LibraryFrame(self.app)

    def get_dir():
        return filedialog.askdirectory(initialdir=syspath[0])


if __name__ == '__main__':
    gSteamclean().app.mainloop()
