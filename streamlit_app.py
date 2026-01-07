import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd  # Step 1: Bring in Pandas

st.title("Customize Your Smoothie 🥤")
st.write("Choose the fruit you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")

cnx = st.connection("snowflake")
session = cnx.session()

# Step 2: Select BOTH columns so we can use SEARCH_ON later
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Step 3: Convert the Snowpark Dataframe to a Pandas Dataframe
pd_df = my_dataframe.to_pandas()

ingredients_list = st.multiselect(
    'Choose up to 5 Ingredients:',
    pd_df['FRUIT_NAME'], # Use the Pandas column for the list
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        # Step 4: Use .loc to find the SEARCH_ON value for the chosen fruit
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')
        
        st.subheader(fruit_chosen + ' Nutrition Information')
        
        # Step 5: Use the 'search_on' variable in the API call
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    # Insert logic remains the same
    my_insert_stmt = f"INSERT INTO smoothies.public.orders(ingredients, name_on_order) VALUES ('{ingredients_string}','{name_on_order}')"
    
    if st.button('Submit Order') and name_on_order:
        session.sql(my_insert_stmt).collect()
        st.success('Smoothie Ordered! ✅', icon="✅")
