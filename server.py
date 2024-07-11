import socket
import threading
import tkinter as tk
from PIL import ImageGrab
import io
import zlib

# Server configuration
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 12345

# Global variables
server_socket = None
server_running = False
log_textbox = None  # Global variable for logging Text widget

# Function to capture and compress screen frames
def capture_screen():
    screen = ImageGrab.grab()  # Capture screen
    img_byte_arr = io.BytesIO()
    screen.save(img_byte_arr, format='JPEG', quality=120)  # Convert to JPEG with compression
    img_byte_arr = zlib.compress(img_byte_arr.getvalue())  # Compress image data
    return img_byte_arr

# Thread function to handle each client connection
def handle_client(client_socket, address):
    log_textbox.insert(tk.END, f"Connected with {address}\n")

    while server_running:
        try:
            # Capture screen and send to client
            frame = capture_screen()
            client_socket.send(frame)

        except Exception as e:
            log_textbox.insert(tk.END, f"Error: {str(e)}\n")
            break

    log_textbox.insert(tk.END, f"Connection closed with {address}\n")
    client_socket.close()

# Function to start the server
def start_server():
    global server_socket, server_running
    global log_textbox

    if server_running:
        log_textbox.insert(tk.END, "Server is already running.\n")
        return

    log_textbox.delete(1.0, tk.END)  # Clear previous logs
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(5)
    log_textbox.insert(tk.END, f"[*] Listening on {SERVER_HOST}:{SERVER_PORT}\n")
    server_running = True

    # Accept client connections in a new thread
    threading.Thread(target=server_accept_clients).start()

# Function to accept client connections
def server_accept_clients():
    global server_socket
    while server_running:
        try:
            client_socket, address = server_socket.accept()
            client_handler = threading.Thread(target=handle_client, args=(client_socket, address))
            client_handler.start()

        except OSError as e:
            if server_running:
                log_textbox.insert(tk.END, f"Error accepting client connection: {str(e)}\n")
                break
            else:
                log_textbox.insert(tk.END, "Server socket closed.\n")
                break

# Function to stop the server
def stop_server():
    global server_socket, server_running
    global log_textbox

    if not server_running:
        log_textbox.insert(tk.END, "Server is not running.\n")
        return

    server_running = False
    if server_socket:
        server_socket.close()
    log_textbox.insert(tk.END, "Server stopped.\n")

# GUI setup
def setup_gui():
    global log_textbox
    root = tk.Tk()
    root.title("Screen Sharing Server")

    log_textbox = tk.Text(root, bg="black", fg="lime green", wrap=tk.WORD)
    log_textbox.pack(fill=tk.BOTH, expand=True)

    start_button = tk.Button(root, text="Start Server", command=start_server)
    start_button.pack(pady=10)

    stop_button = tk.Button(root, text="Stop Server", command=stop_server)
    stop_button.pack(pady=10)

    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root))  # Handle window close event

    root.mainloop()

# Function to handle window close event
def on_closing(root):
    if server_running:
        stop_server()  # Call stop_server function to stop the server
    root.destroy()  # Close the tkinter GUI window

# Start the GUI
if __name__ == "__main__":
    setup_gui()
