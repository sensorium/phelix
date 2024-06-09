import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import subprocess


def browse_template_file():
    file_path = filedialog.askopenfilename(title="Select Template File")
    template_entry.delete(0, tk.END)
    template_entry.insert(0, file_path)


def browse_output_file():
    file_path = filedialog.asksaveasfilename(title="Select Output File")
    output_entry.delete(0, tk.END)
    output_entry.insert(0, file_path)


def call_generate_presets():
    template_file = template_entry.get()
    output_file = output_entry.get()
    preset_name = name_entry.get()
    num_presets = int(num_presets_entry.get())

    command = ["python3", "main.py", template_file, output_file, preset_name, str(num_presets)]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output, _ = process.communicate()

    messagebox.showinfo("Generate Presets", output.decode("utf-8"))


mutate_args = {
    "template_file": "",
    "snapshot_src_num": "",
    "output_file": "",
    "num_presets": 0,
    "postfix_num": 0,
}


def call_generate_mutations():
    # Convert args dictionary to JSON string
    mutate_args_json = json.dumps(mutate_args)
    # Specify the command to run the script
    command = ["python3", "generate_multiple_mutations_from_template", mutate_args_json]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output, _ = process.communicate()

    messagebox.showinfo("Generate Mutations", output.decode("utf-8"))


# Create the main window
window = tk.Tk()
window.title("Function Caller GUI")

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

name_label = tk.Label(window, text="Preset Name:")
name_label.pack()
name_entry = tk.Entry(window)
name_entry.pack()

num_presets_label = tk.Label(window, text="Number of Presets:")
num_presets_label.pack()
num_presets_entry = tk.Entry(window)
num_presets_entry.pack()

generate_button = tk.Button(window, text="Generate Presets", command=call_generate_presets)
generate_button.pack()

# Input fields for Generate Mutations
mutation_type_label = tk.Label(window, text="Mutation Type:")
mutation_type_label.pack()
mutation_type_entry = tk.Entry(window)
mutation_type_entry.pack()

num_mutations_label = tk.Label(window, text="Number of Mutations:")
num_mutations_label.pack()
num_mutations_entry = tk.Entry(window)
num_mutations_entry.pack()

generate_mutations_button = tk.Button(window, text="Generate Mutations", command=call_generate_mutations)
generate_mutations_button.pack()

# Run the GUI
window.mainloop()
