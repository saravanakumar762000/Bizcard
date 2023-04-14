import mysql.connector
import cv2
import easyocr
import urllib.request
import numpy as np
import pandas as pd
import streamlit as st
import re
from io import BytesIO
from PIL import Image,ImageDraw
import matplotlib.pyplot as plt
import os
st.set_page_config(page_title="BizCardX: Extracting Business Card Data with OCR", layout="wide")
st.markdown(
    """
    <style>
    body {
        background-color: blue;
    }
    </style>
    """,
    unsafe_allow_html=True
)

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="12345",
  database="card_extraction"
)

# Create a table to store image and text
mycursor = mydb.cursor(buffered=True)
mycursor.execute('''CREATE TABLE IF NOT EXISTS cards_detection13
                   (id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    company_name TEXT,
                    name TEXT,
                    designation TEXT,
                    mobile_number VARCHAR(50),
                    email TEXT,
                    website TEXT,
                    area TEXT,
                    city TEXT,
                    state TEXT,
                    pincode VARCHAR(10),
                    image LONGBLOB
                    )''')

# Set up EasyOCR reader
reader = easyocr.Reader(['en'])

# Streamlit app

st.title("Extract Text from Image and Save to Database")




menu = ['Home','Insert',  'Update', 'Delete']
choice = st.sidebar.selectbox("Select an option", menu)
if choice =='Home':
    with st.container():
        st.subheader("Hi, I am Saravana:")
        st.title("A Data Scientist")
        
    with st.container():
        st.write("---")
        st.title("The Project:")
        st.write("##")
        st.write(
            """
            This,allows users toupload an image of a business card and extract relevant information from it using
            easyOCR. The extracted information should include the company name, card holder
            name, designation, mobile number, email address, website URL, area, city, state,
            and pin code. 
            The extracted information should then be displayed in the application's
            graphical user interface (GUI).
            In addition, the application should allow users to save the extracted information into
            a database along with the uploaded business card image. The database should be
            able to store multiple entries, each with its own business card image and extracted
            information.
            
            """
            
            
            )
        
if choice == 'Insert':
    uploaded_file = st.file_uploader("Upload a business card image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        def save_card(uploaded_file):
          filename = os.path.join("uploaded_files", uploaded_file.name)
          if not os.path.exists("uploaded_files"):
            os.makedirs("uploaded_files")
          with open(filename, "wb") as f:
            f.write(uploaded_file.getbuffer())
        save_card(uploaded_file)
        
        
        # Read the image using OpenCV
        
        
        def image_preview(image,res): 
            fig, ax = plt.subplots()
            ax.imshow(image)
    
            for (bbox, text, prob) in res:
        # unpack the bounding box
                  (tl, tr, br, bl) = bbox
                  rect = plt.Rectangle(tl, br[0]-tl[0], br[1]-tl[1],linewidth=1,edgecolor='r',facecolor='none')
                  ax.add_patch(rect)
                  ax.text(tl[0], tl[1]-10, text, fontsize=10, color='r', fontweight='bold')
    
            plt.show()
        # Display the uploaded image
        col1,col2=st.columns(2,gap="large")
        with col1:
            st.image(uploaded_file, caption='Uploaded business card image', use_column_width=True)
        with col2:
           
            saved_img = os.getcwd()+ "\\" + "uploaded_files"+ "\\"+ uploaded_file.name
            image=cv2.imread(saved_img)
            res=reader.readtext(saved_img)
            st.pyplot(image_preview(image,res))
        
       
        saved_img = os.getcwd()+ "\\" + "uploaded_files"+ "\\"+ uploaded_file.name
        result = reader.readtext(saved_img,detail = 0,paragraph=False)
        def img_to_binary(file):
            # Convert image data to binary format
            with open(file, 'rb') as file:
                binaryData = file.read()
            return binaryData
        details={"company_name":[],
                 "name":[],
                 "designation":[],
                 "mobile_no":[],
                 "email":[],
                 "website":[],
                 "email":[],
                 "website":[],
                 "area":[],
                 "city":[],
                 "state":[],
                 "pincode":[],
                 "image": img_to_binary(saved_img)
                 } 
        for k,v in enumerate(result):
            
            if "www " in v.lower() or "www."in v.lower():
                details["website"].append(v)
            elif "WWW" in v:
                details["website"]=result[4]+"."+result[5]
            elif "@" in v:
                details["email"].append(v)
            elif"-" in v:
                details["mobile_no"].append(v)
                if len(details["mobile_no"])==2:
                    details["mobile_no"]="&".join(details["mobile_no"])
            elif k==len(result)-1:
                details["company_name"].append(v)
            elif k==0:
                details["name"].append(v)
            elif k==1:
                details["designation"].append(v)
                
            if re.findall('^[0-9].+, [a-zA-Z]+',v):
                    details["area"].append(v.split(',')[0])
            elif re.findall('[0-9] [a-zA-Z]+',v):
                    details["area"].append(v)

                # To get CITY NAME
            match1 = re.findall('.+St , ([a-zA-Z]+).+', v)
            match2 = re.findall('.+St,, ([a-zA-Z]+).+', v)
            match3 = re.findall('^[E].*',v)
            if match1:
                    details["city"].append(match1[0])
            elif match2:
                    details["city"].append(match2[0])
            elif match3:
                    details["city"].append(match3[0])

                # To get STATE
            state_match = re.findall('[a-zA-Z]{9} +[0-9]',v)
            if state_match:
                     details["state"].append(v[:9])
            elif re.findall('^[0-9].+, ([a-zA-Z]+);',v):
                    details["state"].append(v.split()[-1])
            if len(details["state"])== 2:
                    details["state"].pop(0)

                # To get PINCODE        
            if len(v)>=6 and v.isdigit():
                    details["pincode"].append(v)
            elif re.findall('[a-zA-Z]{9} +[0-9]',v):
                    details["pincode"].append(v[10:]) 
        
        def create_df(details):
            df=pd.DataFrame(details)
            return df
        df=create_df(details)
        st.write(df)
        
        if st.button("Insert to database"):
             for i,row in df.iterrows():
                 sql="""INSERT INTO  cards_detection13(company_name,name,designation,mobile_number,email,website,area,city,state,pincode,image)
                         VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                  
                   
                 mycursor.execute(sql,tuple(row))
                 mydb.commit()
             st.success("Data Inserted successfully")

elif choice == 'Update':
    # Create a dropdown menu to select a business card to update
    mycursor.execute("SELECT name FROM cards_detection13")
    result = mycursor.fetchall()
    business_cards = {}
    for row in result:
        business_cards[row[0]] = row[0]
    selected_card = st.selectbox("Select a name to update", list(business_cards.keys()))
    st.markdown("#### Update or modify any data below")
    mycursor.execute("select company_name,name,designation,mobile_number,email,website,area,city,state,pincode from cards_detection13 WHERE name=%s",
                            (selected_card,))
    result = mycursor.fetchone()

    # Display the current information for the selected business card
    st.write("Company_Name:", result[0])
    st.write("Name:", result[1])
    st.write("Designation:", result[2])
    st.write("Mobile_no:", result[3])
    st.write("Email:", result[4])
    st.write("Website:", result[5])
    st.write("Area:", result[6])
    st.write("City:", result[7])
    st.write("State:", result[8])
    st.write("Pincode:", result[9])

    # Get new information for the business card
    company_name = st.text_input("Company_Name", result[0])
    name = st.text_input("Name", result[1])
    designation = st.text_input("Designation", result[2])
    mobile_no = st.text_input("Mobile_Number", result[3])
    email = st.text_input("Email", result[4])
    website = st.text_input("Website", result[5])
    area = st.text_input("Area", result[6])
    city = st.text_input("City", result[7])
    state = st.text_input("State", result[8])
    pincode = st.text_input("Pin_Code", result[9])
    # Create a button to update the business card
    if st.button("Update Business Card"):
        # Update the information for the selected business card in the database
        mycursor.execute("""UPDATE cards_detection13 SET company_name=%s,name=%s,designation=%s,mobile_number=%s,email=%s,website=%s,area=%s,city=%s,state=%s,pincode=%s
                                    WHERE name=%s""", (company_name,name,designation,mobile_no,email,website,area,city,state,pincode,selected_card))
        mydb.commit()
        st.success("Business card information updated in database.")
    if st.button("View updated data"):
        mycursor.execute("select company_name,name,designation,mobile_number,email,website,area,city,state,pincode from cards_detection13")
        updated_df = pd.DataFrame(mycursor.fetchall(),columns=["Company_Name","Name","Designation","Mobile_No","Email","Website","Area","City","State","PinCode"])
        st.write(updated_df)
elif choice == 'Delete':
    # Create a dropdown menu to select a business card to delete
    mycursor.execute("SELECT id, name FROM cards_detection13")
    result = mycursor.fetchall()
    business_cards = {}
    for row in result:
        business_cards[row[0]] = row[1]
    selected_card_id = st.selectbox("Select a business card to delete", list(business_cards.keys()), format_func=lambda x: business_cards[x])

    # Get the name of the selected business card
    mycursor.execute("SELECT name FROM cards_detection13 WHERE id=%s", (selected_card_id,))
    result = mycursor.fetchone()
    if result:
      selected_card_name = result[0]

    # Display the current information for the selected business card
      st.write("Name:", selected_card_name)
    # Display the rest of the information for the selected business card

    # Create a button to confirm the deletion of the selected business card
    if st.button("Delete Business Card"):
        mycursor.execute("DELETE FROM cards_detection13 WHERE name=%s", (selected_card_name,))
        mydb.commit()
        st.success("Business card information deleted from database.")
        
        
        
        
        
        
                
                
            
                
            
                
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
            
