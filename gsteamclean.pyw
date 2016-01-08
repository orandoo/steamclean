#!/usr/bin/env python3

# Filename:         gsteamclean.pyw
# Description:      tkinter frontend for steamclean.py

from os import path as ospath
from sys import path as syspath

from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk

import steamclean as sc


class SdirFrame(ttk.Frame):
    """ Top UI frame to hold data for the default Steam directory. """

    def __init__(self, parent, col=0, row=0):
        ttk.Frame.__init__(self, parent)

        self.sdir_label = ttk.Label(parent, text='Steam directory:')
        self.sdir_label.grid(column=col, row=row, padx=10, pady=2, sticky=W)

        # create a readonly entry field for the Steam directory,
        # this is to be selected via a dialog to ensure it is valid
        # utilize a StringVar in order to set the text is the 'disabled' widget
        self.sdir = StringVar()

        # set button to disabled as this path should be automatically detected
        # and should not need modified
        self.sdir_entry = ttk.Entry(parent, width=64, state='readonly',
                                    textvariable=self.sdir)
        self.sdir_entry.grid(column=col+1, row=row, padx=10, pady=2, sticky=W)

        # use steamclean module to check registry for path and set if returned
        try:
            self.sdir.set(sc.win_reg_check())
        except:
            pass

        # create a select button which will open a select directory dialog
        self.sdir_button = ttk.Button(parent, text='...', width=4,
                                      command=self.set_sdir)
        self.sdir_button.grid(column=col+2, row=row, padx=10, pady=2, sticky=W)

    def set_sdir(self):
        """ Simply set the Steam directory from the dialog."""

        self.sdir.set(gSteamclean.get_dir())


class LibraryFrame(ttk.Frame):
    """ UI frame to hold information regarding selected libraries to scan. """

    def __init__(self, parent, col=0, row=0):
        ttk.Frame.__init__(self, parent)

        self.lib_label = ttk.Label(parent, text='Library list:')
        self.lib_label.grid(column=col, row=row, padx=10, pady=2, sticky=NW)

        # listbox containing all selected additional directories to scan
        self.lib_list = Listbox(parent, width=64, height=4,
                                selectmode=MULTIPLE)
        self.lib_list.bind('<<ListboxSelect>>', self.on_select)
        self.lib_list.grid(column=col+1, row=row, padx=10, pady=2, sticky=W)

        self.lib_button = ttk.Button(parent, text='Add dir',
                                     command=self.add_library)
        self.lib_button.grid(column=col+2, row=row, padx=10, pady=2, sticky=NW)

    def on_select(self, evt):
        self.lib_button['text'] = 'Del dir'
        self.lib_button['command'] = self.rm_library
        print(self.lib_list.curselection())

    def add_library(self):
        """ Insert every selected directory chosen from the dialog. 
            Prevent duplicate directories by checking existing items. """

        dirlist = self.lib_list.get(0, END)
        newdir = gSteamclean.get_dir()
        if newdir not in dirlist:
            self.lib_list.insert(END, newdir)

    def rm_library(self):
        """ Remove selected items from listbox when button in remove mode. """

        # Reverse sort the selected indexes to ensure all items are removed
        selected = sorted(self.lib_list.curselection(), reverse=True)
        for item in selected:
            self.lib_list.delete(item)
        self.lib_button['text'] = 'Add dir'
        self.lib_button['command'] = self.add_library


class FileDataFrame(ttk.Frame):
    def __init__(self, parent, col=0, row=0):
        ttk.Frame.__init__(self, parent)

        self.list_label = ttk.Label(parent, text='Detected files:')
        self.list_label.grid(column=col, row=row, padx=10, pady=2, sticky=NW)

        # button used to initiate the scan of the specified directories
        self.scan_btn = ttk.Button(parent, text='Scan', command=lambda:
                                   gSteamclean.scan_dirs(parent))
        self.scan_btn.grid(column=col+2, row=row, padx=10, pady=2,
                           sticky=E)

        # treeview containing details on filenames and sizes of all detected
        # files from specified directories
        self.fdata_tree = ttk.Treeview(parent)
        self.fdata_tree['columns'] = ('Filesize')
        self.fdata_tree.column('Filesize', stretch=0, width=128)

        # use first column for the path instead of default icon
        self.fdata_tree.heading('#0', text='Path', anchor=W)
        self.fdata_tree.heading('0', text='Filesize (MB)', anchor=W)
        self.fdata_tree.grid(column=col, columnspan=3, row=row+1,
                             padx=10, pady=2, sticky=NSEW)

        # label to show total files found and their size
        # this label is blank to hide it until required to be shown
        self.total_label = ttk.Label(parent)
        self.total_label.grid(column=col+1, row=row+2, padx=10, pady=2,
                              sticky=E)

        # button used to remove the detected data
        self.remove_button = ttk.Button(parent, text='Clean')
        self.remove_button['command'] = lambda: gSteamclean.clean_all(parent)
        self.remove_button.grid(column=col+2, row=row+2, padx=10,
                                pady=2, sticky=E)


class gSteamclean(Tk):
    """ Main application class to hold all internal frames for the UI. """

    def __init__(self):
        Tk.__init__(self)

        self.title('steamclean')
        self.resizable(height=FALSE, width=FALSE)

        self.sdir_frame = SdirFrame(self, row=0)
        self.lib_frame = LibraryFrame(self, row=1)
        self.fdata_frame = FileDataFrame(self, row=2)

    def get_dir():
        """ Method to return the directory selected by the user which should
            be scanned by the application. """

        # get user specified directory and normalize path
        seldir = filedialog.askdirectory(initialdir=syspath[0])
        if seldir:
            seldir = ospath.abspath(seldir)
            return seldir

    def scan_dirs(self):

        totals = {'count': 0, 'size': 0}

        # entry all previous results from gui
        treeview = self.fdata_frame.fdata_tree
        for item in treeview.get_children():
            treeview.delete(item)

        # build list of detected files from selected paths
        files = sc.find_redist(steamdir=self.sdir_frame.sdir_entry.get(),
                               library=self.lib_frame.lib_list.get(0, END))

        totals['count'] = str(len(files))

        if len(files) > 0:
            # add into gui all file paths and sizes formatted to MB
            for k, v in files.items():
                fsize = format(v, '.2f')
                totals['size'] = totals['size'] + v
                # insert data into root element at the end of the list
                # text is the file path, value is filesize
                self.fdata_frame.fdata_tree.insert('', 'end', text=k,
                                                   value=fsize)

            # total files found and modify hidden label with this data
            totals['size'] = str(format(totals['size'], '.2f'))
            totaltext = 'Total: %s files (%s MB)' % (totals['count'],
                                                     totals['size'])
            self.fdata_frame.total_label['text'] = totaltext
        else:
            messagebox.showinfo(title='Congratulations',
                                message='No files found for removal.')

    def clean_all(self):
        flist = {}  # dictionary of all file data read from gui

        # loop through treeview items to get the path and filesize
        treeview = self.fdata_frame.fdata_tree
        for i in treeview.get_children():
            # need to use text here as the first column was repurposed
            flist[treeview.item(i, 'text')] = treeview.item(i, 'value')[0]

        # prompt user to confirm the permanant deletion of detected files
        confirm_prompt = 'Do you wish to permanantly delete all items?'
        confirm = messagebox.askyesno('Confirm removal', confirm_prompt)

        # convert response into expected values for clean_data function
        if confirm is True:
            fcount, tsize = sc.clean_data(flist, confirm='y')
            filemsg = str(fcount) + ' files removed successfully.\n'
            sizemsg = str(format(tsize, '.2f')) + ' MB saved.'
            messagebox.showinfo('Success!', filemsg + sizemsg)
        else:
            sc.clean_data(flist, confirm='n')

if __name__ == '__main__':
    sc.print_header(filename=ospath.basename(__file__))
    gSteamclean().mainloop()
