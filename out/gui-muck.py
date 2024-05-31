""" Creating a Simple GUI for Preset Generation
Here's how you could create a simple GUI for the preset generation script:

1. Choose a GUI Framework:

Tkinter: Built-in Python library, good for simple UIs.
PyQt: Cross-platform, more features and flexibility.
Kivy: Supports touch interactions and mobile development.
2. Design the GUI Layout:

Input Fields:
Template file path
Output file path
Preset name
Number of presets
Buttons:
Generate Presets
Browse for files
Progress Bar:
Shows progress of preset generation
Output Area:
Displays messages and logs
3. Implement the Functionality:

Connect input fields to variables.
Bind button clicks to functions.
Use the generate_multiple_presets_from_template function from your script.
Update the progress bar and output area during generation.
4. Example Code (Tkinter): """

import os
import subprocess
import json
import tkinter as tk

from tkinter import Tk, Text, ttk, filedialog, END, Entry, Button, Label, filedialog

from buildpreset import generate_multiple_presets_from_template

# Create main window
window = tk.Tk()
window.title("Preset Generator")

# Define variables
template_file = ""
output_file = ""
preset_name = ""
num_presets = 0

# Define dictionary keys
config = {
    "template_file": "",
    "output_file": "",
    "preset_name": "",
    "num_presets": 0,
}


# load config from file
def load_config_from_file():
    config_file = filedialog.askopenfilename(
        initialdir="./", title="Select Config File", filetypes=(("json files", "*.json"), ("All files", "*.*"))
    )
    config = load_config(config_file)
    load_config_into_ui(config)


# save config to file
def save_config_to_file():
    save_ui_to_config(config)
    config_file = filedialog.asksaveasfilename(
        initialdir="./", title="Save Config File", filetypes=(("json files", "*.json"), ("All files", "*.*"))
    )
    if config_file:
        save_config(config, config_file)


# def load_config_into_ui(config):
#     template_entry = tk.Entry(window)
#     template_entry.grid(row=1, column=1)
#     output_entry = tk.Entry(window)
#     output_entry.grid(row=2, column=1)
#     name_entry = tk.Entry(window)
#     name_entry.grid(row=3, column=1)
#     num_presets_entry = tk.Entry(window)
#     num_presets_entry.grid(row=4, column=1)

#     template_entry.insert(0, config["template_file"])
#     output_entry.insert(0, config["output_file"])
#     name_entry.insert(0, config["preset_name"])
#     num_presets_entry.insert(0, config["num_presets"])


# # load values from config and populate UI
def load_config_into_ui(config):
    template_entry.insert(0, config["template_file"])
    output_entry.insert(0, config["output_file"])
    name_entry.insert(0, config["preset_name"])
    num_presets_entry.insert(0, config["num_presets"])


# save values from UI to config
def save_ui_to_config(config):
    config["template_file"] = template_entry.get()
    config["output_file"] = output_entry.get()
    config["preset_name"] = name_entry.get()
    config["num_presets"] = int(num_presets_entry.get())


# def run_buildpreset():
#     # Specify the command to run the script
#     command = ["python", "buildpreset.py"]

#     # Run the command and capture the output
#     result = subprocess.run(command, capture_output=True, text=True)

#     # Get the output as a string
#     output = result.stdout

#     # Print or use the output as needed
#     print(output)


# load config from file
def load_config(config_file):
    with open(config_file, "r") as f:
        config = json.load(f)
    return config


# save the last config used
def save_last_config(config):
    with open("last_config.json", "w") as f:
        json.dump(config, f)


# save config to file
def save_config(config, config_file):
    with open(config_file, "w") as f:
        json.dump(config, f, indent=4)


# load last config used on startup
if os.path.isfile("last_config.json"):
    last_config = load_config("last_config.json")
    config = last_config
    save_last_config(config)

# load the last config used on startup
if os.path.isfile("config.json"):
    config = load_config("config.json")
    load_config_into_ui(config)

# # save current config to file
# def save_config_to_file():
#     save_config(config, "config.json")


# load config from file and populate UI
# def load_config_from_file():
#     config = load_config("config.json")
#     load_config_into_ui(config)


def generate_presets():
    template_file = template_entry.get()
    output_file = output_entry.get()
    preset_name = name_entry.get()
    num_presets = int(num_presets_entry.get())

    # Create the args dictionary
    args = {
        "template_file": template_file,
        "output_file": output_file,
        "preset_name": preset_name,
        "num_presets": num_presets,
    }

    # Convert args dictionary to JSON string
    args_json = json.dumps(args)

    # Specify the command to run the script
    command = ["python3", "buildpreset.py", args_json]

    # Run the command and capture the output
    result = subprocess.run(command, capture_output=True, text=True)

    # Get the output as a string
    output = result.stdout

    # Output to output_area
    output_area.insert(END, "Generating presets...\n")
    output_area.insert(END, f"Template file: {template_file}\n")
    output_area.insert(END, f"Output file: {output_file}\n")
    output_area.insert(END, f"Preset name: {preset_name}\n")
    output_area.insert(END, f"Number of presets: {num_presets}\n")

    # Update the output_area with the captured output
    output_area.delete("1.0", "end")
    output_area.insert("end", output)

    # Update progress bar and output area
    progress_bar["value"] = 100
    output_area.insert(tk.END, "Preset generation complete!\n")


def browse_template_file():
    template_file = filedialog.askopenfilename(
        initialdir="./",
        title="Select Template File",
        filetypes=(("HLX files", "*.hlx"), ("All files", "*.*")),
    )
    template_entry.insert(0, template_file)


def browse_output_file():
    output_file = filedialog.asksaveasfilename(
        initialdir="./",
        title="Select Output File",
        filetypes=(("HLX files", "*.hlx"), ("All files", "*.*")),
    )
    output_entry.insert(0, output_file)


# Config file buttons
load_config_button = tk.Button(window, text="Load Config", command=load_config_from_file)
load_config_button.grid(row=0, column=0, padx=5, pady=5)

save_config_button = tk.Button(window, text="Save Config", command=save_config_to_file)
save_config_button.grid(row=0, column=1, padx=5, pady=5)

# Input fields
template_label = tk.Label(window, text="Template File:")
template_label.grid(row=1, column=0, padx=5, pady=5)
template_entry = tk.Entry(window)
template_entry.grid(row=1, column=1, padx=5, pady=5)
template_button = tk.Button(window, text="Browse", command=browse_template_file)
template_button.grid(row=1, column=2, padx=5, pady=5)

output_label = tk.Label(window, text="Output File:")
output_label.grid(row=2, column=0, padx=5, pady=5)
output_entry = tk.Entry(window)
output_entry.grid(row=2, column=1, padx=5, pady=5)
output_button = tk.Button(window, text="Browse", command=browse_output_file)
output_button.grid(row=2, column=2, padx=5, pady=5)

name_label = tk.Label(window, text="Preset Name:")
name_label.grid(row=3, column=0, padx=5, pady=5)
name_entry = tk.Entry(window)
name_entry.grid(row=3, column=1, padx=5, pady=5)

num_presets_label = tk.Label(window, text="Number of Presets:")
num_presets_label.grid(row=4, column=0, padx=5, pady=5)
num_presets_entry = tk.Entry(window)
num_presets_entry.grid(row=4, column=1, padx=5, pady=5)

# Generate button
generate_button = tk.Button(window, text="Generate Presets", command=generate_presets)
generate_button.grid(row=5, column=0, columnspan=3, padx=5, pady=5)

# Progress bar
progress_bar = tk.ttk.Progressbar(window, orient="horizontal", length=200, mode="determinate")
progress_bar.grid(row=6, column=0, columnspan=3, padx=5, pady=5)

# Output area
output_area = tk.Text(window)
output_area.grid(row=7, column=0, columnspan=3, padx=5, pady=5)

# Run the main loop
window.mainloop()
