import subprocess
import os
import glob
import json
import tkinter as tk

from tkinter import Tk, Text, ttk, filedialog, END

from buildpreset import generate_multiple_presets_from_template

CONFIG_FILE = "startup_config.json"

# config dictionary
config = {}

# Initialize global variables
template_entry = None
output_entry = None
name_entry = None
num_presets_entry = None
output_area = None


def run_buildpreset():
    # Specify the command to run the script
    command = ["python", "buildpreset.py"]

    # Run the command and capture the output
    result = subprocess.run(command, capture_output=True, text=True)

    # Get the output as a string
    output = result.stdout

    # Print or use the output as needed
    print(output)


def load_recent_config_from_file():
    global template_entry
    global output_entry
    global name_entry
    global num_presets_entry
    config_files = glob.glob("*.json")
    config_files.sort(key=os.path.getmtime)
    if config_files:
        print("found config")
        config_file = config_files[-1]
        config = load_config(config_file)
        load_config_into_ui(config)


# load config from file
def load_config_from_file():
    config_file = filedialog.askopenfilename(
        initialdir="./", title="Select Config File", filetypes=(("json files", "*.json"), ("All files", "*.*"))
    )
    config = load_config(config_file)
    return config


# load config from file
def load_config(config_file):
    with open(config_file, "r") as f:
        config = json.load(f)
    return config


# save config to file
def save_config_to_file():
    save_ui_to_config(config)
    config_file = filedialog.asksaveasfilename(
        initialdir="./", title="Save Config File", filetypes=(("json files", "*.json"), ("All files", "*.*"))
    )
    if config_file:
        save_config(config, config_file)


# save config to file
def save_config(config, config_file):
    with open(config_file, "w") as f:
        json.dump(config, f, indent=4)


# load values from config and populate UI
def load_config_into_ui(config):
    global template_entry
    global output_entry
    global name_entry
    global num_presets_entry
    # if template_entry is None:
    #     template_entry = Entry(root)
    #     template_entry.pack()
    # if output_entry is None:
    #     output_entry = Entry(root)
    #     output_entry.pack()
    # if name_entry is None:
    #     name_entry = Entry(root)
    #     name_entry.pack()
    # if num_presets_entry is None:
    #     num_presets_entry = Entry(root)
    #     num_presets_entry.pack()
    template_entry.delete(0, END)
    template_entry.insert(0, config["template_file"])
    output_entry.delete(0, END)
    output_entry.insert(0, config["output_file"])
    name_entry.delete(0, END)
    name_entry.insert(0, config["preset_name"])
    num_presets_entry.delete(0, END)
    num_presets_entry.insert(0, config["num_presets"])


# save values from UI to config
def save_ui_to_config(config):
    config["template_file"] = template_entry.get()
    config["output_file"] = output_entry.get()
    config["preset_name"] = name_entry.get()
    config["num_presets"] = int(num_presets_entry.get())


# # save current config to file
# def save_config_to_file():
#     save_config(config, "config.json")


# load config from file and populate UI
# def load_config_from_file():
#     config = load_config("config.json")
#     load_config_into_ui(config)


def generate_presets():
    global output_area
    global template_entry
    global output_entry
    global name_entry
    global num_presets_entry

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
    print("about to run buildpreset")
    # Specify the command to run the script
    command = ["python3", "buildpreset.py", args_json]

    # Run the command and capture the output
    result = subprocess.run(command, capture_output=True, text=True)
    print("buildpreset ran")
    # Get the output as a string
    output = result.stdout
    # # Call the preset generation function
    # generate_multiple_presets_from_template(args)

    # # Example print statements
    # print("Generating presets...")
    # print(f"Template file: {template_file}")
    # print(f"Output file: {output_file}")
    # print(f"Preset name: {preset_name}")
    # print(f"Number of presets: {num_presets}")

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
    # progress_bar["value"] = 100
    # output_area.insert(tk.END, "Preset generation complete!\n")


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


def create_gui():
    global template_entry
    global output_entry
    global name_entry
    global num_presets_entry
    # Create main window
    window = tk.Tk()
    window.title("Preset Generator")

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

    # Load recent config on startup
    load_recent_config_from_file()

    # Run the main loop
    window.mainloop()


create_gui()
