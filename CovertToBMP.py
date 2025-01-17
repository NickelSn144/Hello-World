from PIL import Image
import numpy as np
import time

def main():
    image_index = 5 # number of images to be converted
    # Loop to convert multiple images with numbering after same name
    for index in range(image_index):
        img = Image.open('image({}).jpeg'.format(index))
        ary = np.array(img)

        # Split the three channels
        r,g,b = np.split(ary,3,axis=2)
        r=r.reshape(-1)
        g=r.reshape(-1)
        b=r.reshape(-1)

        # Standard RGB to 1-bit
        # Merging RGB pixels with different weights and coverting to 1-bit
        bitmap = ((0.299*r + 0.587*g + 0.114*b) > 128)*1
        # Reshaping into 2d array
        bitmap = np.array(bitmap).reshape([ary.shape[0], ary.shape[1]])
        # Seperate function to write data into 1-bit BMP format
        write_bmp("image({}).bmp".format(index), bitmap.tolist())

def write_bmp(filename, pixels):
    """Creates and writes a grayscale BMP file
    Args:
        filename: The name of the BMP file to be crated.
        pixels: A rectangular image stored as a sequence of rows.
            Each row must be an iterable series of integers in the range 0-255.
    Raises:
        OSError: If the file couldn't be written.
    """
    height = len(pixels)
    width = len(pixels[0])

    with open(filename, 'wb') as bmp:
        # BMP Header
        bmp.write(b'BM')

        size_bookmark = bmp.tell()  # The next four bytes hold the filesize as a 32-bit
        bmp.write(b'\x00\x00\x00\x00')  # little-endian integer. Zero placeholder for now.

        bmp.write(b'\x00\x00')  # Unused 16-bit integer - should be zero
        bmp.write(b'\x00\x00')  # Unused 16-bit integer - should be zero

        pixel_offset_bookmark = bmp.tell()  # The next four bytes hold the integer offset
        bmp.write(b'\x00\x00\x00\x00')  # to the pixel data. Zero placeholder for now.

        # Image header
        bmp.write(b'\x28\x00\x00\x00')  # Image header size in bytes - 40 decimal
        bmp.write(_int32_to_bytes(width))  # Image width in pixels
        bmp.write(_int32_to_bytes(height))  # Image height in pixels
        bmp.write(b'\x01\x00')  # Number of image planes
        bmp.write(b'\x01\x00')  # Bits per pixel 8 for grayscale
        bmp.write(b'\x00\x00\x00\x00')  # No compression
        bmp.write(b'\x00\x00\x00\x00')  # Zero for uncompressed images
        bmp.write(b'\x00\x00\x00\x00')  # Unused pixels per meter
        bmp.write(b'\x00\x00\x00\x00')  # Unused pixels per meter
        bmp.write(b'\x00\x00\x00\x00')  # Use whole color table
        bmp.write(b'\x00\x00\x00\x00')  # All colors are important
        bmp.write(b'\x00\x00\x00\x00')  # Color palette for 1 bit
        bmp.write(b'\xff\xff\xff\x00')  # #00000 (black) and #ffffff (white)

        # Pixel data
        pixel_data_bookmark = bmp.tell()
        for row in reversed(pixels):    # BMP files are bottom to top
            while(len(row) % 32 != 0):  # padding added; each row should be a multiple of 4 byte
                row.append(0)
            # A new integer list is created by joining 8 1-bit elemnets of input pixel row
            row_data = [int(''.join(str(x) for x in row[i : i + 8]), 2) for i in range(0, len(row), 8)]
            row_data_bytes = bytes(row_data) #binary conversion of int values
            bmp.write(row_data_bytes)

        # End of file
        eof_bookmark = bmp.tell()

        # Fill in file size placeholder
        bmp.seek(size_bookmark)
        bmp.write(_int32_to_bytes(eof_bookmark))

        # Fill in pixel
        bmp.seek(pixel_offset_bookmark)
        bmp.write(_int32_to_bytes(pixel_data_bookmark))


def _int32_to_bytes(i):
    """Convert an integer to four bytes in little-endian format."""
    return bytes((i & 0xff,
                  i >> 8 & 0xff,
                  i >> 16 & 0xff,
                  i >> 24 & 0xff))

if __name__ == '__main__':
    main()