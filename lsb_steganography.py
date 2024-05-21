import tkinter as tk  # Import the tkinter library for GUI
from tkinter import filedialog, messagebox  # Import specific components from tkinter
from PIL import Image, ImageTk, UnidentifiedImageError  # Import PIL for image handling
import wave  # Import wave for audio file handling
import os  # Import os for operating system interactions
import cv2, numpy as np

class SteganographyApp:
    def __init__(self, root):
        self.root = root  # Set the root window
        self.root.title("LSB Steganography and Steganalysis")  # Set the title of the window
        self.root.geometry("700x500")
        self.root.minsize(700,500)
        self.root.maxsize(700,500)
        
        # Create a frame to hold the widgets
        self.frame = tk.Frame(root)
        self.frame.pack(pady=20)  # Add padding around the frame
        
        # Button to select the cover file
        self.cover_button = tk.Button(self.frame, text="Select Input File", command=self.load_cover)
        self.cover_button.grid(row=0, column=0, padx=10)  # Place the button in the grid with padding
        
        # Button to select the payload file
        self.payload_button = tk.Button(self.frame, text="Select Payload File", command=self.load_payload)
        self.payload_button.grid(row=0, column=1, padx=10)  # Place the button in the grid with padding
        
        # Label and spinbox for selecting the number of LSBs
        self.lsb_label = tk.Label(self.frame, text="Number of LSBs:")
        self.lsb_label.grid(row=1, column=0, pady=10)  # Place the label in the grid with padding
        
        self.lsb_var = tk.IntVar(value=1)  # Create an integer variable to hold the number of LSBs
        self.lsb_spinbox = tk.Spinbox(self.frame, from_=1, to=8, textvariable=self.lsb_var)
        self.lsb_spinbox.grid(row=1, column=1, pady=10)  # Place the spinbox in the grid with padding
        
        # Button to encode the payload into the cover file
        self.encode_button = tk.Button(self.frame, text="Encode", command=self.encode)
        self.encode_button.grid(row=2, column=0, pady=10)  # Place the button in the grid with padding
        
        # Button to decode the payload from the stego file
        self.decode_button = tk.Button(self.frame, text="Decode", command=self.decode)
        self.decode_button.grid(row=2, column=1, pady=10)  # Place the button in the grid with padding
        
        # Label to display the cover image
        self.cover_label = tk.Label(root)
        self.cover_label.pack(side="left", padx=20)  # Pack the label with padding
        
        # Label to display the stego image
        self.stego_label = tk.Label(root)
        self.stego_label.pack(side="right", padx=20)  # Pack the label with padding

    def load_cover(self):
        # Open a file dialog to select the cover file
        self.cover_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.bmp *.png *.gif *.jpg *.jpeg"), ("Audio Files", "*.wav")])
        if not self.cover_path:
            return  # If no file is selected, return
        
        try:
            # Check if the selected file is an image
            if self.cover_path.lower().endswith(('.bmp', '.png', '.gif', '.jpg', '.jpeg')):
                print(f"Selected cover file path: {self.cover_path}")  # Debugging statement
                image = Image.open(self.cover_path)  # Open the image
                image.thumbnail((300, 300))  # Resize the image
                self.cover_image = ImageTk.PhotoImage(image)  # Convert the image to PhotoImage
                self.cover_label.config(image=self.cover_image)  # Display the image in the label
            elif self.cover_path.lower().endswith('.wav'):
                messagebox.showinfo("Cover File", "Audio file selected")  # Show a message for audio files
        except UnidentifiedImageError:
            messagebox.showerror("Error", "Cannot identify image file. Please select a valid image file.")  # Show an error if the image can't be opened
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")  # Show a general error message

    def load_payload(self):
        # Open a file dialog to select the payload file
        self.payload_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if self.payload_path:
            messagebox.showinfo("Payload File", f"{os.path.basename(self.payload_path)} selected")  # Show a message with the payload file name

    def to_bin(self, data): # Convert data to binary format as a string
        if isinstance(data, str):
            return ''.join([ format(ord(i), "08b") for i in data ])
        elif isinstance(data, bytes) or isinstance(data, np.ndarray):
            return [ format(i, "08b") for i in data ]
        elif isinstance(data, int) or isinstance(data, np.uint8):
            return format(data, "08b")
        else:
            raise TypeError("Type not supported.")
    
    def encode_image(self, cover_image_path, payload_text, num_lsb):
        # image = Image.open(cover_image_path)  # Open the cover image
        # binary_payload = ''.join(format(ord(char), '08b') for char in payload_text) + '1111111111111110'  # Convert the payload text to binary and add an end delimiter
        # pixels = image.load()  # Load the image pixels
        # width, height = image.size  # Get the image dimensions
        # binary_index = 0
        
        # for y in range(height):
        #     for x in range(width):
        #         if binary_index < len(binary_payload):
        #             pixel = list(pixels[x, y])  # Get the pixel value
        #             for i in range(3):  # For RGB channels
        #                 if binary_index < len(binary_payload):
        #                     pixel[i] = pixel[i] & ~(1 << (num_lsb - 1)) | (int(binary_payload[binary_index]) << (num_lsb - 1))  # Modify the LSB
        #                     binary_index += 1
        #             pixels[x, y] = tuple(pixel)  # Set the modified pixel
        #         else:
        #             break

        # stego_image_path = cover_image_path.split('.')[0] + '_stego.png'  # Create the path for the stego image
        # image.save(stego_image_path)  # Save the stego image
        # return stego_image_path
    
        # BOTTOM CODE IS FOR CV2 VERSION AKA PROF VERSION

        # read the image
        image = cv2.imread(cover_image_path)
        # maximum bytes to encode
        n_bytes = image.shape[0] * image.shape[1] * 3 // 8
        if len(payload_text) > n_bytes:
            raise ValueError("[!] Insufficient bytes, need bigger image or less data.")
        # add stopping criteria
        payload_text += "====="
        data_index = 0
        # convert data to binary
        binary_payload_text = self.to_bin(payload_text)
        data_len = len(binary_payload_text)
        for row in image:
            for pixel in row:
                # convert RGB values to binary format
                r, g, b = map(lambda x: self.to_bin(x), pixel)
                # modify the least significant bit only if there is still data to store
                if data_index < data_len:
                    # least significant red pixel bit
                    pixel[0] = int(r[:-num_lsb] + binary_payload_text[data_index:data_index+num_lsb], 2)
                    data_index += num_lsb
                if data_index < data_len: # least significant green pixel bit
                    pixel[1] = int(g[:-num_lsb] + binary_payload_text[data_index:data_index+num_lsb], 2)
                    data_index += num_lsb
                if data_index < data_len: # least significant blue pixel bit
                    pixel[2] = int(b[:-num_lsb] + binary_payload_text[data_index:data_index+num_lsb], 2)
                    data_index += num_lsb
                if data_index >= data_len:
                    break

        stego_image_path = cover_image_path.split('.')[0] + '_stego.png'  # Create the path for the stego image
        cv2.imwrite(stego_image_path, image)
        return stego_image_path

    def decode_image(self, stego_image_path, num_lsb):
        # image = Image.open(stego_image_path)  # Open the stego image
        # pixels = image.load()  # Load the image pixels
        # width, height = image.size  # Get the image dimensions
        # binary_payload = ''
        
        # for y in range(height):
        #     for x in range(width):
        #         pixel = pixels[x, y]
        #         for i in range(3):  # For RGB channels
        #             binary_payload += str((pixel[i] >> (num_lsb - 1)) & 1)  # Extract the LSB
        
        # # Split the binary payload into bytes and convert to characters
        # byte_payload = [binary_payload[i:i+8] for i in range(0, len(binary_payload), 8)]
        # decoded_text = ''.join(chr(int(byte, 2)) for byte in byte_payload)
        
        # # Find the end delimiter and return the payload
        # return decoded_text.split(chr(255) * 2)[0]
    
        # BOTTOM CODE IS FOR CV2 VERSION AKA PROF VERSION

        # read the image
        image = cv2.imread(stego_image_path)
        binary_data = ""
        for row in image:
            for pixel in row:
                # convert RGB values to binary format
                r, g, b = map(lambda x: self.to_bin(x), pixel)
                # For each color channel
                for color in [r, g, b]:
                    binary_data += color[-num_lsb:]
        # split by 8-bits
        all_bytes = [binary_data[i: i+8] for i in range(0, len(binary_data), 8)]
        # convert from bits to characters
        decoded_data = ""
        for byte in all_bytes:
            decoded_data += chr(int(byte, 2))
            if decoded_data[-5:] == "=====":
                break
        return decoded_data[:-5]

    def encode_audio(self, cover_audio_path, payload_text, num_lsb):
        with wave.open(cover_audio_path, 'rb') as audio:
            params = audio.getparams()  # Get audio parameters
            frames = bytearray(list(audio.readframes(audio.getnframes())))  # Read audio frames
        
        binary_payload = ''.join(format(ord(char), '08b') for char in payload_text) + '1111111111111110'  # Convert the payload text to binary and add an end delimiter
        binary_index = 0
        
        for i in range(len(frames)):
            if binary_index < len(binary_payload):
                frames[i] = frames[i] & ~(1 << (num_lsb - 1)) | (int(binary_payload[binary_index]) << (num_lsb - 1))  # Modify the LSB
                binary_index += 1
            else:
                break
        
        stego_audio_path = cover_audio_path.split('.')[0] + '_stego.wav'  # Create the path for the stego audio
        with wave.open(stego_audio_path, 'wb') as audio:
            audio.setparams(params)  # Set audio parameters
            audio.writeframes(frames)  # Write the modified frames
        
        return stego_audio_path

    def decode_audio(self, stego_audio_path, num_lsb):
        with wave.open(stego_audio_path, 'rb') as audio:
            frames = bytearray(list(audio.readframes(audio.getnframes())))  # Read audio frames
        
        binary_payload = ''
        
        for frame in frames:
            binary_payload += str((frame >> (num_lsb - 1)) & 1)  # Extract the LSB
        
        # Split the binary payload into bytes and convert to characters
        byte_payload = [binary_payload[i:i+8] for i in range(0, len(binary_payload), 8)]
        decoded_text = ''.join(chr(int(byte, 2)) for byte in byte_payload)
        
        return decoded_text.split(chr(255) * 2)[0]  # Find the end delimiter and return the payload

    def encode(self):
        # Check if both cover and payload files are selected
        if hasattr(self, 'cover_path') and hasattr(self, 'payload_path'):
            with open(self.payload_path, 'r') as file:
                payload_text = file.read()  # Read the payload text
            if self.cover_path.endswith(('.bmp', '.png', '.gif', '.jpg', '.jpeg')):
                stego_image_path = self.encode_image(self.cover_path, payload_text, self.lsb_var.get())  # Encode the payload into the image
                stego_image = Image.open(stego_image_path)  # Open the stego image
                stego_image.thumbnail((300, 300))  # Resize the stego image
                self.stego_image = ImageTk.PhotoImage(stego_image)  # Convert the stego image to PhotoImage
                self.stego_label.config(image=self.stego_image)  # Display the stego image in the label
                messagebox.showinfo("Encoding", f"Encoding completed successfully: {stego_image_path}")  # Show a success message
            elif self.cover_path.endswith('.wav'):
                stego_audio_path = self.encode_audio(self.cover_path, payload_text, self.lsb_var.get())  # Encode the payload into the audio
                messagebox.showinfo("Encoding", f"Encoding completed successfully: {stego_audio_path}")  # Show a success message
            else:
                messagebox.showwarning("Error", "Cover file type not supported for encoding")  # Show an error message for unsupported file types
        else:
            messagebox.showwarning("Error", "Please select both cover and payload files")  # Show an error message if files are not selected

    def decode(self):
        # Check if the cover file is selected
        if hasattr(self, 'cover_path'):
            if self.cover_path.endswith(('.bmp', '.png', '.gif', '.jpg', '.jpeg')):
                decoded_text = self.decode_image(self.cover_path, self.lsb_var.get())  # Decode the payload from the image
                messagebox.showinfo("Decoding", f"Decoded text: {decoded_text}")  # Show the decoded text
            elif self.cover_path.endswith('.wav'):
                decoded_text = self.decode_audio(self.cover_path, self.lsb_var.get())  # Decode the payload from the audio
                messagebox.showinfo("Decoding", f"Decoded text: {decoded_text}")  # Show the decoded text
            else:
                messagebox.showwarning("Error", "Cover file type not supported for decoding")  # Show an error message for unsupported file types
        else:
            messagebox.showwarning("Error", "Please select a cover file")  # Show an error message if the cover file is not selected

if __name__ == "__main__":
    root = tk.Tk()  # Create the main window
    app = SteganographyApp(root)  # Create an instance of the SteganographyApp class
    root.mainloop()  # Run the main loop
