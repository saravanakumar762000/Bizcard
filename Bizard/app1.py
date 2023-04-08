import streamlit as st
import easyocr
import mysql.connector

# Set up database connection
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="12345",
  database="card_extraction"
)
mycursor = mydb.cursor()
mycursor.execute("CREATE TABLE IF NOT EXISTS data (id INT AUTO_INCREMENT PRIMARY KEY,name VARCHAR(255),phone VARCHAR(255),email VARCHAR(255),address VARCHAR(255), image LONGBLOB)")
# Set up EasyOCR reader
reader = easyocr.Reader(['en'])

# Define function to extract name, phone number, and email from text
def extract_info(text):
    name = ""
    phone = ""
    email = ""
    address=""
    for word in text.split():
        if "@" in word:
            email = word
        elif len(word) == 10 and word.isdigit():
            phone = word
        elif len(word) > len(name) and word[0].isupper():
            name = word
        elif "address" in word.lower() or "location" in word.lower() or "street" in word.lower():
          address = word
    return name, phone, email,address

# Define Streamlit app
def app():
    # Title
    st.title("Extract Info from Image")

    # Upload image
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg","jpeg","png"])
    
    # Process image and extract info
    if uploaded_file is not None:
        img = uploaded_file.read()
        result = reader.readtext(img)
        text = " ".join([res[1] for res in result])
        name, phone, email,address = extract_info(text)
        
        # Show extracted info
        st.write(f"Name: {name}")
        st.write(f"Phone: {phone}")
        st.write(f"Email: {email}")
        st.write(f"Address: {address}")
        
        # Insert info into database
        mycursor = mydb.cursor()
        sql = "INSERT INTO data (name, phone, email,address, image) VALUES (%s, %s, %s, %s,%s)"
        val = (name, phone, email,address, img)
        mycursor.execute(sql, val)
        mydb.commit()
        st.write("Data inserted successfully!")
        
# Run app
if __name__ == '__main__':
    app()