import streamlit as st
from snowflake.snowpark.functions import col
import requests

st.title("Customize Your Smoothie 🥤")
st.write("Choose the fruit you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your smoothie will be:", name_on_order)

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Step 1: SEARCH_ON column ko bhi select karein
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Step 2: Multiselect mein pura dataframe use karein
# Isse user ko 'FRUIT_NAME' dikhayi dega
ingredients_list = st.multiselect(
    'Choose up to 5 Ingredients:',
    my_dataframe,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        # Step 3: SEARCH_ON value ko fetch karein
        search_on = my_dataframe.filter(col('FRUIT_NAME') == fruit_chosen).select(col('SEARCH_ON')).collect()[0][0]
        st.write('The search value for ', fruit_chosen, ' is ', search_on, '.') # Troubleshooting ke liye
        
        st.subheader(fruit_chosen + ' Nutrition Information')
        
        # Step 4: API call mein search_on ka istemal karein
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        if name_on_order:
            session.sql(my_insert_stmt).collect()
            st.success(f'Your Smoothie is ordered, {name_on_order}! ✅', icon="✅")
