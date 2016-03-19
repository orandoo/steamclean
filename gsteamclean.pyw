#!/usr/bin/env python3

# Filename:         gsteamclean.pyw
# Description:      tkinter frontend for steamclean.py

import providers.libsteam as libsteam
import providers.libgalaxy as libgalaxy
import providers.liborigin as liborigin

from os import name as osname
from os import path as ospath
from sys import path as syspath

from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk

import steamclean as sc


class DirectoryFrame(ttk.Frame):
    """ Top UI frame containing the list of directories to be scanned. """

    def __init__(self, parent, col=0, row=0, steamdir=None):
        ttk.Frame.__init__(self, parent)

        self.lib_label = ttk.Label(parent, text='Directory list:')
        self.lib_label.grid(column=col, row=row, padx=10, pady=2, sticky=NW)

        # listbox containing all selected additional directories to scan
        self.dirlist = Listbox(parent, width=64, height=8,
                               selectmode=MULTIPLE)
        self.dirlist.bind('<<ListboxSelect>>', self.on_select)
        self.dirlist.grid(column=col+1, row=row, padx=10, pady=2, sticky=W)

        self.btnframe = ttk.Frame(parent)
        self.btnframe.grid(column=col+2, row=row, sticky=NW)
        self.lib_addbutton = ttk.Button(self.btnframe, text='Add dir',
                                        command=self.add_library)
        self.lib_addbutton.grid(column=col, row=row, padx=10, pady=2,
                                sticky=NW)
        self.lib_delbutton = ttk.Button(self.btnframe, text='Del dir',
                                        command=self.rm_library,
                                        state=DISABLED)
        self.lib_delbutton.grid(column=col, row=row+1, padx=10, pady=2,
                                sticky=NW)

    def on_select(self, selection):
        """ Enable or disable based on a valid directory selection. """

        if self.dirlist.curselection():
            self.lib_delbutton.configure(state=NORMAL)
        else:
            self.lib_delbutton.configure(state=DISABLED)

    def add_library(self):
        """ Insert selected directory chosen from the dialog.
            Prevent duplicate directories by checking existing items. """

        newdir = gSteamclean.get_dir()
        if newdir not in self.dirlist.get(0, END):
            self.dirlist.insert(END, newdir)

    def rm_library(self):
        """ Remove selected items from listbox when button in remove mode. """

        # Reverse sort the selected indexes to ensure all items are removed
        selected = sorted(self.dirlist.curselection(), reverse=True)
        for item in selected:
            self.dirlist.delete(item)


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

        self.listframe = ttk.Frame(parent)
        self.listframe.grid(column=col, columnspan=3, row=row+1,
                            sticky=NSEW, padx=10, pady=2)

        self.hscroll = ttk.Scrollbar(self.listframe)
        self.hscroll.pack(side=BOTTOM, fill=X)

        self.vscroll = ttk.Scrollbar(self.listframe)
        self.vscroll.pack(side=RIGHT, fill=Y)

        # treeview containing details on filenames and sizes of all detected
        # files from specified directories
        self.fdata_tree = ttk.Treeview(self.listframe)
        self.fdata_tree['columns'] = ('Filesize')
        self.fdata_tree.config(xscrollcommand=self.hscroll.set,
                               yscrollcommand=self.vscroll.set)
        self.fdata_tree.column('Filesize', stretch=0, width=128)

        # use first column for the path instead of default icon
        self.fdata_tree.heading('#0', text='Path', anchor=W)
        self.fdata_tree.heading('0', text='Filesize (MB)', anchor=W)
        self.fdata_tree.pack(side=TOP, fill=BOTH)

        self.hscroll.configure(orient=HORIZONTAL,
                               command=self.fdata_tree.xview)
        self.vscroll.configure(orient=VERTICAL,
                               command=self.fdata_tree.yview)

        # label to show total files found and their size
        # this label is blank to hide it until required to be shown
        self.total_label = ttk.Label(parent)
        self.total_label.grid(column=col+1, row=row+2, padx=10, pady=2,
                              sticky=E)

        # button used to remove the detected data
        self.remove_button = ttk.Button(parent, text='Clean')
        self.remove_button['state'] = 'disabled'
        self.remove_button['command'] = lambda: gSteamclean.clean_all(parent)
        self.remove_button.grid(column=col+2, row=row+2, padx=10,
                                pady=2, sticky=E)


class gSteamclean(Tk):
    """ Main application class to hold all internal frames for the UI. """

    def __init__(self):
        Tk.__init__(self)

        if osname == 'nt':
            steamdir = libsteam.winreg_read()
            galaxydir = libgalaxy.winreg_read()
            origindir = liborigin.winreg_read()
            self.dirlist = [steamdir, galaxydir, origindir]

        self.title('steamclean v' + sc.VERSION)
        self.resizable(height=FALSE, width=FALSE)

        self.dirframe = DirectoryFrame(self, row=0)
        self.fdata_frame = FileDataFrame(self, row=1)

        for provider in self.dirlist:
            self.dirframe.dirlist.insert(END, provider)

            # Attempt to highlight default provider directories blue
            # This differentiates default locations from others in the list
            try:
                self.dirframe.dirlist.itemconfig(END, fg='blue')
            except:
                pass

        if steamdir:
            libs = libsteam.get_libraries(steamdir=steamdir)
            for lib in libs:
                self.dirframe.dirlist.insert(END, lib)

    def get_dir():
        """ Method to return the directory selected by the user which should
            be scanned by the application. """

        # get user specified directory and normalize path
        seldir = filedialog.askdirectory(initialdir=syspath[0])
        if seldir:
            seldir = ospath.abspath(seldir)
            return seldir

    def scan_dirs(self):
        self.fdata_frame.total_label['text'] = ''

        totals = {'count': 0, 'size': 0}

        # entry all previous results from gui
        treeview = self.fdata_frame.fdata_tree
        for item in treeview.get_children():
            treeview.delete(item)

        # build list of detected files from selected paths
        files = sc.find_redist(dirlist=self.dirframe.dirlist.get(0, END))

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

            # enable clean button only if items are found for removal
            self.fdata_frame.remove_button['state'] = 'enabled'
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

        # prompt user to confirm the permanent deletion of detected files
        confirm_prompt = 'Do you wish to permanently delete all items?'
        confirm = messagebox.askyesno('Confirm removal', confirm_prompt)

        # convert response into expected values for clean_data function
        if confirm is True:
            fcount, tsize = sc.clean_data(flist, confirm='y')
            filemsg = str(fcount) + ' files removed successfully.\n'
            sizemsg = str(format(tsize, '.2f')) + ' MB saved.'
            messagebox.showinfo('Success!', filemsg + sizemsg)

            # get list of all filenames and then remove them after cleaning
            treeitems = self.fdata_frame.fdata_tree.get_children()
            for item in treeitems:
                self.fdata_frame.fdata_tree.delete(item)
        else:
            sc.clean_data(flist, confirm='n')

if __name__ == '__main__':
    sc.print_header(filename=ospath.basename(__file__))
    gSteamclean().mainloop()
