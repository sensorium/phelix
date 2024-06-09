import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import subprocess


def call_generate_presets(args):
    command = ["python3", "main.py"] + [str(value) for value in args.values()]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output, _ = process.communicate()
    messagebox.showinfo("Generate Presets", output.decode("utf-8"))


def call_generate_mutations(args):
    command = ["python3", "/Users/timbarrass/Documents/phelix/mutate.py"] + [str(value) for value in args.values()]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output, _ = process.communicate()
    messagebox.showinfo("Generate Mutations", output.decode("utf-8"))


def browse_template_file():
    file_path = filedialog.askopenfilename(title="Select Template File")
    args["template_file"] = file_path
    template_entry.delete(0, tk.END)
    template_entry.insert(0, file_path)


def browse_output_file():
    file_path = filedialog.asksaveasfilename(title="Select Output File")
    args["output_file"] = file_path
    output_entry.delete(0, tk.END)
    output_entry.insert(0, file_path)


# Create the main window
window = tk.Tk()
window.title("Function Caller GUI")

args = {
    "template_file": "",
    "output_file": "",
    "preset_name": "",
    "num_presets": 0,
    "mutation_type": "",
    "num_mutations": 0,
}

# Input fields for Generate Presets
template_label = tk.Label(window, text="Template File:")
template_label.pack()
template_entry = tk.Entry(window)
template_entry.pack()

template_button = tk.Button(window, text="Browse", command=browse_template_file)
template_button.pack()

output_label = tk.Label(window, text="Output File:")
output_label.pack()
output_entry = tk.Entry(window)
output_entry.pack()

output_button = tk.Button(window, text="Browse", command=browse_output_file)
output_button.pack()

# Include the rest of the code for input fields, buttons, and function calls as before

# Run the GUI
window.mainloop()
