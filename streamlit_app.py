# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests #

st.title("Customize Your Smoothie 🥤")
st.write("Choose the fruit you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your smoothie will be:", name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

ingredients_list = st.multiselect(
    'Choose up to 5 Ingredients:',
    my_dataframe,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        # --- API Section Start ---
        st.subheader(fruit_chosen + ' Nutrition Information')
        
        # URL mein ab hum watermelon ki jagah 'fruit_chosen' variable use kar rahe hain taaki har fruit ka data mil sake
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit_chosen)
        
        # Ye line sirf response code dikhayegi (e.g., <Response [200]>)
        st.text(smoothiefroot_response) 
        
        # Data ko table ki surat mein dikhane ke liye niche wali line use karein
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        # --- API Section End ---

    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        if name_on_order:
            session.sql(my_insert_stmt).collect()
            st.success(f'Your Smoothie is ordered, {name_on_order}! ✅', icon="✅")
