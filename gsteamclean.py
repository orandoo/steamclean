from tkinter import *
from tkinter import filedialog
from tkinter import ttk

from sys import path as syspath


class SdirFrame(ttk.Frame):
    ''' Top UI frame to hold data for the default Steam directory. '''

    def __init__(self, parent, col=0, row=0):
        ttk.Frame.__init__(self, parent)
        #self.sdir_frame = ttk.Frame(parent)

        self.sdir_label = ttk.Label(parent, text='Steam directory:')
        self.sdir_label.grid(column=col, row=row, padx=10, pady=2, sticky=W)

        # create a readonly entry field for the Steam directory,
        # this is to be selected via a dialog to ensure it is valid
        # utilize a StringVar in order to set the text is the 'disabled' widget
        self.sdir = StringVar()
        self.sdir_entry = ttk.Entry(parent, width=48,
                                    textvariable=self.sdir)
        self.sdir_entry.grid(column=col+1, row=row, padx=10, pady=2, sticky=W)

        # create a select button which will open a select directory dialog
        self.sdir_button = ttk.Button(parent, text='...', width=4,
                                      command=self.set_sdir)
        self.sdir_button.grid(column=col+2, row=row, padx=10, pady=2, sticky=W)

    def set_sdir(self):
        ''' Simply set the Steam directory from the dialog.'''

        self.sdir.set(gSteamclean.get_dir())


class LibraryFrame(ttk.Frame):
    ''' UI frame to hold information regarding selected libraries to scan. '''

    def __init__(self, parent, col=0, row=0):
        ttk.Frame.__init__(self, parent)
        #self.lib_frame = ttk.Frame(parent, padding=4)

        self.lib_label = ttk.Label(parent, text='Library list:')
        self.lib_label.grid(column=col, row=row, padx=10, pady=2, sticky=NW)

        self.lib_list = Listbox(parent, width=48, height=4,
                                selectmode=SINGLE)
        self.lib_list.grid(column=col+1, row=row, padx=10, pady=2, sticky=W)

        self.lib_button = ttk.Button(parent, text='Add dir...',
                                     width=8, command=self.add_library)
        self.lib_button.grid(column=col+2, row=row, padx=10, pady=2, sticky=NW)

    def add_library(self):
        ''' Insert every selected directory chosen from the dialog.'''

        self.lib_list.insert(END, gSteamclean.get_dir())


class gSteamclean(Tk):
    ''' Main application class to hold all internal frames for the UI. '''

    def __init__(self):
        Tk.__init__(self)
        self.title('steamclean')
        self.resizable(height=FALSE, width=FALSE)

        self.sdir_frame = SdirFrame(self, row=0)
        self.lib_frame = LibraryFrame(self, row=1)

    def get_dir():
        return filedialog.askdirectory(initialdir=syspath[0])


if __name__ == '__main__':
    gSteamclean().mainloop()
