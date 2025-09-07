import os
import time
import threading
from watchdog.observers import Observer  # Used to observe changes in the file system
from watchdog.events import FileSystemEventHandler  # Handles file system events
import shutil  # For file manipulation (e.g., moving files)
from tkinter import *  # GUI module
from tkinter import messagebox  # For displaying alert messages in GUI


# Main class for managing the directory watcher
class Watcher:
    def __init__(self, directory):
        # Initialize the watcher with the directory to monitor
        self.DIRECTORY_TO_WATCH = directory
        self.observer = Observer()  # Observer to track file system changes
        self.log_labels = []  # Store log messages to display in the GUI

        print(self.DIRECTORY_TO_WATCH)

    def run(self):
        # Starts the file system watcher
        try:
            event_handler = Handler(self.DIRECTORY_TO_WATCH, self.log_labels)
            # Schedule the observer to monitor the directory
            self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=False)
            self.observer.start()  # Start the observer

            self.sort()  # Perform an initial sort on existing files

            # Keep the program running to monitor changes
            try:
                while True:
                    time.sleep(5)  # Check for changes every 5 seconds
            except KeyboardInterrupt:
                # Stop the observer if the program is interrupted
                self.observer.stop()
                print("Observer Stopped")

            self.observer.join()  # Ensure observer thread joins properly

        except FileNotFoundError:
            # Handle invalid directory paths
            messagebox.showerror("Fake Path", message="This full_path does not exist")
            print("This full_path does not exist")

    def sort(self):
        # Organizes files in the watched directory by their extensions
        entries = os.listdir(self.DIRECTORY_TO_WATCH)
        entries.sort()  # Sort files alphabetically
        extensions = {}  # Placeholder for extension-based logic (currently unused)

        for entry in entries:
            full_path = os.path.join(self.DIRECTORY_TO_WATCH, entry)

            if os.path.isfile(full_path):
                try:
                    ext = os.path.splitext(entry)[1][1:]  # Get file extension without the dot

                    if ext == "":
                        print("No extension")  # Handle files with no extensions

                    directory = os.path.join(self.DIRECTORY_TO_WATCH, ext)

                    # Create a subdirectory for the file extension if it doesn't exist
                    if not os.path.exists(directory):
                        os.makedirs(directory)

                    # Move file to its respective directory
                    file_destination = os.path.join(directory, entry)
                    shutil.move(full_path, file_destination)

                    # Log the operation in the GUI
                    log = Label(windows, font=("Comic Sans", 15), bg="Sky Blue",
                                text=f'Moved {entry} to {directory}/')
                    log.pack()
                    self.log_labels.append(log)

                    print(f'Moved {entry} to {directory}/')

                except Exception as e:
                    # Catch any errors during the file operation
                    print(f"Failed to process {entry}: {e}")

    def clear(self):
        # Clear all log labels from the GUI
        for log in self.log_labels:
            log.destroy()
        self.log_labels.clear()  # Clear the list after destroying all labels


# Event handler class for responding to file system events
class Handler(FileSystemEventHandler):
    def __init__(self, directory_to_watch, log_labels):
        self.DIRECTORY_TO_WATCH = directory_to_watch
        self.log_labels = log_labels

    def on_created(self, event):
        # Triggered when a new file or directory is created
        print(f'Hey, {event.src_path} has been created!')

        file_path = event.src_path
        time.sleep(1)  # Delay to allow file writing to complete

        self.sort(file_path)  # Organize the newly created file

    def sort(self, filepath):
        # Sort a single file by moving it to its corresponding directory
        try:
            ext = os.path.splitext(filepath)[1][1:]  # Get file extension

            if ext == "":
                print("It has no extension")

            directory = os.path.join(self.DIRECTORY_TO_WATCH, ext)

            # Create directory if it doesn't exist
            if not os.path.exists(directory):
                os.makedirs(directory)
                print("It got the dir")

            # Move the file to its designated directory
            file_destination = os.path.join(directory, os.path.basename(filepath))
            shutil.move(filepath, file_destination)

            # Log the operation in the GUI
            log = Label(windows, font=("Comic Sans", 15), bg="Sky Blue",
                        text=f'Moved {os.path.basename(filepath)} to {directory}/')
            log.pack()
            self.log_labels.append(log)

            print("It moved")

        except Exception as e:
            # Handle errors in file sorting
            print(f"Failed to process {filepath}: {e}")

    @staticmethod
    def on_deleted(event):
        # Triggered when a file or directory is deleted
        print(f"Hey {event.src_path} has been deleted")


# Function to start the file watcher
def start_watcher():
    directory = entry.get().replace('"', '')  # Get the directory full_path from the GUI input
    if not os.path.exists(directory):
        # Show an error if the full_path is invalid
        messagebox.showerror("Invalid Path", "The full_path does not exist")
        return
    begin = Watcher(directory)

    # Add a button to clear log messages
    clear_button = Button(windows, font=("Comic Sans", 15), bg="Sky Blue", text="Clear",
                          border=10, command=begin.clear, activeforeground="black", activebackground="Sky Blue")
    clear_button.pack(side=TOP, anchor=NE)

    # Run the watcher in a separate thread
    watcher_thread = threading.Thread(target=begin.run)
    watcher_thread.daemon = True  # Ensure the thread exits with the main program
    watcher_thread.start()


# Main GUI setup
if __name__ == "__main__":
    windows = Tk()  # Create the main window
    label = Label(windows, text="Enter DIR Path", font=("Comic Sans", 30), bg="sky blue")
    label.pack()

    entry = Entry(windows, width=50, border=100, bg="sky blue", font=("ink free", 20))
    entry.pack()

    sort = Button(windows, text="Sort", font=("comic sans", 15), bg="light blue", border=10,
                  command=start_watcher, activeforeground="black", activebackground="light blue")
    sort.pack()

    credit = Label(windows, text="Made by Richmond", font=("Consolas", 10), bg="sky blue")
    credit.pack(side=BOTTOM, anchor=SE)

    # Center the window on the screen
    window_width = 500
    window_height = 500
    screen_width = windows.winfo_screenwidth()
    screen_height = windows.winfo_screenheight()
    x = int((screen_width / 2) - (window_width / 2))
    y = int((screen_height / 2) - (window_height / 2))
    windows.geometry("{}x{}+{}+{}".format(window_width, window_height, x, y))
    windows.config(bg="sky blue")  # Set background color
    windows.resizable(False, False)  # Disable resizing
    windows.title("File sorter")  # Set the window title
    windows.mainloop()  # Start the GUI loop
