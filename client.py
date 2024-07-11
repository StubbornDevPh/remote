import socket
import tkinter as tk
from PIL import Image, ImageTk
import zlib
import io
import threading

# Server configuration
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12345

class RemoteDesktopClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Remote Desktop Client")
        self.master.geometry("700x500")  # Set initial size
        self.screen_label = tk.Label(self.master)
        self.screen_label.pack(fill=tk.BOTH, expand=True)

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((SERVER_HOST, SERVER_PORT))
        print(f"Connected to server {SERVER_HOST}:{SERVER_PORT}")

        self.receive_thread = threading.Thread(target=self.update_screen)
        self.receive_thread.start()

    def update_screen(self):
        while True:
            try:
                # Receive frame from server
                frame_data = self.client_socket.recv(99999999)
                frame_data = zlib.decompress(frame_data)
                img = Image.open(io.BytesIO(frame_data))

                # Update screen image in the main thread
                self.master.after(1, lambda: self.update_image(img))

            except Exception as e:
                print(f"Error: {str(e)}")
                break

    def update_image(self, img):
        # Resize the image for display
        resized_img = img.resize((self.master.winfo_width(), self.master.winfo_height()), Image.LANCZOS)

        img_tk = ImageTk.PhotoImage(resized_img)
        self.screen_label.config(image=img_tk)
        self.screen_label.image = img_tk  # Keep a reference to prevent garbage collection

def start_client():
    root = tk.Tk()
    client = RemoteDesktopClient(root)
    root.mainloop()

if __name__ == "__main__":
    start_client()
