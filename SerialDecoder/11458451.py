#Q1 Answer: 430
#Q2 Answer: 13
#Q3 Answer: 2021, 10, 25 and 2016, 10, 19 

# Import the required libraries
from datetime import datetime, timedelta
import csv

#Open the binary input file
input_file = open("binaryFileC_1(1).bin", 'rb')

#Initialize variables
start_decoding = False # Flag to indicate when to start decoding
current_byte = 1 # Counter to keep track of the current byte
prev_byte = None # Variable to store the previous byte
frame_counter = 0 # Counter to keep track of the number of frames
corrupt_frame_counter = 0 # Counter to keep track of the number of corrupt frames
byte_1 = None # Variable to store the first byte of for 16-bit value addition
byte_list = [] # List to store the 8 bytes for 64-bit value addition
byte_check = [] # List to store the bytes for checksum calculation
dates = [] # List to store the dates of corrupt messages
data = [] # List to store the decoded data



#Read the first byte and loop as long as there is always another byte available
byte = input_file.read(1)

while byte:

    if start_decoding and current_byte != 26:
        byte_check.append(byte) # Add the current byte to the list for checksum calculation

    if start_decoding:
        current_byte += 1  # Increment the byte counter

    #  If start of frame found, allow the frame to start with either ~ or ~~.
    if (current_byte == 1 or current_byte == 2) and start_decoding == True:
        byte_value = 0
        if byte == b'~':
            byte_value = '~~'
        data.append(byte_value)

    if current_byte == 2 and start_decoding == True:
        byte_value = 0
        if byte == b'~':
            byte_value = '~'
        data.append(byte_value)
    
    #  Find Start of frame and start decoing
    if byte == b'~' and prev_byte == b'~' and start_decoding == False: 
        start_decoding = True
        current_byte = 2 
        data.append("~~")
        byte_check.append(byte)  # Add the current byte to the list for checksum calculation
        byte_check.append(prev_byte)  # Add the current byte to the list for checksum calculation


    if current_byte in range(3, 6):
        byte_value = int.from_bytes(byte, byteorder='big')
        data.append(byte_value)
    
        

    elif current_byte == 6:
        byte_value = int.from_bytes(byte, byteorder='big')
        data.append(byte_value)
        


    elif current_byte == 7:
        byte_value = int.from_bytes(byte, byteorder='big')
        data.append(byte_value)
       

    elif current_byte == 8:
    # check if byte is "P"
        byte_value = 0
        if byte == b'P':
            byte_value = 'P'
        data.append(byte_value)
  

    # combine two 8 bit bytes into one 16 bit value
    # Use bit shifting and bitwise OR to combine the bytes
    elif current_byte in range(9, 13):
        if byte_1 is None:
            byte_1 = byte  # Keep the first byte
        else:
            # Combine the first(MSB) and second(LSB) byte into a 16-bit value
            # Shift the first byte 8 bits to the left and combine it with the second byte
            combined_value = (int.from_bytes(byte_1, 'big') << 8) | int.from_bytes(byte, 'big', signed=False)
            data.append(combined_value)
            byte_1 = None  # Reset for the next pair

    elif current_byte in range(13, 15):
        if byte_1 is None:
            byte_1 = byte  # Keep the first byte
        else:
            # Combine the first(LSB) and second(MSB) byte into a 16-bit value
            # Shift the first byte 8 bits to the right and combine it with the second byte
            byte_value = (int.from_bytes(byte_1, 'big') >> 8) | int.from_bytes(byte, 'big', signed=True)
            data.append(byte_value)
            byte_1 = None  # Reset for the next frame


    elif current_byte in range(15, 17):
    # convert byte to temp value
        conversion_table = {
            0xA0: 30.0, 0xA1: 30.1, 0xA2: 30.2, 0xA3: 30.3,
            0xA4: 30.4, 0xA5: 30.5, 0xA6: 30.6, 0xA7: 30.7,
            0xA8: 30.8, 0xA9: 30.9, 0xAA: 31.0, 0xAB: 31.1,
            0xAC: 31.2, 0xAD: 31.3, 0xAE: 31.4, 0xAF: 31.5,
            0xB0: 31.6, 0xB1: 31.7, 0xB2: 31.8, 0xB3: 31.9,
            0xB4: 32.0, 0xB5: 32.1, 0xB6: 32.2, 0xB7: 32.3,
            0xB8: 32.4, 0xB9: 32.5, 0xBA: 32.6, 0xBB: 32.7,
            0xBC: 32.8, 0xBD: 32.9, 0xBE: 33.0, 0xBF: 33.1,
            0xC0: 33.2, 0xC1: 33.3, 0xC2: 33.4, 0xC3: 33.5,
            0xC4: 33.6, 0xC5: 33.7, 0xC6: 33.8, 0xC7: 33.9,
            0xC8: 34.0, 0xC9: 34.1, 0xCA: 34.2, 0xCB: 34.3,
            0xCC: 34.4, 0xCD: 34.5, 0xCE: 34.6, 0xCF: 34.7,
            0xD0: 34.8, 0xD1: 34.9, 0xD2: 35.0, 0xD3: 35.1,
            0xD4: 35.2, 0xD5: 35.3, 0xD6: 35.4, 0xD7: 35.5,
            0xD8: 35.6, 0xD9: 35.7, 0xDA: 35.8, 0xDB: 35.9,
            0xDC: 36.0, 0xDD: 36.1, 0xDE: 36.2, 0xDF: 36.3
        }
        byte_value = conversion_table.get(int.from_bytes(byte, 'big'), "0.0")
        data.append(byte_value)


    elif current_byte == 17:
        # check if byte is "T"
        byte_value = 0
        if byte == b'T':
            byte_value = 'T'    
        data.append(byte_value)
    

    elif current_byte in range(18, 26):
        # combine 8 bytes into a single 64 bit value
        byte_list.append(byte)  # Add the current byte to the list

        # Once we have collected 8 bytes, combine them into a 64-bit value
        if len(byte_list) == 8:
            # add all 8 bytes in byte_list into a single 64 bit value
            bytes_combined = b''.join(byte_list)
            timestamp =  int.from_bytes(bytes_combined, byteorder='big', signed=False)
            data.append(timestamp)
            byte_list = []  # Reset for the next group


    #Checksum calculation
    # Sum up all the values except the checksum byte itself
    elif current_byte == 26:

        # Calculate the checksum
        sum_values = sum(int.from_bytes(b, 'big') for b in byte_check)
        modulo_result = sum_values % 256
        checksum = 255 - modulo_result

        # Read the checksum byte
        checksum_byte = int.from_bytes(byte, 'big')
        data.append(checksum_byte)

        # Compare the calculated checksum with the checksum byte
        if checksum == checksum_byte:
            pass # Checksum is correct
        else:
            corrupt_frame_counter += 1

            # Find Calendar Date of corrupt messages
            cutoff_date = datetime(2024, 2, 6)
            cutoff_timestamp = cutoff_date.timestamp()
            try:
                seconds = timestamp / 1e6  # Convert microseconds to seconds
                date_time = datetime(1970, 1, 1) + timedelta(seconds=seconds)
                # Check if the date is before the cutoff date and add it to the list
                if date_time > cutoff_date:
                    pass
                else:
                    dates.append(date_time)
            except OverflowError:
                pass
            
        # Reset the list for the next frame
        byte_check = []
        # Reset current_byte for the next frame
        start_decoding = False
        current_byte = 1
        frame_counter += 1  # Increment the frame counter
         
    prev_byte = byte  # Save the current byte for the next iteration
    byte = input_file.read(1)  # Read the next byte


# Create a new list to store the chunks of 16 byte data frames
chunks = [data[i:i + 15] for i in range(0, len(data), 15)]

# Write the chunks to a CSV file
with open('11458451.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    for chunk in chunks:
        writer.writerow(chunk)


input_file.close()
#print("Number of Frames: ", frame_counter)
#print("Number of Corrupt Frames: ", corrupt_frame_counter)
#print("Calendar Date of Messages: ", dates)
