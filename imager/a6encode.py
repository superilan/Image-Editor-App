"""
Steganography methods for the imager application.

This module provides all of the test processing operations (encode, decode) 
that are called by the application. Note that this class is a subclass of Filter. 
This allows us to layer this functionality on top of the Instagram-filters, 
providing this functionality in one application.

Based on an original file by Dexter Kozen (dck10) and Walker White (wmw2)

Aaron Baruch (amb565) Ilan Klimberg (idk7)
11/15/2022
"""
import a6filter


class Encoder(a6filter.Filter):
    """
    A class that contains a collection of image processing methods
    
    This class is a subclass of Filter.  That means it inherits all of the 
    methods and attributes of that class too. We do that separate the 
    steganography methods from the image filter methods, making the code
    easier to read.
    
    Both the `encode` and `decode` methods should work with the most recent
    image in the edit history.
    """
    
    def encode(self, text):
        """
        Returns True if it could hide the text; False otherwise.
        
        This method attemps to hide the given message text in the current 
        image. This method first converts the text to a byte list using the 
        encode() method in string to use UTF-8 representation:
            
            blist = list(text.encode('utf-8'))
        
        This allows the encode method to support all text, including emoji.

        The method then does the following to encode the text in the current
        image:
        
        1. Encodes an indicator of a hidden message in the first few pixels of
        the image with the code 'm' + length of text. For example, if a message 
        of length 156 bytes exists in the image, the indicator 'm156' will be 
        hidden in the first 4 pixels of the image.

        2. Then encodes the hidden message in the image by encoding each byte
        into the pixels following the indicator.
        
        If the text UTF-8 encoding requires more than 999999 bytes or the 
        picture does  not have enough pixels to store these bytes this method
        returns False without storing the message. However, if the number of
        bytes is both less than 1000000 and less than (# pixels - 10), then 
        the encoding should succeed.  So this method uses no more than 10
        pixels to store additional encoding information.
        
        Parameter text: a message to hide
        Precondition: text is a string
        """
        # You may modify anything in the above specification EXCEPT
        # The first line (Returns True...)
        # The last paragraph (If the text UTF-8 encoding...)
        # The precondition (text is a string)
        assert isinstance(text,str)
        current = self.getCurrent()
        num_pixels = len(current)
        blist = list(text.encode('utf-8'))
        num_bytes = len(blist)
        indicator = 'm' + str(len(blist)) + '!'
        if (num_bytes > 999999) or (num_pixels < num_bytes):
            return False
        elif (num_bytes < 1000000) and (num_bytes < (num_pixels - 10)):
            #encodes the indicator in the first few pixels
            for pos in range(len(indicator)):
                n = indicator[pos].encode('utf-8')
                n = list(n)
                pixel = self._encode_pixel(n[0],current[pos])
                current[pos] = pixel
            #encodes the message in the following pixels of the image
            for pos in range(len(blist)):
                pixel = self._encode_pixel(blist[pos],\
                    current[pos+len(indicator)])
                current[pos+len(indicator)] = pixel
            return True

    def decode(self):
        """
        Returns the secret message (a string) stored in the current image. 
        
        The message should be decoded as a list of bytes. Assuming that a list
        blist has only bytes (ints in 0.255), you can turn it into a string
        using UTF-8 with the decode method:
            
            text = bytes(blist).decode('utf-8')

        The function first uses the _has_message helper to determine whether
        there is a hidden message. If a message is detected, it first decodes
        the indicator in the first few pixels.

        The length of the hidden message (the number of bytes in the message) 
        is extracted from the indicator to determine when the message will end.

        The function extracts the encoded byte from each pixel until the length
        of the message ends, and then decodes the bytes to determine and return
        the hidden message. 
        
        If no message is detected, or if there is an error in decoding the
        message, this method returns None
        """
        # You may modify anything in the above specification EXCEPT
        # The first line (Returns the secret...)
        # The last paragraph (If no message is detected...)
        if self._has_message() == False:
            return None
        blist = []
        indicator = ' '
        i = 0
        while indicator[-1] != '!':
            blist.append(self._decode_pixel(i))
            indicator = bytes(blist).decode('utf-8')
            i = i + 1
        message_len = int(indicator[1:-1])
        blist = []
        for i in range(message_len):
            byte = self._decode_pixel(i+len(indicator))
            blist.append(byte)
        message = bytes(blist).decode('utf-8')
        return message
  
    # HELPER METHODS
    def _has_message(self):
        """
        Return: True if it detects the indicator 'm' + length of message + '!',
        False otherwise (if it doesn't detect the indicator, or encounters an
        error).

        This function detects if there is an indicator for a hidden message,
        and assumes that an indicator can fill up to no more than the first
        10 pixels of the image.
        """
        blist = []
        try:
            for i in range(11):
                blist.append(self._decode_pixel(i))
                c = bytes(blist)
                string = c.decode('utf-8')
                if string[0] == 'm' and string[-1] == '!':
                    return True
        except:
            return False
        return False

    def _decode_pixel(self, pos):
        """
        Return: the number n hidden in pixel pos of the current image.
        
        This function assumes that the value was a 3-digit number encoded as 
        the last digit in each color channel (e.g. red, green and blue).
        
        Parameter pos: a pixel position
        Precondition: pos is an int with  0 <= p < image length (as a 1d list)
        """
        # This is helper. You do not have to use it. You are allowed to change it.
        # There are no restrictions on how you can change it.
        assert isinstance(pos,int) and pos >= 0 and pos < len(self.getCurrent())
        rgb = self.getCurrent()[pos]
        red   = rgb[0]
        green = rgb[1]
        blue  = rgb[2]
        return  (red % 10) * 100  +  (green % 10) * 10  +  blue % 10

    def _encode_pixel(self, byte, pixel):
        """
        Return: the pixel of the current image encoded with byte
        
        This function changes the least significant digit of each color 
        component in pixel to each digit of the byte.

        The function must ensure that the color components remain in the range
        0..255. In the case that the color component exceeds 255, the funciton
        will decrement the color component by 10 to remain in range with the
        digit of the byte still in the position of the least significant digit
        of the color component.
        
        Parameter byte: The byte
        Precondition: byte is an int in the range 0..255

        Parameter pixel: The pixel value
        Precondition: pixel is a 3-element tuple (r,g,b) of ints in 0..255
        """
        str_byte = str(byte)
        str_pixel = str(pixel)
        if len(str_byte) == 1:
            str_byte = '00' + str_byte
        if len(str_byte) == 2:
            str_byte = '0' + str_byte
        red = str_pixel[1:str_pixel.find(',')]
        green = str_pixel[str_pixel.find(',')+2:\
            str_pixel.find(',',str_pixel.find(',')+1)]
        blue = str_pixel[str_pixel.find(',',str_pixel.find(',')+1)+2:\
            str_pixel.find(')')]
        for i in range(len(str_byte)):
            if i == 0:
                red = red[:-1] + str_byte[0]
            elif i == 1:
                green = green[:-1] + str_byte[1]
            elif i == 2:
                blue = blue[:-1] + str_byte[2]
        if int(red) > 255:
            red = int(red) - 10
        if int(green) > 255:
            green = int(green) - 10
        if int(blue) > 255:
            blue = int(blue) - 10
        pixel_result = (int(red), int(green), int(blue))
        return pixel_result