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
frame1 = None
frame2 = None


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


def generate_presets(output_area):
    # global output_area
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

    # Create a subprocess using Popen
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # Read the output from the subprocess
    output, _ = process.communicate()

    # Decode the output to a string
    output = output.decode("utf-8")

    print("buildpreset ran")

    # print(output)

    # Output to output_area
    output_area.insert(END, "Generating presets...\n")
    output_area.insert(END, f"Template file: {template_file}\n")
    output_area.insert(END, f"Output file: {output_file}\n")
    output_area.insert(END, f"Preset name: {preset_name}\n")
    output_area.insert(END, f"Number of presets: {num_presets}\n")

    # Update the output_area with the captured output
    # output_area.delete("1.0", "end")
    output_area.insert("end", output)
    # Update progress bar and output area
    # progress_bar["value"] = 100
    output_area.insert(tk.END, "Preset generation complete xxxx!\n")
    output_area.see(tk.END)

    print("Preset generation complete!")


def browse_template_file():
    template_entry.delete(0, "end")
    template_file = filedialog.askopenfilename(
        initialdir="./",
        title="Select Template File",
        filetypes=(("HLX files", "*.hlx"), ("All files", "*.*")),
    )
    template_entry.insert(0, template_file)


def browse_output_file():
    output_entry.delete(0, "end")
    output_file = filedialog.asksaveasfilename(
        initialdir="./",
        title="Select Output File",
        filetypes=(("HLX files", "*.hlx"), ("All files", "*.*")),
    )
    output_entry.insert(0, output_file)


# Function to show a specific frame
current_frame = None


def show_frame(frame):
    global current_frame
    if current_frame is not None:
        current_frame.pack_forget()
    current_frame = frame
    frame.pack(fill="both", expand=True)


# Function to clear the output area
def clear_output_area():
    output_area.delete("1.0", "end")


# Function to save the output area to a file
def save_output_area():
    output_file = filedialog.asksaveasfilename(
        initialdir="./", title="Save Output", filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
    )
    if output_file:
        with open(output_file, "w") as f:
            f.write(output_area.get("1.0", "end"))


def create_gui():
    # global output_area
    global template_entry
    global output_entry
    global name_entry
    global num_presets_entry
    global frame1
    global frame2

    # Create main window
    window = tk.Tk()
    window.title("Preset Generator")

    # Create frames
    frame1 = tk.Frame(window)
    frame2 = tk.Frame(window)

    # Create tab buttons
    def show_frame1():
        show_frame(frame1)

    def show_frame2():
        show_frame(frame2)

    button1 = tk.Button(window, text="Generate", command=show_frame1)
    button1.pack(side="left")

    button2 = tk.Button(window, text="Tab 2", command=show_frame2)
    button2.pack(side="left")

    # Hide frames initially
    frame1.pack(fill="both", expand=True)
    frame2.pack(fill="both", expand=True)
    frame2.pack_forget()

    # Move all the fields below to frame1
    frame1.columnconfigure(0, weight=1)
    frame1.columnconfigure(1, weight=1)
    frame1.columnconfigure(2, weight=1)

    template_label = tk.Label(frame1, text="Template File:")
    template_label.grid(row=1, column=0, padx=5, pady=5)
    template_entry = tk.Entry(frame1)
    template_entry.config(width=40)
    template_entry.grid(row=1, column=1, padx=5, pady=5)
    template_button = tk.Button(frame1, text="Browse", command=browse_template_file)
    template_button.grid(row=1, column=2, padx=5, pady=5)

    # Output area
    output_area = tk.Text(frame1)
    output_area.grid(row=7, column=0, columnspan=3, padx=5, pady=5)

    output_label = tk.Label(frame1, text="Output File:")
    output_label.grid(row=2, column=0, padx=5, pady=5)
    output_entry = tk.Entry(frame1)
    output_entry.config(width=40)
    output_entry.grid(row=2, column=1, padx=5, pady=5)
    output_button = tk.Button(frame1, text="Browse", command=browse_output_file)
    output_button.grid(row=2, column=2, padx=5, pady=5)

    name_label = tk.Label(frame1, text="Preset Name:")
    name_label.grid(row=3, column=0, padx=5, pady=5)
    name_entry = tk.Entry(frame1)
    name_entry.config(width=40)
    name_entry.grid(row=3, column=1, padx=5, pady=5)

    num_presets_label = tk.Label(frame1, text="Number of Presets:")
    num_presets_label.grid(row=4, column=0, padx=5, pady=5)
    num_presets_entry = tk.Entry(frame1)
    num_presets_entry.config(width=40)
    num_presets_entry.grid(row=4, column=1, padx=5, pady=5)

    # Generate button
    generate_button = tk.Button(frame1, text="Generate Presets", command=lambda: generate_presets(output_area))
    generate_button.grid(row=5, column=0, columnspan=3, padx=5, pady=5)

    # # Progress bar
    # progress_bar = tk.ttk.Progressbar(window, orient="horizontal", length=200, mode="determinate")
    # progress_bar.grid(row=6, column=0, columnspan=3, padx=5, pady=5)

    # Load recent config on startup
    load_recent_config_from_file()

    # Run the main loop
    window.mainloop()


create_gui()