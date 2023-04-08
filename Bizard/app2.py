import streamlit as st
import easyocr
import cv2
import numpy as np
import mysql.connector
from mysql.connector import Error

# Load EasyOCR reader
reader = easyocr.Reader(['en'])

# Create a function to extract information from image
def extract_info(img):
    # Convert the image to grayscale
    img_cv_grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Extract text using EasyOCR
    result = reader.readtext(img_cv_grey)
    # Create an empty dictionary to store the extracted information
    extracted_info = {'Name': '', 'Phone': '', 'Email': ''}
    # Loop through the result and extract information
    for detection in result:
        text = detection[1]
        if 'name' in text.lower() and not extracted_info['Name']:
            extracted_info['Name'] = text
        elif 'phone' in text.lower() and not extracted_info['Phone']:
            extracted_info['Phone'] = text
        elif 'email' in text.lower() and not extracted_info['Email']:
            extracted_info['Email'] = text
    # Return the extracted information
    return extracted_info

# Create a function to display image and extracted information
def show_info(img_path):
    # Load the image
    img = cv2.imread(img_path)
    # Display the image
    st.image(img, channels='BGR')
    # Extract information from the image
    extracted_info = extract_info(img)
    # Display the extracted information in a table
    st.table([extracted_info])

# Create a Streamlit app
def app():
    # Display the title
    st.title('Business Card Reader')
    # Create a file uploader
    uploaded_file = st.file_uploader("Choose an image...", type=['jpg', 'jpeg', 'png'])
    # Check if a file was uploaded
    if uploaded_file is not None:
        # Read the uploaded file
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        # Display the extracted information
        extracted_info = extract_info(img)
        show_info(uploaded_file)
        # Connect to MySQL database
        connection = mysql.connector.connect(
            host='localhost',
            database='card_extraction',
            user='root',
            password='12345'
        )
        if connection.is_connected():
            # Insert the extracted information into MySQL database
            mycursor = connection.cursor()
            sql = "INSERT INTO cards5 (name, phone, email, image) VALUES (%s, %s, %s, %s)"
            val = (extracted_info['Name'], extracted_info['Phone'], extracted_info['Email'], file_bytes.tobytes())
            mycursor.execute(sql, val)
            connection.commit()
            st.success('Information saved to database')
            # Close database connection
            connection.close()
            st.info('Database connection closed')

# Run the app
app()