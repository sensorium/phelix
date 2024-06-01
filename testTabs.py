import tkinter as tk
from tkinter import ttk

# Create the main window
window = tk.Tk()

# Create the tab widget
tabs = ttk.Notebook(window)

# Create the frames
tab1 = ttk.Frame(tabs)
tab2 = ttk.Frame(tabs)

# Add the frames to the tab widget
tabs.add(tab1, text="Tab One")
tabs.add(tab2, text="Tab Two")

# Pack the tab widget
tabs.pack(fill="both", expand=True)

# Configure the tab widget to allow clicking on the labels to switch tabs
tabs.enable_traversal()


# Add a button to tab 1
button1 = tk.Button(tab1, text="Button for Tab 1")
button1.pack()

# Add a button to tab 2
button2 = tk.Button(tab2, text="Button for Tab 2")
button2.pack()


# Run the main loop
window.mainloop()
