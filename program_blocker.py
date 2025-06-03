import psutil
import time
import threading
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk # Import ttk for themed widgets
import ctypes
import os

SAVE_FILE = "default_blocked_apps.txt"

# Load blocked apps from file or use defaults
def load_blocked_apps():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            apps = [line.strip() for line in f if line.strip()]
        return apps
    else:
        return ["Discord.exe", "Steam.exe", "Vesktop.exe"]

def save_blocked_apps():
    with open(SAVE_FILE, "w") as f:
        for app in blocked_apps:
            f.write(app + "\n")

blocked_apps = load_blocked_apps()

def kill_blocked_apps():
    blocked_apps_lower = [app.lower() for app in blocked_apps]
    while True:
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] and proc.info['name'].lower() in blocked_apps_lower:
                    print(f"[{datetime.now()}] Killing: {proc.info['name']}")
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        time.sleep(5)

def start_blocking_and_exit_gui(duration_minutes, root):
    root.destroy()  # Close GUI

    # Hide console window on Windows
    try:
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except Exception:
        pass

    def background_loop():
        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        blocked_apps_lower = [app.lower() for app in blocked_apps]
        while datetime.now() < end_time:
            for proc in psutil.process_iter(['name']):
                try:
                    if proc.info['name'] and proc.info['name'].lower() in blocked_apps_lower:
                        print(f"[{datetime.now()}] Killing: {proc.info['name']}")
                        proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            time.sleep(5)
        print("Blocking period is over.")

    threading.Thread(target=background_loop, daemon=False).start()


def update_blocked_list(listbox):
    listbox.delete(0, tk.END)
    for app in blocked_apps:
        listbox.insert(tk.END, app)

def add_app_from_entry(entry_widget, listbox):
    global blocked_apps
    app_name = entry_widget.get().strip()
    if app_name:
        if not app_name.lower().endswith(".exe"):
            messagebox.showwarning("Invalid Name", "App name must end with .exe (e.g., Discord.exe)")
            return
        if app_name not in blocked_apps:
            blocked_apps.append(app_name)
            save_blocked_apps()
            update_blocked_list(listbox)
            entry_widget.delete(0, tk.END)
        else:
            messagebox.showinfo("Info", f"{app_name} is already in the blocked list.")
    else:
        messagebox.showwarning("Empty Input", "Please enter an app name like Discord.exe")


def remove_selected_app(listbox):
    global blocked_apps
    selected = listbox.curselection()
    if not selected:
        messagebox.showinfo("No Selection", "Please select an app to remove.")
        return
    app_to_remove = listbox.get(selected[0])
    if app_to_remove in blocked_apps:
        blocked_apps.remove(app_to_remove)
        save_blocked_apps()
        update_blocked_list(listbox)

def on_start_button_click(duration_entry, root):
    try:
        duration = float(duration_entry.get())
        if duration <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid Duration", "Enter a positive number for duration.")
        return

    if not blocked_apps:
        messagebox.showwarning("No Apps", "Add at least one app to block.")
        return

    print(f"Blocking apps: {blocked_apps} for {duration} minutes.")
    start_blocking_and_exit_gui(duration, root)


def create_gui():
    root = tk.Tk()
    root.title("App Blocker")
    root.geometry("400x550") # Set a fixed window size
    root.resizable(False, False) # Make window non-resizable

    # Apply a theme
    style = ttk.Style()
    style.theme_use("clam") # "clam", "alt", "default", "classic"

    # Configure styles for widgets
    style.configure("TFrame", background="#f0f0f0")
    style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
    style.configure("TButton", font=("Arial", 10, "bold"), padding=5)
    style.configure("TEntry", padding=5)
    style.configure("TListbox", font=("Arial", 10))

    # Main frame for padding
    main_frame = ttk.Frame(root, padding="15 15 15 15")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Title Label
    title_label = ttk.Label(main_frame, text="App Blocker", font=("Arial", 16, "bold"))
    title_label.pack(pady=(0, 15))

    # Blocked Apps Section
    ttk.Label(main_frame, text="Currently Blocked Apps:").pack(pady=(5, 5), anchor=tk.W)

    listbox_frame = ttk.Frame(main_frame)
    listbox_frame.pack(pady=(0, 10), fill=tk.BOTH, expand=True)

    blocked_listbox = tk.Listbox(listbox_frame, width=40, height=10, font=("Arial", 10),
                                 selectmode=tk.SINGLE, bd=2, relief="groove")
    blocked_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Scrollbar for the listbox
    scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=blocked_listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    blocked_listbox.config(yscrollcommand=scrollbar.set)

    # Add/Remove App Section
    app_input_frame = ttk.Frame(main_frame)
    app_input_frame.pack(pady=(5, 10), fill=tk.X)

    app_entry = ttk.Entry(app_input_frame)
    app_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

    add_button = ttk.Button(app_input_frame, text="➕ Add", command=lambda: add_app_from_entry(app_entry, blocked_listbox))
    add_button.grid(row=0, column=1, padx=(0, 5))

    remove_button = ttk.Button(app_input_frame, text="❌ Remove Selected", command=lambda: remove_selected_app(blocked_listbox))
    remove_button.grid(row=0, column=2)

    # Make the entry expand with the frame
    app_input_frame.columnconfigure(0, weight=1)


    # Block Duration Section
    ttk.Label(main_frame, text="Block Duration (minutes):").pack(pady=(10, 5), anchor=tk.W)
    duration_entry = ttk.Entry(main_frame)
    duration_entry.insert(0, "60")
    duration_entry.pack(fill=tk.X, pady=(0, 10))

    # Start Blocking Button
    start_btn = ttk.Button(main_frame, text="Start Blocking", command=lambda: on_start_button_click(duration_entry, root))
    start_btn.pack(pady=(10, 0), fill=tk.X)

    update_blocked_list(blocked_listbox)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
