from tkinter import *
from tkinter import filedialog
from tkinter import ttk

from sys import path as syspath


class SdirFrame:
    ''' Top UI frame to hold data for the default Steam directory. '''

    def __init__(self, parent):
        self.sdir_frame = ttk.Frame(parent, padding=4)

        self.sdir_label = ttk.Label(self.sdir_frame, text='Steam directory:')
        self.sdir_label.pack(padx=4, side='left')

        # create a readonly entry field for the Steam directory,
        # this is to be selected via a dialog to ensure it is valid
        # utilize a StringVar in order to set the text is the 'disabled' widget
        self.sdir = StringVar()
        self.sdir_entry = ttk.Entry(self.sdir_frame, width=48,
                                    textvariable=self.sdir, state='readonly')
        self.sdir_entry.pack(padx=4, side='left')

        # create a select button which will open a select directory dialog
        self.sdir_button = ttk.Button(self.sdir_frame, text='...', width=4,
                                      command=self.select_dir)
        self.sdir_button.pack(padx=4, side='left')

        self.sdir_frame.pack(side='top')

    def select_dir(self):
        self.sdir.set(filedialog.askdirectory(initialdir=syspath[0]))


class LibraryFrame:
    ''' UI frame to hold information regarding selected libraries to scan. '''

    def __init__(self, parent):
        self.lib_frame = ttk.Frame(parent, padding=4)

        self.lib_label = ttk.Label(self.lib_frame, text='Library list:')
        self.lib_label.pack(anchor='nw', padx=4, side='left')

        self.lib_list = Listbox(self.lib_frame, width=48, height=4)
        self.lib_list.pack(padx=4, side='left')

        self.lib_button = ttk.Button(self.lib_frame)
        self.lib_frame.pack(side='top')


class gSteamclean():
    ''' Main application class to hold all internal frames for the UI. '''

    def __init__(self):
        self.app = Tk()
        self.sdir_frame = SdirFrame(self.app)
        self.lib_frame = LibraryFrame(self.app)


if __name__ == '__main__':
    gSteamclean().app.mainloop()
