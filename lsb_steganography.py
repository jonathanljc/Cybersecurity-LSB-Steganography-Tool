import tkinter as tk  # Import the tkinter library for GUI
from tkinter import filedialog, messagebox  # Import specific components from tkinter
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk, UnidentifiedImageError  # Import PIL for image handling
import wave  # Import wave for audio file handling
import os  # Import os for operating system interactions
import cv2, numpy as np
import vlc
from moviepy.editor import VideoFileClip
import shutil
import stat
import pygame

class SteganographyApp:
    def __init__(self, root):
        self.root = root  # Set the root window
        self.root.title("LSB Steganography and Steganalysis")  # Set the title of the window
        self.root.geometry("1200x800")
        self.root.minsize(1200, 800)
        self.root.maxsize(1200, 800)

        # Initialize the mixer module
        pygame.mixer.init()

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

        # Add drag-and-drop functionality
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.drop)

    def drop(self, event):
        file_path = event.data.strip('{}')
        if file_path.lower().endswith(('.bmp', '.png', '.gif', '.jpg', '.jpeg', '.wav', '.mp4', '.mkv')):
            self.cover_path = file_path
            self.load_cover_from_path(file_path)
        elif file_path.lower().endswith('.txt'):
            self.payload_path = file_path
            self.load_payload_from_path(file_path)
        else:
            messagebox.showwarning("Unsupported File", "The file type is not supported")

    def load_cover_from_path(self, path):
        self.cover_path = path
        try:
            self.stego_label.config(image="")
            self.cover_label.config(image="")
            self.cover_label.config(height=0, width=0)
            self.stego_label.config(height=0, width=0)

            # Destroy the play buttons if they exist
            if hasattr(self, 'play_button_cover'):
                self.play_button_cover.destroy()
            if hasattr(self, 'play_button_stego'):
                self.play_button_stego.destroy()

            if hasattr(self, 'player'):
                # Stop the player
                self.player.stop()
                # Release the media
                self.player.set_media(None)
                # Delete the player
                del self.player
            if hasattr(self, 'player2'):
                # Stop the player
                self.player2.stop()
                # Release the media
                self.player2.set_media(None)
                # Delete the player
                del self.player2
            # Check if the selected file is an image
            if self.cover_path.lower().endswith(('.bmp', '.png', '.gif', '.jpg', '.jpeg')):
                print(f"Selected cover file path: {self.cover_path}")  # Debugging statement
                image = Image.open(self.cover_path)  # Open the image
                image.thumbnail((500, 500))  # Resize the image
                self.cover_image = ImageTk.PhotoImage(image)  # Convert the image to PhotoImage
                self.cover_label.config(image=self.cover_image)  # Display the image in the label
            elif self.cover_path.lower().endswith(('.mp4', '.mkv')):
                print(f"Selected cover file path: {self.cover_path}")  # Debugging statement
                # Create a VLC instance
                instance = vlc.Instance()
                # Create a VLC player
                self.player = instance.media_player_new()
                # Create a new Media instance
                media = instance.media_new(self.cover_path)
                # Set the player media
                self.player.set_media(media)
                self.cover_label.config(height=70, width=70)
                # Set the player window ID
                self.player.set_hwnd(self.cover_label.winfo_id())
                # Play the video
                self.player.play()
                # Get the total number of frames (not directly possible with python-vlc)
                self.total_frames = None

            elif self.cover_path.lower().endswith('.wav'):
                messagebox.showinfo("Cover File", "Audio file selected")  # Show a message for audio files
                # Create Play button for cover audio
                self.play_button_cover = tk.Button(self.frame, text="Play Input Audio", command=self.play_cover_audio)
                self.play_button_cover.grid(row=5, column=0)  # Adjust row and column as per your layout

        except UnidentifiedImageError:
            messagebox.showerror("Error", "Cannot identify image file. Please select a valid image file.")  # Show an error if the image can't be opened
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")  # Show a general error message

    def load_cover(self):
        # Open a file dialog to select the cover file
        self.cover_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.bmp *.png *.gif *.jpg *.jpeg"), ("Audio Files", "*.wav"), ("Video Files", "*.mp4 *.mkv")])
        if self.cover_path:
            self.load_cover_from_path(self.cover_path)

    def load_payload_from_path(self, path):
        self.payload_path = path
        messagebox.showinfo("Payload File", f"{os.path.basename(self.payload_path)} selected")  # Show a message with the payload file name

    def load_payload(self):
        # Open a file dialog to select the payload file
        self.payload_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if self.payload_path:
            self.load_payload_from_path(self.payload_path)

    def to_bin(self, data):  # Convert data to binary format as a string
        if isinstance(data, str):
            return ''.join([format(ord(i), "08b") for i in data])
        elif isinstance(data, bytes) or isinstance(data, np.ndarray):
            return [format(i, "08b") for i in data]
        elif isinstance(data, int) or isinstance(data, np.uint8):
            return format(data, "08b")
        else:
            raise TypeError("Type not supported.")

    def encode_image(self, cover_image_path, payload_text, num_lsb):
        print("Encoding image...")
        # read the image
        image = cv2.imread(cover_image_path)
        # maximum bytes to encode
        n_bytes = (image.shape[0] * image.shape[1] * image.shape[2] * num_lsb) // 8
        if len(payload_text) > n_bytes:
            messagebox.showwarning("Error", "Insufficient bytes, need bigger image, smaller payload or more LSB.")
            raise ValueError("Error: Insufficient bytes, need bigger image, smaller payload or more LSB.")
        # add stopping criteria
        payload_text += "====="
        data_index = 0
        # convert data to binary
        print("Converting to binary...")
        binary_payload_text = self.to_bin(payload_text)
        data_len = len(binary_payload_text)

        print("Encoding image... (Please wait)")
        for row in image:
            for pixel in row:
                # convert RGB values to binary format
                r, g, b = map(lambda x: self.to_bin(x), pixel)
                # modify the least significant bit only if there is still data to store
                if data_index < data_len:
                    # least significant red pixel bit
                    pixel[0] = int(r[:-num_lsb] + binary_payload_text[data_index:data_index + num_lsb], 2)
                    data_index += num_lsb
                if data_index < data_len:  # least significant green pixel bit
                    pixel[1] = int(g[:-num_lsb] + binary_payload_text[data_index:data_index + num_lsb], 2)
                    data_index += num_lsb
                if data_index < data_len:  # least significant blue pixel bit
                    pixel[2] = int(b[:-num_lsb] + binary_payload_text[data_index:data_index + num_lsb], 2)
                    data_index += num_lsb
                if data_index >= data_len:
                    break

        stego_image_path = cover_image_path.split('.')[0] + '_stego.png'  # Create the path for the stego image
        cv2.imwrite(stego_image_path, image)
        print("Encoding completed!")
        return stego_image_path

    def decode_image(self, stego_image_path, num_lsb):
        # read the image
        print("Reading image..")
        image = cv2.imread(stego_image_path)
        binary_data = ""
        print("Decoding image... (Please wait)")
        for row in image:
            for pixel in row:
                # convert RGB values to binary format
                r, g, b = map(lambda x: self.to_bin(x), pixel)
                # For each color channel
                for color in [r, g, b]:
                    binary_data += color[-num_lsb:]
        # split by 8-bits
        print("Splitting binary...")
        all_bytes = [binary_data[i: i + 8] for i in range(0, len(binary_data), 8)]
        # convert from bits to characters
        print("Converting binary to characters...")
        decoded_data = ""
        for byte in all_bytes:
            decoded_data += chr(int(byte, 2))
            if decoded_data[-5:] == "=====":
                print("Decoding completed!")
                return decoded_data[:-5]
            if decoded_data[-4:] == "====":
                print("Decoding completed!")
                return decoded_data[:-4]

    def encode_video(self, cover_video_path, payload_text, num_lsb):
        try:
            print("Starting video encoding...")
            n_lsb = int(num_lsb)
            stego_video_path = self.encode_lsb(cover_video_path, payload_text, n_lsb)
            return stego_video_path
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Function to extract frames using moviepy and PIL
    def frame_extract(self, video_path):
        if not os.path.exists("./temp"):
            os.makedirs("temp")
        temp_folder = "./temp/"
        video_object = VideoFileClip(video_path)
        for index, frame in enumerate(video_object.iter_frames()):
            print(f"Extracting frames... (Frame {index})")
            img = Image.fromarray(frame, 'RGB')
            img.save(f'{temp_folder}{index}.png')

    # Function to encode text into video frames using LSB and then reassemble using ffmpeg
    def encode_lsb(self, video_path, text, n_lsb):
        self.frame_extract(video_path)

        temp_folder = "./temp/"
        # frames = sorted([f for f in os.listdir(temp_folder) if f.endswith('.png')])
        frames = sorted([f for f in os.listdir(temp_folder) if f.endswith('.png')], key=lambda f: int(f.split('.')[0]))

        text_bits = ''.join([format(ord(char), '08b') for char in text])
        text_bits += '00000000' * 8  # Adding 8 null bytes to signify the end of the message
        bit_index = 0

        for frame_idx, frame_file in enumerate(frames):
            frame = cv2.imread(os.path.join(temp_folder, frame_file))
            if bit_index >= len(text_bits):
                break  # Stop encoding if all text bits are encoded
            print("Encoding frame {}...".format(frame_file))
            # print(frame_file)
            for i in range(frame.shape[0]):
                for j in range(frame.shape[1]):
                    for k in range(3):  # Iterate over the BGR channels
                        if bit_index < len(text_bits):
                            frame[i, j, k] = (frame[i, j, k] & ~((1 << n_lsb) - 1)) | int(text_bits[bit_index:bit_index + n_lsb], 2)
                            bit_index += n_lsb

            cv2.imwrite(os.path.join(temp_folder, frame_file), frame)

        fps = VideoFileClip(video_path).fps

        print("Extracting audio...")
        os.system(f'ffmpeg -i {video_path} -q:a 0 -map a temp/audio.mp3 -y -loglevel quiet')
        stego_video_path = video_path.split('.')[0] + '_stego.mkv'

        print("Combining new video and audio...")
        os.system(f'ffmpeg -framerate {fps} -i {temp_folder}%d.png -codec copy -y temp/video-only.mkv -loglevel quiet')
        os.system(f'ffmpeg -i temp/video-only.mkv -i temp/audio.mp3 -codec copy -y {stego_video_path} -loglevel quiet')

        print("Deleting temp folder...")
        if os.path.exists("./temp"):
            try:
                shutil.rmtree("./temp", onerror=self.remove_readonly)
            except OSError as e:
                print("Error: %s : %s" % ("./temp", e.strerror))

        print("Encoding completed!")
        return stego_video_path

    def remove_readonly(self, func, path, _):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    def decode_video(self, stego_video_path, num_lsb):
        try:
            print("Starting video decoding...")
            n_lsb = int(num_lsb)
            decoded_text = self.decode_lsb(stego_video_path, n_lsb)
            return decoded_text
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Function to decode text from video using LSB
    def decode_lsb(self, video_path, n_lsb):
        self.frame_extract(video_path)

        temp_folder = "./temp/"
        # frames = sorted([f for f in os.listdir(temp_folder) if f.endswith('.png')])
        frames = sorted([f for f in os.listdir(temp_folder) if f.endswith('.png')], key=lambda f: int(f.split('.')[0]))

        text_bits = ''

        for frame_file in frames:
            frame = cv2.imread(os.path.join(temp_folder, frame_file))
            print("Decoding frame {}...".format(frame_file))
            for i in range(frame.shape[0]):
                for j in range(frame.shape[1]):
                    for k in range(3):  # Iterate over the BGR channels
                        bits = format(frame[i, j, k] & ((1 << n_lsb) - 1), f'0{n_lsb}b')
                        text_bits += bits
                        if text_bits.endswith('00000000' * 8):
                            if os.path.exists("./temp"):
                                try:
                                    shutil.rmtree("./temp", onerror=self.remove_readonly)
                                except OSError as e:
                                    print("Error: %s : %s" % ("./temp", e.strerror))
                            decoded_text = ''.join([chr(int(text_bits[i:i + 8], 2)) for i in range(0, len(text_bits) - 64, 8)])
                            with open("decoded_text.txt", "w") as file:
                                file.write(decoded_text)

                            print("Decoding completed!")
                            return "Check decoded_text.txt for the decoded text."
                            # return ''.join([chr(int(text_bits[i:i+8], 2)) for i in range(0, len(text_bits) - 64, 8)])

        if os.path.exists("./temp"):
            try:
                shutil.rmtree("./temp", onerror=self.remove_readonly)
            except OSError as e:
                print("Error: %s : %s" % ("./temp", e.strerror))

        return ''

    def encode_audio(self, cover_audio_path, payload_text, num_lsb):
        with wave.open(cover_audio_path, 'rb') as audio:
            params = audio.getparams()  # Get audio parameters
            frames = bytearray(list(audio.readframes(audio.getnframes())))  # Read audio frames

        binary_payload = ''.join(format(ord(char), '08b') for char in payload_text) + '1111111111111111'  # Convert the payload text to binary and add an end delimiter
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
        byte_payload = [binary_payload[i:i + 8] for i in range(0, len(binary_payload), 8)]
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
                stego_image.thumbnail((500, 500))  # Resize the stego image
                self.stego_image = ImageTk.PhotoImage(stego_image)  # Convert the stego image to PhotoImage
                self.stego_label.config(image=self.stego_image)  # Display the stego image in the label
                messagebox.showinfo("Encoding", f"Encoding completed successfully: {stego_image_path}")  # Show a success message

            elif self.cover_path.endswith(('.mp4', '.mkv')):
                stego_video_path = self.encode_video(self.cover_path, payload_text, self.lsb_var.get())  # Encode the payload into the video
                # Create a VLC instance
                instance2 = vlc.Instance()
                # Create a VLC player
                self.player2 = instance2.media_player_new()
                # Create a new Media instance
                media2 = instance2.media_new(stego_video_path)
                # Set the player media
                self.player2.set_media(media2)
                self.stego_label.config(height=70, width=70)
                # Set the player window ID
                self.player2.set_hwnd(self.stego_label.winfo_id())
                # Play the video
                self.player2.play()
                messagebox.showinfo("Encoding", f"Encoding completed successfully: {stego_video_path}")

            elif self.cover_path.endswith('.wav'):
                stego_audio_path = self.encode_audio(self.cover_path, payload_text, self.lsb_var.get())  # Encode the payload into the audio
                messagebox.showinfo("Encoding", f"Encoding completed successfully: {stego_audio_path}")  # Show a success message
                # Create Play button for stego audio
                self.stego_play_path = stego_audio_path
                self.play_button_stego = tk.Button(self.frame, text="Play Stego Audio", command=self.play_stego_audio)
                self.play_button_stego.grid(row=5, column=1)  # Adjust row and column as per your layout
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
            elif self.cover_path.endswith(('.mp4', '.mkv')):
                decoded_text = self.decode_video(self.cover_path, self.lsb_var.get())  # Decode the payload from the image
                messagebox.showinfo("Decoding", f"Decoded text: {decoded_text}")  # Show the decoded text
            elif self.cover_path.endswith('.wav'):
                decoded_text = self.decode_audio(self.cover_path, self.lsb_var.get())  # Decode the payload from the audio
                messagebox.showinfo("Decoding", f"Decoded text: {decoded_text}")  # Show the decoded text
            else:
                messagebox.showwarning("Error", "Cover file type not supported for decoding")  # Show an error message for unsupported file types
        else:
            messagebox.showwarning("Error", "Please select a cover file")  # Show an error message if the cover file is not selected

    def play_cover_audio(self):
        pygame.mixer.music.load(self.cover_path)
        pygame.mixer.music.play()

    def play_stego_audio(self):
        pygame.mixer.music.load(self.stego_play_path)
        pygame.mixer.music.play()

if __name__ == "__main__":
    root = TkinterDnD.Tk()  # Create the main window
    app = SteganographyApp(root)  # Create an instance of the SteganographyApp class
    root.mainloop()  # Run the main loop
