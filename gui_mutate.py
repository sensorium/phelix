m_template_entry = None
m_output_entry = None
m_name_entry = None
m_num_presets_entry = None
m_output_area = None


def m_generate_presets(output_area):

    global m_template_entry
    global m_output_entry
    global m_name_entry
    global m_num_presets_entry

    m_template_file = m_template_entry.get()
    m_output_file = m_output_entry.get()
    m_preset_name = m_name_entry.get()
    m_num_presets = int(m_num_presets_entry.get())

    # Create the args dictionary
    m_args = {
        "template_file": m_template_file,
        "output_file": m_output_file,
        "preset_name": m_preset_name,
        "num_presets": m_num_presets,
    }

    # Convert args dictionary to JSON string
    m_args_json = json.dumps(m_args)

    # Specify the command to run the script
    command = ["python3", "mutate.py", m_args_json]

    # Create a subprocess using Popen
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # Read the output from the subprocess
    m_output, _ = process.communicate()

    # Decode the output to a string
    m_output = m_output.decode("utf-8")

    # Output to output_area
    output_area.insert(END, "Generating presets...\n")
    output_area.insert(END, f"Template file: {m_template_file}\n")
    output_area.insert(END, f"Output file: {m_output_file}\n")
    output_area.insert(END, f"Preset name: {m_preset_name}\n")
    output_area.insert(END, f"Number of presets: {m_num_presets}\n")

    # Update the output_area with the captured output
    # output_area.delete("1.0", "end")
    output_area.insert("end", m_output)
    # Update progress bar and output area
    # progress_bar["value"] = 100
    output_area.insert(tk.END, "\nPreset generation complete!\n")
    output_area.see(tk.END)

    print("Preset mutation complete!")


# # Fields in frame2
tab2.columnconfigure(0, weight=1)
tab2.columnconfigure(1, weight=1)
tab2.columnconfigure(2, weight=1)

m_template_label = tk.Label(tab2, text="Mutate Template File:")
m_template_label.grid(row=1, column=0, padx=5, pady=5)
m_template_entry = tk.Entry(tab2)
m_template_entry.config(width=40)
m_template_entry.grid(row=1, column=1, padx=5, pady=5)
m_template_button = tk.Button(tab2, text="Browse", command=browse_template_file)
m_template_button.grid(row=1, column=2, padx=5, pady=5)

m_output_label = tk.Label(tab2, text="Mutation Output Filename:")
m_output_label.grid(row=2, column=0, padx=5, pady=5)
m_output_entry = tk.Entry(tab2)
m_output_entry.config(width=40)
m_output_entry.grid(row=2, column=1, padx=5, pady=5)
m_output_button = tk.Button(tab2, text="Browse", command=browse_output_file)
m_output_button.grid(row=2, column=2, padx=5, pady=5)

# Output area
m_output_area = tk.Text(tab2)
m_output_area.grid(row=7, column=0, columnspan=3, padx=5, pady=5)

# Mutate button
m_generate_button = tk.Button(tab2, text="Mutate Preset", command=lambda: generate_presets(m_output_area))
m_generate_button.grid(row=6, column=0, columnspan=3, padx=5, pady=5)
mutate_label = tk.Label(tab2, text="Mutation Type:")
mutate_label.grid(row=0, column=0, padx=5, pady=5)
mutate_combo = tk.ttk.Combobox(tab2, values=mutations.mutate_types)
mutate_combo.grid(row=0, column=1, padx=5, pady=5)

num_mutations_label = tk.Label(tab2, text="Number of Mutations:")
num_mutations_label.grid(row=1, column=0, padx=5, pady=5)
num_mutations_entry = tk.Entry(tab2)
num_mutations_entry.grid(row=1, column=1, padx=5, pady=5)

mutate_button = tk.Button(tab2, text="Mutate", command=lambda: mutations(mutate_args))
mutate_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

# Fields in frame2 to run mutate.mutations()
mutate_button = tk.Button(tab2, text="Mutate", command=lambda: mutations(output_area))
mutate_button.grid(row=0, column=0, columnspan=3, padx=5, pady=5)
