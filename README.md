# activate venvv environment unless u install these modules stated below already in yr local
venv\Scripts\activate
# install Tkinter
pip install tkinker
# install Pillow
pip install pillow
# install cv2
pip install opencv-python
# run program
python steganography_app.py
# Testing
1. upload duck image(select cover file) and encode the hidden text(select payload file) into the duck image.
2. set the LSBs you wanna encode.
3. it will produce a stego image.
4. upload the stego image and decode it based on the LSB you set.
5. result output would be based on the hidden text file.
