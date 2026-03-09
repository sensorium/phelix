""" 
phelix.py
 
 This file is part of phelix.
 
 Copyright 2024 Tim Barrass
 
 phelix is licensed under the GNU General Public Licence (GPL) Version 3 or later. 
"""

import subprocess
import os
import glob
import json
import tkinter as tk
from tkinter import ttk, filedialog, END
from tkinter import BooleanVar
import var

# config dictionary
config = {}
entries_dict = {}  # Dictionary to store block probabilities entries
settings_entries_dict = {}  # Dictionary to store runtime settings entries

# Initialize global variables
gen_tab = None
mutate_tab = None

TEXT_FIELD_WIDTH = 50
NUMBER_FIELD_WIDTH = 5
OUTPUT_FIELD_WIDTH = 100
BUTTON_WIDTH = 15


def load_recent_config_from_file():
    config_files = glob.glob("config/*.json")
    config_files.sort(key=os.path.getmtime)
    if config_files:
        config_file = config_files[-1]
        with open(config_file, "r") as f:
            global config
            config = json.load(f)
        update_ui_from_config()


def load_config_from_file():
    if config_file := filedialog.askopenfilename(
        initialdir="./",
        title="Select Config File",
        filetypes=(("json files", "*.json"), ("All files", "*.*")),
    ):
        with open(config_file, "r") as f:
            global config
            config = json.load(f)
        update_ui_from_config()


def save_config_to_file(event=None):
    copyEntriesToBlockProbabilities()
    copyEntriesToRuntimeSettings()

    config["template_file"] = gen_tab.template_entry.get()
    config["output_file"] = gen_tab.output_entry.get()
    config["preset_name"] = gen_tab.name_entry.get()
    config["num_presets"] = int(gen_tab.num_presets_entry.get() or "0")

    config["mutate_template_file"] = mutate_tab.template_entry.get()
    config["mutate_output_file"] = mutate_tab.output_entry.get()
    config["mutate_preset_name"] = mutate_tab.name_entry.get()
    config["mutate_num_presets"] = int(mutate_tab.num_presets_entry.get() or "0")
    config["mutate_snapshot_src_num"] = mutate_tab.snapshot_src_num_entry.get()
    config["change_topology"] = mutate_tab.change_topology_var.get()
    config["change_controllers"] = mutate_tab.change_controllers_var.get()

    config["block_probabilities"] = var.block_probabilities
    config["runtime_settings"] = get_runtime_settings_dict()

    if config_file := filedialog.asksaveasfilename(
        initialdir="./",
        title="Save Config File",
        filetypes=(("json files", "*.json"), ("All files", "*.*")),
    ):
        with open(config_file, "w") as f:
            json.dump(config, f, indent=4)


def browse_open_hlx_file(hlx_entry, field_title):
    hlx_entry.delete(0, "end")
    if hlx_file := filedialog.askopenfilename(
        initialdir="./",
        title=field_title,
        filetypes=(("HLX files", "*.hlx"), ("All files", "*.*")),
    ):
        hlx_entry.insert(0, os.path.relpath(hlx_file))


def browse_save_hlx_file(hlx_entry, field_title):
    hlx_entry.delete(0, "end")
    if output_file := filedialog.asksaveasfilename(
        initialdir="./",
        title=field_title,
        filetypes=(("HLX files", "*.hlx"), ("All files", "*.*")),
    ):
        hlx_entry.insert(0, os.path.relpath(output_file))


def update_ui_from_config():
    gen_tab.template_entry.delete(0, END)
    gen_tab.template_entry.insert(0, config["template_file"])
    gen_tab.output_entry.delete(0, END)
    gen_tab.output_entry.insert(0, config["output_file"])
    gen_tab.name_entry.delete(0, END)
    gen_tab.name_entry.insert(0, config["preset_name"])
    gen_tab.num_presets_entry.delete(0, END)
    gen_tab.num_presets_entry.insert(0, config["num_presets"])

    mutate_tab.template_entry.delete(0, END)
    mutate_tab.template_entry.insert(0, config["mutate_template_file"])
    mutate_tab.output_entry.delete(0, END)
    mutate_tab.output_entry.insert(0, config["mutate_output_file"])
    mutate_tab.name_entry.delete(0, END)
    mutate_tab.name_entry.insert(0, config["mutate_preset_name"])
    mutate_tab.num_presets_entry.delete(0, END)
    mutate_tab.num_presets_entry.insert(0, config["mutate_num_presets"])
    mutate_tab.snapshot_src_num_entry.delete(0, END)
    mutate_tab.snapshot_src_num_entry.insert(0, config["mutate_snapshot_src_num"])
    mutate_tab.change_topology_var.set(config["change_topology"])
    mutate_tab.change_controllers_var.set(config["change_controllers"])
    
    if "block_probabilities" in config:
        var.block_probabilities.update(config["block_probabilities"])

    if "runtime_settings" in config:
        apply_runtime_settings(config["runtime_settings"])

    for category, entry in entries_dict.items():
        entry.delete(0, END)
        entry.insert(0, var.block_probabilities.get(category, ""))

    for setting_name, entry in settings_entries_dict.items():
        entry.delete(0, END)
        entry.insert(0, getattr(var, setting_name, ""))


def copyEntriesToBlockProbabilities():
    for category, entry in entries_dict.items():
        # Probabilities must be integers for random.choices
        var.block_probabilities[category] = int(entry.get() or "0")


def get_runtime_settings_dict():
    return {
        "NUM_PEDAL2_PARAMS": var.NUM_PEDAL2_PARAMS,
        "NUM_MIDICC_PARAMS": var.NUM_MIDICC_PARAMS,
        "NUM_SNAPSHOT_PARAMS": var.NUM_SNAPSHOT_PARAMS,
        "BLOCKS_PATH": var.BLOCKS_PATH,
        "MUTATION_RATE": var.MUTATION_RATE,
        "FRACTION_MOVE": var.FRACTION_MOVE,
        "TOGGLE_RATE": var.TOGGLE_RATE,
    }


def apply_runtime_settings(settings):
    var.NUM_PEDAL2_PARAMS = int(settings.get("NUM_PEDAL2_PARAMS", var.NUM_PEDAL2_PARAMS))
    var.NUM_MIDICC_PARAMS = int(settings.get("NUM_MIDICC_PARAMS", var.NUM_MIDICC_PARAMS))
    var.NUM_SNAPSHOT_PARAMS = int(settings.get("NUM_SNAPSHOT_PARAMS", var.NUM_SNAPSHOT_PARAMS))
    var.BLOCKS_PATH = str(settings.get("BLOCKS_PATH", var.BLOCKS_PATH))
    var.MUTATION_RATE = float(settings.get("MUTATION_RATE", var.MUTATION_RATE))
    var.FRACTION_MOVE = float(settings.get("FRACTION_MOVE", var.FRACTION_MOVE))
    var.TOGGLE_RATE = float(settings.get("TOGGLE_RATE", var.TOGGLE_RATE))


def copyEntriesToRuntimeSettings():
    settings = {
        key: entry.get().strip() for key, entry in settings_entries_dict.items()
    }
    apply_runtime_settings(settings)


########### generate_tab #######################################################
class Generate:

    def __init__(self, parent):
        self.template_entry = None
        self.output_entry = None
        self.name_entry = None
        self.num_presets_entry = None
        self.output_area = None
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.create_widgets()

    def generate_presets(self):
        copyEntriesToBlockProbabilities()
        copyEntriesToRuntimeSettings()

        args = {
            "template_file": self.template_entry.get(),
            "output_file": self.output_entry.get(),
            "preset_name": self.name_entry.get(),
            "num_presets": int(self.num_presets_entry.get() or "0"),
            "block_probabilities": var.block_probabilities,
            "runtime_settings": get_runtime_settings_dict(),
        }
        args_json = json.dumps(args)
        command = ["python3", "generate.py", args_json]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output, _ = process.communicate()
        output = output.decode("utf-8")
        self.output_area.delete("1.0", tk.END)
        self.output_area.insert("end", output)
        self.output_area.insert(tk.END, "\nPreset generation complete!\n")
        self.output_area.see(tk.END)

    def create_widgets(self):
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)

        # Input Preset File
        self.template_entry = tk.Entry(self.frame)
        self.template_entry.config(width=TEXT_FIELD_WIDTH)
        self.template_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        template_button = tk.Button(
            self.frame,
            width=BUTTON_WIDTH,
            text="Input Preset File",
            command=lambda: browse_open_hlx_file(self.template_entry, "Select Input Preset"),
        )
        template_button.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        # Output Preset File
        self.output_entry = tk.Entry(self.frame)
        self.output_entry.config(width=TEXT_FIELD_WIDTH)
        self.output_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        output_button = tk.Button(
            self.frame,
            width=BUTTON_WIDTH,
            text="Output Preset File",
            command=lambda: browse_save_hlx_file(self.output_entry, "Select Output File"),
        )
        output_button.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        # Preset Name
        name_label = tk.Label(self.frame, text="Preset Name (optional):")
        name_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.name_entry = tk.Entry(self.frame)
        self.name_entry.config(width=TEXT_FIELD_WIDTH)
        self.name_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Number of Presets
        num_presets_label = tk.Label(self.frame, text="Number of Presets:")
        num_presets_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.num_presets_entry = tk.Entry(self.frame)
        self.num_presets_entry.config(width=NUMBER_FIELD_WIDTH)
        self.num_presets_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # Generate Button
        generate_button = tk.Button(self.frame, text="Generate Presets", command=lambda: self.generate_presets())
        generate_button.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        # Output Area
        self.output_area = tk.Text(self.frame, width=OUTPUT_FIELD_WIDTH)
        self.output_area.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky="w")


class Mutate:

    def __init__(self, parent):
        self.template_entry = None
        self.output_entry = None
        self.name_entry = None
        self.num_presets_entry = None
        self.snapshot_src_num_entry = None
        self.change_topology_var = BooleanVar()
        self.change_controllers_var = BooleanVar()
        self.output_area = None
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.create_widgets()

    def mutate_preset(self):
        copyEntriesToBlockProbabilities()
        copyEntriesToRuntimeSettings()

        args = {
            "template_file": self.template_entry.get(),
            "output_file": self.output_entry.get(),
            "snapshot_src_num": self.snapshot_src_num_entry.get(),
            "preset_name": self.name_entry.get(),
            "num_presets": int(self.num_presets_entry.get() or "0"),
            "change_topology": self.change_topology_var.get(),
            "change_controllers": self.change_controllers_var.get(),
            "block_probabilities": var.block_probabilities,
            "runtime_settings": get_runtime_settings_dict(),
        }

        args_json = json.dumps(args)
        command = ["python3", "mutate.py", args_json]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output, _ = process.communicate()
        output = output.decode("utf-8")
        self.output_area.delete("1.0", tk.END)
        self.output_area.insert("end", output)
        self.output_area.insert(tk.END, "\nPreset generation complete!\n")
        self.output_area.see(tk.END)

    def create_widgets(self):
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)

        # Input Preset File
        self.template_entry = tk.Entry(self.frame, width=TEXT_FIELD_WIDTH)
        self.template_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        template_button = tk.Button(
            self.frame,
            width=BUTTON_WIDTH,
            text="Input Preset File",
            command=lambda: browse_open_hlx_file(self.template_entry, "Select Input Preset"),
        )
        template_button.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.snapshot_src_num_entry = self._extracted_from_create_widgets_17(
            "Source Snapshot:", 1, NUMBER_FIELD_WIDTH
        )
        # Output Preset File
        self.output_entry = tk.Entry(self.frame)
        self.output_entry.config(width=TEXT_FIELD_WIDTH)
        self.output_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        output_button = tk.Button(
            self.frame,
            width=BUTTON_WIDTH,
            text="Output Preset File",
            command=lambda: browse_save_hlx_file(self.output_entry, "Select Output File"),
        )
        output_button.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        self.name_entry = self._extracted_from_create_widgets_17(
            "Preset Name (optional):", 3, TEXT_FIELD_WIDTH
        )
        self.num_presets_entry = self._extracted_from_create_widgets_17(
            "Number of Presets:", 4, NUMBER_FIELD_WIDTH
        )
        # Change Topology Checkbox
        change_topology_label = tk.Label(self.frame, text="Change Topology")
        change_topology_label.grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.change_topology_checkbox = tk.Checkbutton(self.frame, variable=self.change_topology_var)
        self.change_topology_checkbox.grid(row=5, column=1, padx=5, pady=5, sticky="w")

        # Change Controllers Checkbox
        change_controllers_label = tk.Label(self.frame, text="Change Controllers")
        change_controllers_label.grid(row=6, column=0, padx=5, pady=5, sticky="w")
        self.change_controllers_checkbox = tk.Checkbutton(self.frame, variable=self.change_controllers_var)
        self.change_controllers_checkbox.grid(row=6, column=1, padx=5, pady=5, sticky="w")

        # Mutate Button
        generate_button = tk.Button(self.frame, text="Mutate Preset", command=lambda: self.mutate_preset())
        generate_button.grid(row=7, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        # Output Area
        self.output_area = tk.Text(self.frame, width=OUTPUT_FIELD_WIDTH)
        self.output_area.grid(row=8, column=0, columnspan=3, padx=5, pady=5, sticky="w")

    # TODO Rename this here and in `create_widgets`
    def _extracted_from_create_widgets_17(self, text, row, width):
        # Source Snapshot
        snapshot_src_num_label = tk.Label(self.frame, text=text)
        snapshot_src_num_label.grid(row=row, column=0, padx=5, pady=5, sticky="w")
        result = tk.Entry(self.frame, width=width)
        result.grid(row=row, column=1, padx=5, pady=5, sticky="w")

        return result


window = tk.Tk()
# Set the theme to 'clam' or any other theme name
# style = ttk.Style()
# style.theme_use("clam")
window.title("Preset Generator")
tabs = ttk.Notebook(window)
gen_tab = Generate(tabs)
mutate_tab = Mutate(tabs)

probabilities_tab = ttk.Frame(window)
# Assuming constants.block_probabilities is a list of tuples [(category, value), ...]
for idx, (category, value) in enumerate(var.block_probabilities.items()):
    label = tk.Label(probabilities_tab, text=f"{category}:")
    label.grid(row=idx, column=0, padx=5, pady=5, sticky="w")

    entry = tk.Entry(probabilities_tab, width=NUMBER_FIELD_WIDTH)
    entry.insert(0, value)
    entry.grid(row=idx, column=1, padx=5, pady=5)

    entries_dict[category] = entry

copy_button = tk.Button(probabilities_tab, text="Update Probabilities", command=copyEntriesToBlockProbabilities)
copy_button.grid(row=len(var.block_probabilities), column=0, columnspan=2, padx=5, pady=5, sticky="ew")

settings_tab = ttk.Frame(window)
runtime_settings = get_runtime_settings_dict()
for idx, (setting_name, value) in enumerate(runtime_settings.items()):
    label = tk.Label(settings_tab, text=f"{setting_name}:")
    label.grid(row=idx, column=0, padx=5, pady=5, sticky="w")

    entry = tk.Entry(settings_tab, width=TEXT_FIELD_WIDTH if setting_name == "BLOCKS_PATH" else NUMBER_FIELD_WIDTH)
    entry.insert(0, value)
    entry.grid(row=idx, column=1, padx=5, pady=5, sticky="w")

    settings_entries_dict[setting_name] = entry

runtime_settings_button = tk.Button(settings_tab, text="Update Runtime Settings", command=copyEntriesToRuntimeSettings)
runtime_settings_button.grid(row=len(runtime_settings), column=0, columnspan=2, padx=5, pady=5, sticky="ew")

tabs.add(gen_tab.frame, text="Generate")
tabs.add(mutate_tab.frame, text="Mutate")
tabs.add(probabilities_tab, text="Probabilities")
tabs.add(settings_tab, text="Runtime Settings")
tabs.pack(expand=1, fill="both")

# -----------------------------------------------------------------------------
menubar = tk.Menu(window)
filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Load Config", command=load_config_from_file)
filemenu.add_command(label="Save Config", command=save_config_to_file)
menubar.add_cascade(label="File", menu=filemenu)
window.config(menu=menubar)

load_recent_config_from_file()

window.mainloop()
