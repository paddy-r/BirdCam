# -*- coding: utf-8 -*-
"""
Created on Mon May  9 10:14:21 2022

@author: prehr
"""
import tkinter as tk

class CustomDialog(tk.Toplevel):
    def __init__(self, parent, prompt):
        tk.Toplevel.__init__(self, parent)

        self.camera = tk.IntVar(value = 2)

        self.label = tk.Label(self, text=prompt)
        # self.entry = tk.Entry(self, textvariable=self.var)
        for i in [0,1,2]:
            rb = tk.Radiobutton(self, text="camera" + str(i), variable=self.camera, value=i)
            rb.pack(side="top")
            rb.bind("<Return>", self.on_ok)

        self.ok_button = tk.Button(self, text="OK", command=self.on_ok)

        self.label.pack(side="top", fill="x")
        # self.entry.pack(side="top", fill="x")
        self.ok_button.pack(side="right")

        # self.entry.bind("<Return>", self.on_ok)

    def on_ok(self, event=None):
        self.destroy()

    def show(self):
        self.wm_deiconify()
        # self.entry.focus_force()
        self.wait_window()
        return self.camera.get()

class Example(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.button = tk.Button(self, text="Get Input", command=self.on_button)
        self.label = tk.Label(self, text="", width=20)
        self.button.pack(padx=8, pady=8)
        self.label.pack(side="bottom", fill="both", expand=True)

    def on_button(self):
        index = CustomDialog(self, "Click radio button:").show()
        self.label.configure(text="You entered:\n" + str(index))


if __name__ == "__main__":
    root = tk.Tk()
    root.wm_geometry("400x200")
    Example(root).pack(fill="both", expand=True)
    root.mainloop()