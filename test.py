from tkinter import *
from tkinter import ttk
import os
import glob

# from PIL import Image, ImageTk, ImageGrab
from pathlib import Path


class App:
    def __init__(self, master):
        notebook = ttk.Notebook(master)
        notebook.pack()

        # Frames
        left_frame = ttk.Frame(notebook)
        right_frame = ttk.Frame(notebook)
        notebook.add(left_frame, text="Main-Screen")
        notebook.add(right_frame, text="Manual")

        var1 = IntVar()
        var1a = IntVar()

        # Displaying checkboxes and assigning to variables
        self.Checkbox = Checkbutton(
            right_frame,
            text="Ingredients present in full (any allergens in bold with allergen warning if necessary)",
            variable=var1,
        )
        self.Checkbox.grid(column=1, row=1, sticky=W)
        self.Checkbox2 = Checkbutton(right_frame, variable=var1a)
        self.Checkbox2.grid(column=0, row=1, sticky=W)

        ###FRAME 2###
        # widgets
        self.msg1 = Label(left_frame, text="Choose here")
        self.msg1.grid(column=0, row=0)


root = Tk()
root.minsize(890, 400)
root.title("test only")
app = App(root)
root.mainloop()
