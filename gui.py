import subprocess
import os
import glob
import json
import tkinter as tk

from tkinter import Tk, Text, ttk, filedialog, END, BOTH, TRUE

# from main import generate_multiple_presets_from_template
from mutate import generate_multiple_mutations_from_template


# config dictionary
config = {}

# Initialize global variables

gen_tab = None
mutate_tab = None


def load_recent_config_from_file():
    config_files = glob.glob("*.json")
    config_files.sort(key=os.path.getmtime)
    if config_files:
        print("found config")
        config_file = config_files[-1]
        with open(config_file, "r") as f:
            config = json.load(f)
    gen_tab.template_entry.delete(0, END)
    gen_tab.template_entry.insert(0, config["template_file"])
    gen_tab.output_entry.delete(0, END)
    gen_tab.output_entry.insert(0, config["output_file"])
    gen_tab.name_entry.delete(0, END)
    gen_tab.name_entry.insert(0, config["preset_name"])
    gen_tab.num_presets_entry.delete(0, END)
    gen_tab.num_presets_entry.insert(0, config["num_presets"])


def load_config_from_file():
    config_file = filedialog.askopenfilename(
        initialdir="./", title="Select Config File", filetypes=(("json files", "*.json"), ("All files", "*.*"))
    )
    with open(config_file, "r") as f:
        return json.load(f)


def save_config_to_file():
    # save values from UI to config
    config["template_file"] = gen_tab.template_entry.get()
    config["output_file"] = gen_tab.output_entry.get()
    config["preset_name"] = gen_tab.name_entry.get()
    config["num_presets"] = int(gen_tab.num_presets_entry.get())
    config_file = filedialog.asksaveasfilename(
        initialdir="./", title="Save Config File", filetypes=(("json files", "*.json"), ("All files", "*.*"))
    )
    if config_file:
        with open(config_file, "w") as f:
            json.dump(config, f, indent=4)


def browse_open_hlx_file(hlx_entry, field_title):
    hlx_entry.delete(0, "end")
    hlx_file = filedialog.askopenfilename(
        initialdir="./",
        title=field_title,
        filetypes=(("HLX files", "*.hlx"), ("All files", "*.*")),
    )
    hlx_entry.insert(0, hlx_file)


def browse_save_hlx_file(hlx_entry, field_title):
    hlx_entry.delete(0, "end")
    output_file = filedialog.asksaveasfilename(
        initialdir="./",
        title=field_title,
        filetypes=(("HLX files", "*.hlx"), ("All files", "*.*")),
    )
    hlx_entry.insert(0, output_file)


# ---------------------------------------------------------------------------


# -----------------------------------------------------------------------------


########### generate_tab #######################################################
class Generate:

    def __init__(self, parent):
        self.template_entry = None
        self.output_entry = None
        self.name_entry = None
        self.num_presets_entry = None
        # self.output_area = None
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.create_widgets()

    def generate_presets(self):
        args = {
            "template_file": self.template_entry.get(),
            "output_file": self.output_entry.get(),
            "preset_name": self.name_entry.get(),
            "num_presets": int(self.num_presets_entry.get()),
        }
        args_json = json.dumps(args)
        command = ["python3", "main.py", args_json]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output, _ = process.communicate()
        output = output.decode("utf-8")
        self.output_area.insert("end", output)
        self.output_area.insert(tk.END, "\nPreset generation complete!\n")
        self.output_area.see(tk.END)

    def create_widgets(self):
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.columnconfigure(2, weight=1)

        template_label = tk.Label(self.frame, text="Input Preset File:")
        template_label.grid(row=1, column=0, padx=5, pady=5)
        self.template_entry = tk.Entry(self.frame)
        self.template_entry.config(width=40)
        self.template_entry.grid(row=1, column=1, padx=5, pady=5)
        template_button = tk.Button(
            self.frame,
            text="Browse",
            command=lambda: browse_open_hlx_file(self.template_entry, "Select Input Preset"),
        )
        template_button.grid(row=1, column=2, padx=5, pady=5)

        output_label = tk.Label(self.frame, text="Output Preset File:")
        output_label.grid(row=2, column=0, padx=5, pady=5)
        self.output_entry = tk.Entry(self.frame)
        self.output_entry.config(width=40)
        self.output_entry.grid(row=2, column=1, padx=5, pady=5)
        output_button = tk.Button(
            self.frame,
            text="Browse",
            command=lambda: browse_save_hlx_file(self.output_entry, "Select Output File"),
        )
        output_button.grid(row=2, column=2, padx=5, pady=5)

        name_label = tk.Label(self.frame, text="Preset Name (optional):")
        name_label.grid(row=3, column=0, padx=5, pady=5)
        self.name_entry = tk.Entry(self.frame)
        self.name_entry.config(width=40)
        self.name_entry.grid(row=3, column=1, padx=5, pady=5)

        num_presets_label = tk.Label(self.frame, text="Number of Presets:")
        num_presets_label.grid(row=4, column=0, padx=5, pady=5)
        self.num_presets_entry = tk.Entry(self.frame)
        self.num_presets_entry.config(width=40)
        self.num_presets_entry.grid(row=4, column=1, padx=5, pady=5)

        generate_button = tk.Button(self.frame, text="Generate Presets", command=lambda: self.generate_presets())
        generate_button.grid(row=6, column=0, columnspan=3, padx=5, pady=5)
        # generate_button.grid(row=6, column=0, padx=5, pady=5)

        self.output_area = tk.Text(self.frame)
        self.output_area.grid(row=7, column=0, columnspan=3, padx=5, pady=5)


class Mutate:

    def __init__(self, parent):
        self.template_entry = None
        self.output_entry = None
        self.name_entry = None
        self.num_presets_entry = None
        # self.output_area = None
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.create_widgets()

    def generate_presets(self):
        args = {
            "template_file": self.template_entry.get(),
            "output_file": self.output_entry.get(),
            "preset_name": self.name_entry.get(),
            "num_presets": int(self.num_presets_entry.get()),
        }
        args_json = json.dumps(args)
        command = ["python3", "main.py", args_json]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output, _ = process.communicate()
        output = output.decode("utf-8")
        self.output_area.insert("end", output)
        self.output_area.insert(tk.END, "\nPreset generation complete!\n")
        self.output_area.see(tk.END)

    def create_widgets(self):
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.columnconfigure(2, weight=1)

        template_label = tk.Label(self.frame, text="Input Preset File:")
        template_label.grid(row=1, column=0, padx=5, pady=5)
        self.template_entry = tk.Entry(self.frame)
        self.template_entry.config(width=40)
        self.template_entry.grid(row=1, column=1, padx=5, pady=5)
        template_button = tk.Button(
            self.frame,
            text="Browse",
            command=lambda: browse_open_hlx_file(self.template_entry, "Select Input Preset"),
        )
        template_button.grid(row=1, column=2, padx=5, pady=5)

        output_label = tk.Label(self.frame, text="Output Preset File:")
        output_label.grid(row=2, column=0, padx=5, pady=5)
        self.output_entry = tk.Entry(self.frame)
        self.output_entry.config(width=40)
        self.output_entry.grid(row=2, column=1, padx=5, pady=5)
        output_button = tk.Button(
            self.frame,
            text="Browse",
            command=lambda: browse_save_hlx_file(self.output_entry, "Select Output File"),
        )
        output_button.grid(row=2, column=2, padx=5, pady=5)

        name_label = tk.Label(self.frame, text="Preset Name (optional):")
        name_label.grid(row=3, column=0, padx=5, pady=5)
        self.name_entry = tk.Entry(self.frame)
        self.name_entry.config(width=40)
        self.name_entry.grid(row=3, column=1, padx=5, pady=5)

        num_presets_label = tk.Label(self.frame, text="Number of Presets:")
        num_presets_label.grid(row=4, column=0, padx=5, pady=5)
        self.num_presets_entry = tk.Entry(self.frame)
        self.num_presets_entry.config(width=40)
        self.num_presets_entry.grid(row=4, column=1, padx=5, pady=5)

        generate_button = tk.Button(self.frame, text="Generate Presets", command=lambda: self.generate_presets())
        generate_button.grid(row=6, column=0, columnspan=3, padx=5, pady=5)
        # generate_button.grid(row=6, column=0, padx=5, pady=5)

        self.output_area = tk.Text(self.frame)
        self.output_area.grid(row=7, column=0, columnspan=3, padx=5, pady=5)


window = tk.Tk()
window.title("Preset Generator")
tabs = ttk.Notebook(window)
gen_tab = Generate(tabs)
mutate_tab = Mutate(tabs)
tabs.add(gen_tab.frame, text="Generate")
tabs.add(mutate_tab.frame, text="Mutate")
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
