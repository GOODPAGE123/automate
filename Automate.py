"""
Create a log of softwares user open, documents user creates/ works on adding the time the user spends for each activity. User uses Windows.
Install libraries:
    pip install psutil pywin32
"""


import os
import datetime
import time
import psutil
import win32gui  # Windows-specific
import threading

def log_activity(activity, log_file_path, duration=None):
    """Logs an activity with a timestamp and optional duration."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp}: {activity}"
    if duration:
        log_entry += f" (Duration: {duration:.2f} seconds)"
    log_entry += "\n"

    try:
        with open(log_file_path, "a") as log_file:
            log_file.write(log_entry)
        print(f"Activity logged to {log_file_path}")
    except OSError as e:
        print(f"Error logging activity: {e}")

def create_log_file(log_file_path):
    """Creates the log file if it doesn't exist."""
    try:
        with open(log_file_path, "x") as log_file:  # 'x' for exclusive creation
            log_file.write("--- Daily Activity Log ---\n")
        print(f"Log file created at: {log_file_path}")
    except FileExistsError:
        print(f"Log file already exists at: {log_file_path}")
    except OSError as e:
        print(f"Error creating log file: {e}")

def monitor_processes(log_file_path):
    """Monitors running processes and logs software launches."""
    previous_processes = set(p.name() for p in psutil.process_iter())
    print("Monitoring processes...")

    while True:
        time.sleep(5)
        current_processes = set(p.name() for p in psutil.process_iter())
        new_processes = current_processes - previous_processes

        for process_name in new_processes:
            log_activity(f"Software launched: {process_name}", log_file_path)

        previous_processes = current_processes

def get_active_window_title():
    """Gets the title of the currently active window (Windows-specific)."""
    try:
        window_title = win32gui.GetWindowText(win32gui.GetForegroundWindow())
        return window_title
    except Exception as e:
        print(f"Error getting window title: {e}")
        return None

def monitor_active_window(log_file_path):
    """Monitors active window and logs changes with duration."""
    previous_window_title = None
    start_time = None
    print("Monitoring active window...")

    while True:
        time.sleep(5)
        current_window_title = get_active_window_title()

        if current_window_title and current_window_title != previous_window_title:
            if previous_window_title:
                end_time = time.time()
                duration = end_time - start_time if start_time else 0
                log_activity(f"Window closed/changed: {previous_window_title}", log_file_path, duration)

            log_activity(f"Active window: {current_window_title}", log_file_path)
            previous_window_title = current_window_title
            start_time = time.time()


# --- Main execution ---
if __name__ == "__main__":
    log_file = os.path.join(os.path.expanduser("~"), "daily_activity.txt")  # Log file in user's home directory
    create_log_file(log_file)

    # Start monitoring threads:
    process_thread = threading.Thread(target=monitor_processes, args=(log_file,))
    window_thread = threading.Thread(target=monitor_active_window, args=(log_file,))

    process_thread.daemon = True  # Allow main thread to exit
    window_thread.daemon = True

    process_thread.start()
    window_thread.start()

    try:
        while True:
            time.sleep(1)  # Keep main thread alive (adjust sleep time as needed)
    except KeyboardInterrupt:
        pass  # Allow Ctrl+C to exit

    print("Logging complete.")


# --- Scheduling (Optional - Windows) ---
# 1. Open Task Scheduler.
# 2. Create a Basic Task...
# 3. Name it (e.g., "Activity Logger").
# 4. Set trigger (e.g., "Daily" at a specific time).
# 5. Action: "Start a program".
# 6. Program/script: Full path to your Python interpreter (e.g., "C:\path\to\python.exe").
# 7. Add arguments: Full path to your script (e.g., "C:\path\to\activity_tracker.py").
# 8. Finish.

# To run in background (no console):
# 1. Create a .bat file (e.g., run_activity_tracker.bat):
#    start /b C:\path\to\python.exe C:\path\to\activity_tracker.py
# 2. Schedule the .bat file (not the Python script directly).
