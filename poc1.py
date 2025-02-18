import os
import textwrap
import subprocess

def clear_screen():
    # Clear the screen for better simulation
    os.system('cls' if os.name == 'nt' else 'clear')

def print_line(text, width=80, color=None):
    # Simulate text color if supported by the terminal
    if color:
        print(f"\033[{color}m{text:<{width}}\033[0m")
    else:
        print(f"{text:<{width}}")

def print_box(text, width=20, height=3, x_offset=0, y_offset=0, color="92"):
    # Print a box with text inside using ANSI characters
    for i in range(height):
        if i == 0 or i == height - 1:
            line = "┌" + "─" * (width - 2) + "┐" if i == 0 else "└" + "─" * (width - 2) + "┘"
        else:
            if i == 1:
                line = "│ " + text.center(width - 4) + " │"
            else:
                line = "│ " + " " * (width - 4) + " │"
        print(f"\033[{y_offset + i + 1};{x_offset + 1}H\033[{color}m{line}\033[0m")

def print_sixel_image(file_path, width=60, height=15, x_offset=24, y_offset=5, color="92"):
    # This function reads and prints a sixel image file inside the large box
    try:
        with open(file_path, 'r') as file:
            sixel_data = file.read()
        # Move cursor to the start position inside the box
        print(f"\033[{y_offset + 2};{x_offset + 3}H", end="")
        # Output the sixel data
        print(sixel_data)
    except FileNotFoundError:
        print(f"\033[{y_offset + 2};{x_offset + 3}H\033[{color}mFile not found: {file_path}\033[0m")
    except IOError:
        print(f"\033[{y_offset + 2};{x_offset + 3}H\033[{color}mError reading file: {file_path}\033[0m")

def word_wrap_text(text, width):
    # Word wrap the text to fit within the specified width
    return textwrap.wrap(text, width=width)

def print_large_box(content, width=60, x_offset=24, y_offset=1, color="92", image_width=0, terminal_height=24):
    # Word wrap the content, accounting for image width
    adjusted_width = width - 4 - image_width  # Subtract for box borders and image
    wrapped_lines = []
    for paragraph in content.split('\n\n'):
        wrapped_lines.extend(word_wrap_text(paragraph, adjusted_width))
        wrapped_lines.append('')  # Add an empty line between paragraphs

    # Calculate the height based on the number of wrapped lines
    content_height = len(wrapped_lines)
    # Ensure the box fits within the terminal, leaving space for instructions
    height = min(content_height + 2, terminal_height - y_offset - 4)  # +2 for borders, -4 for space at bottom

    # Print a larger box around the main content, adjusting for image width
    # Top and bottom lines
    for i in range(height):
        if i == 0 or i == height - 1:
            line = "┌" + "─" * (width - 2) + "┐" if i == 0 else "└" + "─" * (width - 2) + "┘"
        else:
            line = "│" + " " * (width - 2) + "│"
        print(f"\033[{y_offset + i + 1};{x_offset + 1}H\033[{color}m{line}\033[0m")

    # Print content inside the box, shifted right by image_width
    for i, line in enumerate(wrapped_lines[:height - 2]):  # -2 for top and bottom borders
        adjusted_x_offset = x_offset + 3 + image_width
        print(f"\033[{y_offset + i + 2};{adjusted_x_offset}H\033[{color}m{line[:adjusted_width]}\033[0m")

def get_terminal_height():
    # Get terminal height using system commands
    if os.name == 'nt':  # Windows
        # Using 'mode con' command to get console info
        result = subprocess.run(['mode', 'con'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if 'Lines:' in line:
                return int(line.split(':')[1].strip())
    else:  # Unix-based systems
        # Using 'stty size' command to get terminal size
        result = subprocess.run(['stty', 'size'], capture_output=True, text=True)
        if result.returncode == 0:
            height, _ = result.stdout.split()
            return int(height)
    # Default value if we can't determine the height
    return 24  # Assuming a default terminal height of 24 lines

def main():
    clear_screen()

    # Title
    print_line("PERSONAL TERMINAL", color="92")
    print()

    # Folders - Adjust y_offset to align with the "This is a shared message" box
    print_line("FOLDERS", color="92")
    folders = ["PERSONAL", "SHARED", "UTILITY", "PERSONAL"]
    for i, folder in enumerate(folders):
        print_box(folder, width=20, height=3, x_offset=0, y_offset=1 + i*4)

    # Get terminal height
    terminal_height = get_terminal_height()

    # Main content - Adjust y_offset based on terminal height
    y_offset_shared_message = 1
    print_box("This is a shared message", width=34, height=3, x_offset=24, y_offset=y_offset_shared_message)

    # Path to your text file containing the message
    text_file_path = "/home/pi/interface/test.txt"

    try:
        # Read the message from the text file
        with open(text_file_path, 'r') as file:
            message = file.read()
    except FileNotFoundError:
        message = f"Error: File not found at {text_file_path}"
    except IOError:
        message = f"Error reading file: {text_file_path}"

    # Path to your sixel image file
    sixel_file_path = "/home/pi/Downloads/pepe2.six"

    # Assume the width of the sixel image in characters
    image_width = 20  # Example value, replace with actual width if known

    # Calculate y_offset for large box, ensuring it starts below "This is a shared message" box
    y_offset_large_box = y_offset_shared_message + 4  # +4 to account for the height of "This is a shared message" box

    # Draw larger box around main text, accounting for image width, terminal height, and adjusting y_offset
    print_large_box(message, width=60, x_offset=24, y_offset=y_offset_large_box, image_width=image_width, terminal_height=terminal_height)

    # Print the sixel image inside the large box
    print_sixel_image(sixel_file_path, width=60, height=15, x_offset=24, y_offset=y_offset_large_box)

    # Instructions - Positioned 2 rows up from the bottom
    print(f"\033[{terminal_height - 1};1H", end="")  # Move cursor to the second last row
    print_line("UP, DOWN: select folder | LEFT, RIGHT: scroll | q: exit", color="92")

if __name__ == "__main__":
    main()
