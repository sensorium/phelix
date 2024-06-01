import tkinter as tk

# Create the main window
window = tk.Tk()

# Create the outer grid
outer_grid = tk.Frame(window)
outer_grid.pack(fill="both", expand=True)
outer_grid.rowconfigure(0, weight=1)
outer_grid.rowconfigure(1, weight=1)
outer_grid.rowconfigure(2, weight=1)
outer_grid.columnconfigure(0, weight=1)
outer_grid.columnconfigure(1, weight=1)
outer_grid.columnconfigure(2, weight=1)

# Create the inner grids
inner_grid_1 = tk.Frame(outer_grid)
inner_grid_1.grid(row=0, column=0, sticky="nsew")
inner_grid_1.rowconfigure(0, weight=1)
inner_grid_1.rowconfigure(1, weight=1)
inner_grid_1.columnconfigure(0, weight=1)
inner_grid_1.columnconfigure(1, weight=1)

inner_grid_2 = tk.Frame(outer_grid)
inner_grid_2.grid(row=0, column=1, sticky="nsew")
inner_grid_2.rowconfigure(0, weight=1)
inner_grid_2.rowconfigure(1, weight=1)
inner_grid_2.columnconfigure(0, weight=1)
inner_grid_2.columnconfigure(1, weight=1)

inner_grid_3 = tk.Frame(outer_grid)
inner_grid_3.grid(row=0, column=2, sticky="nsew")
inner_grid_3.rowconfigure(0, weight=1)
inner_grid_3.rowconfigure(1, weight=1)
inner_grid_3.columnconfigure(0, weight=1)
inner_grid_3.columnconfigure(1, weight=1)

# Add widgets to the inner grids
tk.Label(inner_grid_1, text="Widget 1").grid(row=0, column=0)
tk.Label(inner_grid_1, text="Widget 2").grid(row=0, column=1)
tk.Label(inner_grid_1, text="Widget 3").grid(row=1, column=0)
tk.Label(inner_grid_1, text="Widget 4").grid(row=1, column=1)

tk.Label(inner_grid_2, text="Widget 5").grid(row=0, column=0)
tk.Label(inner_grid_2, text="Widget 6").grid(row=0, column=1)
tk.Label(inner_grid_2, text="Widget 7").grid(row=1, column=0)
tk.Label(inner_grid_2, text="Widget 8").grid(row=1, column=1)

tk.Label(inner_grid_3, text="Widget 9").grid(row=0, column=0)
tk.Label(inner_grid_3, text="Widget 10").grid(row=0, column=1)
tk.Label(inner_grid_3, text="Widget 11").grid(row=1, column=0)
tk.Label(inner_grid_3, text="Widget 12").grid(row=1, column=1)

# Run the main loop
window.mainloop()
