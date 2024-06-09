import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from mutate import mtest
from main import test


def function_on_tab1():
    # Call the function from another file with arguments for Tab 1
    mtest(s1="Argument 1 for Tab 1", s2="Argument 2 for Tab 1")


def function_on_tab2():
    # Call the function from another file with arguments for Tab 2
    test(s1="Argument 1 for Tab 2", s2="Argument 2 for Tab 2")


# Create the main window
window = tk.Tk()
window.title("GUI with Tabs")

# Create a tabbed interface
tabs = ttk.Notebook(window)

# Tab 1
tab1 = ttk.Frame(tabs)
tabs.add(tab1, text="Tab 1")

button_tab1 = tk.Button(tab1, text="Call Function on Tab 1", command=function_on_tab1)
button_tab1.pack(padx=20, pady=10)

# Tab 2
tab2 = ttk.Frame(tabs)
tabs.add(tab2, text="Tab 2")

button_tab2 = tk.Button(tab2, text="Call Function on Tab 2", command=function_on_tab2)
button_tab2.pack(padx=20, pady=10)

tabs.pack(expand=1, fill="both")

# Run the GUI
window.mainloop()
