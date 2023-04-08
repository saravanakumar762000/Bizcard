import streamlit as st
import easyocr
import cv2
import numpy as np
import mysql.connector
import io
from PIL import Image
import cv2
import base64

# Set up MySQL connection
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="12345",
  database="card_extraction"
)

mycursor = mydb.cursor()

reader = easyocr.Reader(['en'])

mycursor.execute("CREATE TABLE IF NOT EXISTS business_card8 (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), email VARCHAR(255), phone VARCHAR(255), address VARCHAR(255), image BLOB)")

uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])
menu = ['Insert Data', 'Display Data', 'Update Data', "Delete Data"]
choose = st.sidebar.selectbox("Select An Option", menu)

if choose == 'Insert Data':
  if uploaded_file is not None:
    img_bytes = uploaded_file.read()
    img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
    result = reader.readtext(img)

        # Extract the relevant information from the OCR result
    name, phone, email,address = "", "", "",""
    for r in result:
            text = r[1]
            if 'name' not in name.lower() and any(x.isalpha() for x in text):
                name = text
            elif 'phone' not in phone.lower() and any(x.isdigit() for x in text):
                phone = text
            elif 'email' not in email.lower() and '@' in text:
                email = text
            elif "address" not in address.lower and 'st' in text:
                address=text
        # Display the extracted information
    st.write("Name:", name)
    st.write("Phone:", phone)
    st.write("Email:", email)

        # Save the image and information to the database
    if st.button("Save"):
        mycursor = mydb.cursor()
        encoded_string = base64.b64encode(img_bytes).decode('utf-8')
        sql = "INSERT INTO  business_card8 (name, phone, email,address, image) VALUES (%s, %s, %s, %s,%s)"
        val = (name, phone, email,address,encoded_string)
        mycursor.execute(sql, val)
        mydb.commit()
        st.success("Data saved successfully")
        mycursor.close()
