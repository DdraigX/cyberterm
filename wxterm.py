import os
import requests
import xml.etree.ElementTree as ET
import sys
import textwrap
import subprocess
import logging
import time

# Set up logging to write to a file instead of stdout, keeping the terminal clean
logging.basicConfig(filename='weather_display.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

CLEAR_SCREEN = "\033[2J"
RESET = "\033[0m"

def grabImage():
    cmd = 'wget -N https://radar.weather.gov/ridge/standard/KLWX_0.gif'
    subprocess.Popen(cmd, shell=True, stdout=sys.stdout, stderr=subprocess.PIPE, text=True)

def get_terminal_size():
    """Get current terminal size"""
    return os.get_terminal_size().columns, os.get_terminal_size().lines

def draw_box(start_col, start_row, width, height):
    """Draw a box using ANSI escape codes with double lines and color"""
    # Define colors (green background, white text - adjust as needed)
    BOX_BG_COLOR = "\033[40m"  # Green background
    BOX_FG_COLOR = "\033[38;5;208m"  # White text
    RESET_COLOR = "\033[0m"    # Reset to default
    
    horizontal = "═" * (width - 2)
    output = []
    
    # Top border with color
    output.append(f"\033[{start_row};{start_col}H{BOX_BG_COLOR}{BOX_FG_COLOR}╔{horizontal}╗{RESET_COLOR}")
    
    # Sides with color
    for i in range(height - 2):
        output.append(f"\033[{start_row + i + 1};{start_col}H{BOX_BG_COLOR}{BOX_FG_COLOR}║{' ' * (width - 2)}║{RESET_COLOR}")
    
    # Bottom border with color
    output.append(f"\033[{start_row + height - 1};{start_col}H{BOX_BG_COLOR}{BOX_FG_COLOR}╚{horizontal}╝{RESET_COLOR}")
    
    return "".join(output)

def get_weather_forecast():
    """Fetch and parse weather forecast from XML, returning the first 4 non-empty text elements"""
    url = "https://forecast.weather.gov/MapClick.php?lat=38.3292&lon=-78.4801&unit=0&lg=english&FcstType=dwml"
    try:
        response = requests.get(url)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        
        # Find wordedForecast section
        worded_forecast = root.find(".//wordedForecast")
        if worded_forecast is None:
            logging.error("wordedForecast not found")
            return ["Error: wordedForecast not found"]
        
        # Get all forecast texts and filter out empty or whitespace-only nodes
        all_forecast_texts = [t.text.strip() for t in worded_forecast.findall("text") if t.text and t.text.strip()]
        if not all_forecast_texts:
            logging.error("No non-empty forecast texts found")
            return ["Error: No non-empty forecast texts found"]
        
        logging.debug(f"Found {len(all_forecast_texts)} non-empty forecast texts: {all_forecast_texts[:4]}...")  # Log first 4 for brevity
        
        # Take only the first 4 non-empty texts
        forecast_texts = all_forecast_texts[:4]
        
        # Define fixed titles
        daytitle = ["Today", "Tonight", "Tomorrow", "Tomorrow Night"]
        
        # Pair titles with texts (use empty string if fewer texts than titles)
        if len(forecast_texts) >= len(daytitle):
            return list(zip(daytitle, forecast_texts))
        else:
            # Pad with empty strings if fewer texts than titles
            padded_texts = forecast_texts + [""] * (len(daytitle) - len(forecast_texts))
            return list(zip(daytitle, padded_texts))
    
    except requests.RequestException as e:
        logging.error(f"Error fetching data: {str(e)}")
        return [f"Error fetching data: {str(e)}"]
    except ET.ParseError:
        logging.error("Error parsing XML")
        return ["Error parsing XML"]

def word_wrap(text, width, strip_ansi=False):
    """Wrap text to fit within the specified width, optionally stripping ANSI codes for length calculation"""
    if strip_ansi:
        # Remove ANSI escape codes for accurate width calculation
        import re
        ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
        clean_text = ansi_escape.sub('', text)
        return textwrap.wrap(clean_text, width=width-4)
    return textwrap.wrap(text, width=width-4)  # Subtract 4 for box padding

def display_image(image_path):
    """Display the specified image file using img2sixel with a width of 200 pixels"""
    try:
        logging.debug(f"Attempting to display image from: {image_path}")
        
        # Check if the file exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Display using img2sixel with width 200 pixels (matching your successful manual command)
        cmd = f"img2sixel -w 375 {image_path}"
        logging.debug(f"Executing command: {cmd}")
        
        # Run img2sixel, sending output directly to the terminal and capturing stderr
        process = subprocess.Popen(cmd, shell=True, stdout=sys.stdout, stderr=subprocess.PIPE, text=True)
        
        # Wait for the process to complete, capturing stderr
        stderr = process.communicate()[1]  # Get stderr
        
        if process.returncode != 0:
            logging.error(f"img2sixel failed with error: {stderr}")
            print(f"\033[2;{term_cols//2+2}HError: Failed to display image - {stderr}", end="")
        else:
            logging.debug("Image displayed successfully")
        
        # Log the environment for debugging (to file, not terminal)
        logging.debug(f"Current environment: {dict(os.environ)}")
        
    except FileNotFoundError as e:
        logging.error(f"Error: {str(e)}")
        print(f"\033[2;{term_cols//2+2}HError: {str(e)}", end="")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error displaying image: {str(e)}")
        print(f"\033[2;{term_cols//2+2}HError: Failed to display image - {str(e)}", end="")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        print(f"\033[2;{term_cols//2+2}HError: Unexpected error - {str(e)}", end="")

def main():


    print('Getting Latest Radar Image')
    grabImage()
    # Clear screen
    print(CLEAR_SCREEN, end="")
    sys.stdout.flush()  # Ensure screen is cleared before drawing
    
    # Get terminal dimensions
    global term_cols  # Make term_cols global for use in display_image
    term_cols, term_rows = get_terminal_size()
    
    # Calculate box dimensions (each box is half the terminal width)
    box_width = term_cols // 2
    box_height = term_rows - 2
    
    # Draw boxes first to establish layout
    print(draw_box(1, 1, box_width, box_height), end="")  # Left box for weather
    print(draw_box(box_width + 1, 1, box_width, box_height), end="")  # Right box for image
    sys.stdout.flush()  # Flush to ensure boxes are drawn before other output
    
    # Get and display weather forecast in left box
    forecasts = get_weather_forecast()
    midpoint = term_cols/2+2 
    title = "WX Radar"
    print(f"\033[1;{int(midpoint)}H\033[40;5;0m\033[4m{title}", end="")
    # Display title in left box
    title = "Weather Forecast"
    print(f"\033[1;2H\033[40;5;0m\033[4m{title[:box_width-4]}\033[0m", end="")
    obj = time.localtime()
    tm = time.asctime(obj)
    print(f"\033[{term_rows - 4};2H{tm[:box_width-4]}", end="")
    sys.stdout.flush()  # Flush after title
    
    # Display forecast data with word wrapping in left box
    current_row = 4  # Start below title
    for title_text, forecast_text in forecasts:
        if not forecast_text:  # Skip empty texts
            continue
            
        # Combine title and text on the same line, then wrap
        # Use underline for title (ANSI \033[4m for underline, \033[0m to reset)
        combined_text = f"\033[4m{title_text}:\033[0m {forecast_text}"
        wrapped_lines = word_wrap(combined_text, box_width, strip_ansi=True)
        
        if current_row + len(wrapped_lines) >= box_height - 1:
            break
            
        # Display each wrapped line, starting at column 2
        for i, line in enumerate(wrapped_lines, current_row):
            print(f"\033[{i};2H{line}", end="")
        
        current_row += len(wrapped_lines) + 1  # Add extra line for spacing
    sys.stdout.flush()  # Flush after weather data
    
    # Display specified image in right box
    # Specify the full path to your image file here (e.g., "/home/pi/terminal/wxradar2/KLWX_0.gif")
    image_path = "./KLWX_0.gif"  # Updated with your path from the log
    
    # Move cursor to right box and display image
    print(f"\033[2;{box_width+2}H", end="")  # Position cursor in right box, row 2, column box_width+2
    sys.stdout.flush()  # Flush to ensure cursor is positioned before image display
    display_image(image_path)
    sys.stdout.flush()  # Flush after image display

    # Reset cursor position and ensure proper flushing
    sys.stdout.flush()  # Explicitly flush stdout
    print(f"\033[{term_rows};1H", end="")
    sys.stdout.flush()  # Flush again to ensure all output is sent

if __name__ == "__main__":
    i = 1
    n = 1
    try:   
        # while True:
        #     if n == 1: 
        #         main()
        #         time.sleep(5)
        #     else: 
        #         break
        while True: 
            main()
            time.sleep(600)
            
    except KeyboardInterrupt:
        # Reset terminal on exit
        print(RESET)
        sys.exit(0)