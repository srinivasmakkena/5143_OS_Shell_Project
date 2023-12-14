from rich.console import Console
print("Hi")
# Create a separate console window
console = Console()

# Now, you can use the console to print rich text
console.print("Hello, this is a rich console!")

# You can also use various formatting options provided by rich
console.print("[bold magenta]This text is bold and magenta[/bold magenta]")

# Close the console when you are done
