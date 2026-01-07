import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd # Pandas ko fetch karne ke liye

st.title("Customize Your Smoothie 🥤")
st.write("Choose the fruit you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")

cnx = st.connection("snowflake")
session = cnx.session()

# SEARCH_ON column ko select karna zaroori hai
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Dataframe ko Pandas mein convert karein (Error se bachne ke liye)
pd_df = my_dataframe.to_pandas()

ingredients_list = st.multiselect(
    'Choose up to 5 Ingredients:',
    pd_df['FRUIT_NAME'], # User ko sirf fruit names dikhayein
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        # SEARCH_ON value fetch karein
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')
        
        st.subheader(fruit_chosen + ' Nutrition Information')
        
        # API call mein search_on ka istemal
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    # Order submit logic
    my_insert_stmt = f"INSERT INTO smoothies.public.orders (ingredients, name_on_order) VALUES ('{ingredients_string}', '{name_on_order}')"
    
    time_to_insert = st.button('Submit Order')
    if time_to_insert and name_on_order:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered! ✅', icon="✅")
