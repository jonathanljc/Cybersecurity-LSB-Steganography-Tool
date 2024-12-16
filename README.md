# 🛡️ GUI-Based LSB Steganography and Steganalysis Program
## 📄 Project Overview

The **GUI-based LSB Steganography and Steganalysis Program** was developed as part of **INF2005 - Cybersecurity Fundamentals ACW1**. It enables users to encode and decode text payloads into various cover objects, such as images, audio, and video files. Key features include:

- **Support for multiple cover object types**: BMP, PNG, WAV, MP4.
- **Selectable number of LSBs (1 to 8)** for encoding and decoding.
- **Drag-and-drop functionality** for selecting cover objects, payloads, and stego objects.
- **Real-time playback and display** of cover and stego objects for comparison.
- **Error handling** for payload size limits relative to the cover object.

---

# 🚀 Setup and Installation Guide

## 🖥️ Virtual Environment Setup
1. **Activate Virtual Environment** (if not already installed):
   ```bash
   venv\Scripts\activate
---
2. **Install Required Modules** (if not already installed):
```bash
pip install tkinker        # For GUI components
pip install pillow         # For image processing
pip install opencv-python  # For image encoding/decoding
pip install python-vlc     # For video playback in the GUI
pip install moviepy        # For video processing
pip install tkinterdnd2    # For drag-and-drop functionality
pip install pygame         # For audio playback
```
---

## 📦 Installing FFmpeg

### 🪟 For Windows:
Follow this guide: [Install FFmpeg on Windows](https://www.wikihow.com/Install-FFmpeg-on-Windows).

### 🍎 For Mac:
Install via Homebrew:
```bash
brew install ffmpeg
```
---

## ▶️ Running the Program
```bash
python lsb_steganography.py
```
---

## 🛠️ Testing Steps
Encode Hidden Text:

- Upload a cover image (e.g., duck.jpg).
- Upload a payload file containing the hidden text you wish to encode.
- Specify the number of LSBs (Least Significant Bits) to encode.
- The application will generate a stego image.

Decode Hidden Text:

- Upload the stego image.
- Set the same number of LSBs used during encoding.
- The application will output the decoded hidden text.

---

## 🎓 Contributors

| **Name**                      | **ID**       | **Email**                          |
|-------------------------------|--------------|------------------------------------|
| Felix Chang                   | 2301105      | 2301105@sit.singaporetech.edu.sg   |
| Dawn Aw Tay Rui Qi            | 2301096      | 2301096@sit.singaporetech.edu.sg   |
| Lim Jing Chuan, Jonathan      | 2300923      | 2300923@sit.singaporetech.edu.sg   |
| Elroy Lee                     | 2300950      | 2300950@sit.singaporetech.edu.sg   |
| Ong Jia En, Darryl            | 2301402      | 2301402@sit.singaporetech.edu.sg   |
| Ong Yong Sheng                | 2301123      | 2301123@sit.singaporetech.edu.sg   |

