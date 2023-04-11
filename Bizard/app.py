import streamlit as st
import mysql.connector
import cv2
import easyocr
import urllib.request
import numpy as np
import pandas as pd


mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="12345",
  database="card_extraction"
)

# Create a table to store image and text
mycursor = mydb.cursor()
mycursor.execute("CREATE TABLE IF NOT EXISTS cards_detection6 (id INT AUTO_INCREMENT PRIMARY KEY,name VARCHAR(255),job_title VARCHAR(255),phone1 VARCHAR(255),phone2 VARCHAR(255),website VARCHAR(255),email VARCHAR(255),address VARCHAR(255),company_name VARCHAR(255),image LONGBLOB)")

# Set up EasyOCR reader
reader = easyocr.Reader(['en'])

# Streamlit app

st.title("Extract Text from Image and Save to Database")

uploaded_file = st.file_uploader("Upload a business card image", type=["jpg", "jpeg", "png"])

# Create a sidebar menu with options to add, view, update, and delete business card information
menu = ['Insert', 'View', 'Update', 'Delete']
choice = st.sidebar.selectbox("Select an option", menu)

if choice == 'Insert':
    if uploaded_file is not None:
        # Read the image using OpenCV
        image = cv2.imdecode(np.fromstring(uploaded_file.read(), np.uint8), 1)
        # Display the uploaded image
        st.image(image, caption='Uploaded business card image', use_column_width=True)
        # Create a button to extract information from the image
        if st.button('Extract Information'):
            # Call the function to extract the information from the image
            bounds = reader.readtext(image, detail=0)
            # Convert the extracted information to a string
            text = "\n".join(bounds)
            # Insert the extracted information and image into the database
            sql = "INSERT INTO cards_detection6(name, job_title, phone1, phone2, website, email, address, company_name,image) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s,%s)"
            val = (bounds[0], bounds[1], bounds[2], bounds[3], bounds[4], bounds[5], bounds[6], bounds[7],cv2.imencode('.jpg', image)[1].tobytes())
            mycursor.execute(sql, val)
            mydb.commit()
            # Display a success message
            st.success("Business card information added to database.")
elif choice == 'View':
    # Display the stored business card information
    mycursor.execute("SELECT * FROM cards_detection6")
    result = mycursor.fetchall()
    df = pd.DataFrame(result, columns=['id','name', 'job_title', 'phone1', 'phone2', 'website', 'email', 'address', 'company_name','image'])
    st.write(df)

elif choice == 'Update':
    # Create a dropdown menu to select a business card to update
    mycursor.execute("SELECT id, name FROM cards_detection6")
    result = mycursor.fetchall()
    business_cards = {}
    for row in result:
        business_cards[row[1]] = row[0]
    selected_card_name = st.selectbox("Select a business card to update", list(business_cards.keys()))
    
    # Get the current information for the selected business card
    mycursor.execute("SELECT * FROM cards_detection6 WHERE name=%s", (selected_card_name,))
    result = mycursor.fetchone()
    mycursor.fetchall()

    # Display the current information for the selected business card
    st.write("Name:", result[1])
    st.write("Job Title:", result[2])
    st.write("Phone1:", result[3])
    st.write("Phone2:", result[4])
    st.write("Website:", result[5])
    st.write("Email:", result[6])
    st.write("Address:", result[7])
    st.write("Comapny name:", result[8])

    # Get new information for the business card
    name = st.text_input("Name", result[1])
    job_title = st.text_input("Job Title", result[2])
    phone1 = st.text_input("Phone1", result[3])
    phone2 = st.text_input("Phone2", result[4])
    website = st.text_input("Website", result[5])
    email = st.text_input("Email", result[6])
    address = st.text_input("Address", result[7])
    company_name = st.text_input("Company Name", result[8])

    # Create a button to update the business card
    if st.button("Update Business Card"):
        # Update the information for the selected business card in the database
        mycursor.execute("UPDATE cards_detection6 SET name=%s, job_title=%s, phone1=%s, phone2=%s, website=%s, email=%s, address=%s, company_name=%s WHERE name=%s", 
                             (name, job_title, phone1, phone2, website, email, address, company_name, selected_card_name))
        mydb.commit()
        st.success("Business card information updated in database.")
elif choice == 'Delete':
    # Create a dropdown menu to select a business card to delete
    mycursor.execute("SELECT id, name FROM cards_detection6")
    result = mycursor.fetchall()
    business_cards = {}
    for row in result:
        business_cards[row[0]] = row[1]
    selected_card_id = st.selectbox("Select a business card to delete", list(business_cards.keys()), format_func=lambda x: business_cards[x])

    # Get the name of the selected business card
    mycursor.execute("SELECT name FROM cards_detection6 WHERE id=%s", (selected_card_id,))
    result = mycursor.fetchone()
    if result:
      selected_card_name = result[0]

    # Display the current information for the selected business card
      st.write("Name:", selected_card_name)
    # Display the rest of the information for the selected business card

    # Create a button to confirm the deletion of the selected business card
    if st.button("Delete Business Card"):
        mycursor.execute("DELETE FROM cards_detection6 WHERE name=%s", (selected_card_name,))
        mydb.commit()
        st.success("Business card information deleted from database.")
        
        
        
        
        
        
        
        
