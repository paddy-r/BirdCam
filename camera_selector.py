# -*- coding: utf-8 -*-
"""
Created on Sun May  8 17:41:31 2022

@author: hughr
"""
import tkinter as tk
from tkinter.simpledialog import Dialog

class MyDialog(Dialog):

    # override buttonbox() to create your action buttons
    def buttonbox(self):
        box = tk.Frame(self)
        # note that self.ok() and self.cancel() are defined inside `Dialog` class
        tk.Button(box, text="Yes", width=10, command=self.ok, default=tk.ACTIVE)\
            .pack(side=tk.TOP, padx=5, pady=5)
        tk.Button(box, text="No", width=10, command=self.cancel)\
            .pack(side=tk.TOP, padx=5, pady=5)
        tk.Button(box, text="No", width=10, command=self.cancel)\
            .pack(side=tk.TOP, padx=5, pady=5)
        box.pack()

root = tk.Tk()
root.withdraw()
dlg = MyDialog(root, title="Test")
print(dlg.result)
root.destroy()
