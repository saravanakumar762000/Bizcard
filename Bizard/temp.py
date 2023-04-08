import streamlit as st
import mysql.connector
import cv2
import easyocr
import urllib.request
import numpy as np

# Connect to MySQL database
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="12345",
  database="card_extraction"
)

# Create a table to store image and text
mycursor = mydb.cursor()
mycursor.execute("CREATE TABLE IF NOT EXISTS image_text (id INT AUTO_INCREMENT PRIMARY KEY, image LONGBLOB, text VARCHAR(255))")

# Set up EasyOCR reader
reader = easyocr.Reader(['en'])

# Streamlit app
def app():
    st.title("Extract Text from Image and Save to Database")

    # Upload image file
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # Resize image
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        resized_img = cv2.resize(img, (640, 480))

        # Display resized image
        st.image(resized_img, caption="Resized image", use_column_width=True)

        # Extract text from image
        result = reader.readtext(resized_img)

        # Display extracted text
        text = ""
        for r in result:
            text += r[1] + " "
        st.write("Extracted Text: ", text)

        # Store image and text in database
        sql = "INSERT INTO image_text (image, text) VALUES (%s, %s)"
        val = (cv2.imencode('.jpg', resized_img)[1].tobytes(), text)
        mycursor.execute(sql, val)
        mydb.commit()
        st.success("Image and Text Saved to Database!")

# Run Streamlit app
if __name__ == '__main__':
    app()