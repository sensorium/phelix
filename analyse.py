import astroid

# Load the AST for your file
tree = astroid.parse(open("/Users/timbarrass/Documents/phelix/utils.py").read())

# Iterate through the functions
for func in tree.functions:
    # Get the function name
    func_name = func.name

    # Get the arguments
    args = func.args.args

    # Print information about the function
    print(f"Function: {func_name}")
    print(f"Arguments: {args}")

    # You can now analyze the function's body, its calls, etc.
