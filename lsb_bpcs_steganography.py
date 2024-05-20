import tkinter as tk  # Import the tkinter library for GUI
from tkinter import filedialog, messagebox  # Import specific components from tkinter
from PIL import Image, ImageTk, UnidentifiedImageError  # Import PIL for image handling
import wave  # Import wave for audio file handling
import os  # Import os for operating system interactions
import numpy as np  # Import numpy for array manipulation

class SteganographyApp:
    def __init__(self, root):
        self.root = root  # Set the root window
        self.root.title("LSB & BPCS Steganography and Steganalysis")  # Set the title of the window
        
        # Create a frame to hold the widgets
        self.frame = tk.Frame(root)
        self.frame.pack(pady=20)  # Add padding around the frame
        
        # Button to select the cover file
        self.cover_button = tk.Button(self.frame, text="Select Cover File", command=self.load_cover)
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
        
        # Button to encode the payload into the cover file using LSB
        self.encode_button = tk.Button(self.frame, text="Encode LSB", command=self.encode_lsb)
        self.encode_button.grid(row=2, column=0, pady=10)  # Place the button in the grid with padding
        
        # Button to decode the payload from the stego file using LSB
        self.decode_button = tk.Button(self.frame, text="Decode LSB", command=self.decode_lsb)
        self.decode_button.grid(row=2, column=1, pady=10)  # Place the button in the grid with padding
        
        # Button to encode the payload into the cover file using BPCS
        self.encode_bpcs_button = tk.Button(self.frame, text="Encode BPCS", command=self.encode_bpcs)
        self.encode_bpcs_button.grid(row=3, column=0, pady=10)  # Place the button in the grid with padding
        
        # Button to decode the payload from the stego file using BPCS
        self.decode_bpcs_button = tk.Button(self.frame, text="Decode BPCS", command=self.decode_bpcs)
        self.decode_bpcs_button.grid(row=3, column=1, pady=10)  # Place the button in the grid with padding
        
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
                image.thumbnail((250, 250))  # Resize the image
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

    def encode_image(self, cover_image_path, payload_text, num_lsb):
        image = Image.open(cover_image_path)  # Open the cover image
        binary_payload = ''.join(format(ord(char), '08b') for char in payload_text) + '1111111111111110'  # Convert the payload text to binary and add an end delimiter
        pixels = image.load()  # Load the image pixels
        width, height = image.size  # Get the image dimensions
        binary_index = 0
        
        for y in range(height):
            for x in range(width):
                if binary_index < len(binary_payload):
                    pixel = list(pixels[x, y])  # Get the pixel value
                    for i in range(3):  # For RGB channels
                        if binary_index < len(binary_payload):
                            pixel[i] = pixel[i] & ~(1 << (num_lsb - 1)) | (int(binary_payload[binary_index]) << (num_lsb - 1))  # Modify the LSB
                            binary_index += 1
                    pixels[x, y] = tuple(pixel)  # Set the modified pixel
                else:
                    break
        
        stego_image_path = cover_image_path.split('.')[0] + '_stego.png'  # Create the path for the stego image
        image.save(stego_image_path)  # Save the stego image
        return stego_image_path

    def decode_image(self, stego_image_path, num_lsb):
        image = Image.open(stego_image_path)  # Open the stego image
        pixels = image.load()  # Load the image pixels
        width, height = image.size  # Get the image dimensions
        binary_payload = ''
        
        for y in range(height):
            for x in range(width):
                pixel = pixels[x, y]
                for i in range(3):  # For RGB channels
                    binary_payload += str((pixel[i] >> (num_lsb - 1)) & 1)  # Extract the LSB
        
        # Split the binary payload into bytes and convert to characters
        byte_payload = [binary_payload[i:i+8] for i in range(0, len(binary_payload), 8)]
        decoded_text = ''.join(chr(int(byte, 2)) for byte in byte_payload)
        
        # Find the end delimiter and return the payload
        return decoded_text.split(chr(255) * 2)[0]

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

    def encode_lsb(self):
        # Check if both cover and payload files are selected
        if hasattr(self, 'cover_path') and hasattr(self, 'payload_path'):
            with open(self.payload_path, 'r') as file:
                payload_text = file.read()  # Read the payload text
            if self.cover_path.endswith(('.bmp', '.png', '.gif', '.jpg', '.jpeg')):
                stego_image_path = self.encode_image(self.cover_path, payload_text, self.lsb_var.get())  # Encode the payload into the image
                stego_image = Image.open(stego_image_path)  # Open the stego image
                stego_image.thumbnail((250, 250))  # Resize the stego image
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

    def decode_lsb(self):
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

    def calculate_complexity(self, block):
        # Calculate the complexity of an 8x8 block
        transitions = np.sum(np.abs(np.diff(block))) + np.sum(np.abs(np.diff(block, axis=0)))
        return transitions

    def embed_payload_into_image(self, image_path, payload_text):
        image = Image.open(image_path).convert('L')  # Convert image to grayscale
        image_data = np.array(image)
        
        binary_image = np.unpackbits(image_data, axis=1)  # Convert to binary
        payload_binary = ''.join(format(ord(char), '08b') for char in payload_text)
        payload_binary += '00000000' * 8  # End delimiter
        
        height, width = binary_image.shape
        block_size = 8
        payload_index = 0
        
        for i in range(0, height, block_size):
            for j in range(0, width, block_size):
                block = binary_image[i:i+block_size, j:j+block_size]
                if self.calculate_complexity(block) > 30:  # Threshold for complexity
                    for k in range(block_size):
                        for l in range(block_size):
                            if payload_index < len(payload_binary):
                                block[k, l] = int(payload_binary[payload_index])
                                payload_index += 1
                            else:
                                break
                binary_image[i:i+block_size, j:j+block_size] = block
                if payload_index >= len(payload_binary):
                    break
        
        stego_image_data = np.packbits(binary_image)
        stego_image = Image.fromarray(stego_image_data)
        stego_image.save('stego_image_bpcs.png')
        return 'stego_image_bpcs.png'

    def decode_payload_from_image(self, image_path):
        image = Image.open(image_path).convert('L')
        image_data = np.array(image)
        binary_image = np.unpackbits(image_data, axis=1)
        
        height, width = binary_image.shape
        block_size = 8
        binary_payload = ''
        
        for i in range(0, height, block_size):
            for j in range(0, width, block_size):
                block = binary_image[i:i+block_size, j:j+block_size]
                if self.calculate_complexity(block) > 30:  # Threshold for complexity
                    for k in range(block_size):
                        for l in range(block_size):
                            binary_payload += str(block[k, l])
        
        byte_payload = [binary_payload[i:i+8] for i in range(0, len(binary_payload), 8)]
        decoded_text = ''.join(chr(int(byte, 2)) for byte in byte_payload)
        
        return decoded_text.split(chr(255) * 2)[0]  # Find the end delimiter and return the payload

    def encode_bpcs(self):
        # Check if both cover and payload files are selected
        if hasattr(self, 'cover_path') and hasattr(self, 'payload_path'):
            with open(self.payload_path, 'r') as file:
                payload_text = file.read()  # Read the payload text
            if self.cover_path.endswith(('.bmp', '.png', '.gif', '.jpg', '.jpeg')):
                stego_image_path = self.embed_payload_into_image(self.cover_path, payload_text)  # Encode the payload into the image using BPCS
                stego_image = Image.open(stego_image_path)  # Open the stego image
                stego_image.thumbnail((250, 250))  # Resize the stego image
                self.stego_image = ImageTk.PhotoImage(stego_image)  # Convert the stego image to PhotoImage
                self.stego_label.config(image=self.stego_image)  # Display the stego image in the label
                messagebox.showinfo("Encoding", f"Encoding completed successfully: {stego_image_path}")  # Show a success message
            else:
                messagebox.showwarning("Error", "Cover file type not supported for BPCS encoding")  # Show an error message for unsupported file types
        else:
            messagebox.showwarning("Error", "Please select both cover and payload files")  # Show an error message if files are not selected

    def decode_bpcs(self):
        # Check if the cover file is selected
        if hasattr(self, 'cover_path'):
            if self.cover_path.endswith(('.bmp', '.png', '.gif', '.jpg', '.jpeg')):
                decoded_text = self.decode_payload_from_image(self.cover_path)  # Decode the payload from the image using BPCS
                messagebox.showinfo("Decoding", f"Decoded text: {decoded_text}")  # Show the decoded text
            else:
                messagebox.showwarning("Error", "Cover file type not supported for BPCS decoding")  # Show an error message for unsupported file types
        else:
            messagebox.showwarning("Error", "Please select a cover file")  # Show an error message if the cover file is not selected

if __name__ == "__main__":
    root = tk.Tk()  # Create the main window
    app = SteganographyApp(root)  # Create an instance of the SteganographyApp class
    root.mainloop()  # Run the main loop
