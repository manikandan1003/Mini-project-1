import streamlit as st
st.markdown("<h1 style='color: red;'>🚨POLICE CHICK POST🚔</h1>", unsafe_allow_html=True)
from PIL import Image


img = Image.open("C:\\Users\\User\\Desktop\\maniimage.webp")

rotated_img = img.rotate(0)

resized_img = rotated_img.resize((900, 500))  


st.image(resized_img)





import streamlit as st
st.title("POLICE POST")

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt 
import seaborn as sns 
import openpyxl as opxl



uploaded_file = st.file_uploader("D:\guvi data science\cleaned_data.xlsx", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
       
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        st.success("File uploaded and read successfully!")
        
     
        st.write("### Excel File Preview")
        st.dataframe(df)
        
    except Exception as e:
        st.error(f"Error reading the Excel file: {e}")
else:
    st.info("Please upload an Excel file (XLS or XLSX).")

import mysql.connector

def create_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="mani",
            password="1234",
            database="police_post"
        )
        return connection
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

def fetch_data(query):
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)  
            cursor.execute(query)
            result = cursor.fetchall()
            if not result:
                return pd.DataFrame()
            df = pd.DataFrame(result)
            return df  
        finally:
            connection.close()
    else:
        return pd.DataFrame()


# -------------------- Streamlit UI -------------------




st.title("🚓 Police Traffic Stop Dashboard")


col1, col2, col3 = st.columns(3)

total_stops = fetch_data("SELECT COUNT(*) AS total_stops FROM traffic_stops")
total_arrests = fetch_data("SELECT COUNT(*) AS total_arrests FROM traffic_stops WHERE is_arrested = TRUE")
common_violation = fetch_data("""
    SELECT violation, COUNT(*) AS count 
    FROM traffic_stops 
    GROUP BY violation 
    ORDER BY count DESC 
    LIMIT 1
""")
total_searches = fetch_data("SELECT COUNT(*) AS total_searches FROM traffic_stops WHERE search_conducted = TRUE")
drug_stops = fetch_data("SELECT COUNT(*) AS drug_related FROM traffic_stops WHERE drugs_related_stop = TRUE")
avg_age = fetch_data("SELECT AVG(driver_age) AS avg_driver_age FROM traffic_stops WHERE driver_age IS NOT NULL")

col1.metric("Total Stops", total_stops['total_stops'][0])
col2.metric("Total Arrests", total_arrests['total_arrests'][0])
col3.metric("Most Common Violation", common_violation['violation'][0])

col1.metric("Searches Conducted", total_searches['total_searches'][0])
col2.metric("Drug-related Stops", drug_stops['drug_related'][0])
avg_driver_age = float(avg_age['avg_driver_age'][0])
col3.metric("Average Driver Age", round(avg_driver_age, 1))


# -------------------- Charts --------------------



st.subheader("📊 Driver Gender Distribution")
gender_data = fetch_data("""
    SELECT driver_gender, COUNT(*) AS count 
    FROM traffic_stops 
    GROUP BY driver_gender
""")
if not gender_data.empty:
    fig1, ax1 = plt.subplots()
    ax1.pie(gender_data['count'], labels=gender_data['driver_gender'], autopct='%1.1f%%')
    st.pyplot(fig1)





st.subheader("📄 Recent Traffic Stops (Latest 10)")
recent_stops = fetch_data("""
    SELECT stop_date, stop_time, driver_gender, driver_race, violation, stop_outcome, vechicle_number, is_arrested, drugs_related_stop
    FROM traffic_stops 
    ORDER BY stop_date DESC, stop_time DESC 
    LIMIT 10
""")
st.dataframe(recent_stops)


st.header("Medium Level")
selected_query = st.selectbox("Select a Query to run", [
    "Total Number of Police Stops",
    "Count of Stops by Violation Type",
    "Number of Arrests vs. Warnings",
    "Average Age of Drivers Stopped",
    "Top 5 Most Frequent Search Types",
    "Count of Stops by Gender",
    "Most Common Violation for Arrests",
    "Average Stop Duration for Each Violation",
    "Number of Drug-Related Stops by Year",
    "Drivers with the Highest Number of Stops",
    "Number of Stops Conducted at Night (Between 10 PM - 5 AM)",
    "Number of Searches Conducted by Violation Type",
    "Arrest Rate by Driver Gender",
    "Violation Trends Over Time (Monthly Count of Violations)",
    "Most Common Stop Outcomes for Drug-Related Stops"
])


query_map = {
    "Total Number of Police Stops": "SELECT COUNT(*) AS total_police_stops FROM traffic_stops",
    "Count of Stops by Violation Type": "SELECT violation, COUNT(*) AS stop_count FROM traffic_stops GROUP BY violation ORDER BY stop_count DESC",
    "Number of Arrests vs. Warnings": "SELECT stop_outcome, COUNT(*) AS total FROM traffic_stops WHERE stop_outcome IN ('Arrest', 'Warning') GROUP BY stop_outcome ORDER BY total DESC",
    "Average Age of Drivers Stopped": "SELECT AVG(driver_age) AS average_driver_age FROM traffic_stops WHERE driver_age IS NOT NULL",
    "Top 5 Most Frequent Search Types": "SELECT search_type, COUNT(*) AS total_searches FROM traffic_stops WHERE search_type IS NOT NULL AND search_type != '' GROUP BY search_type ORDER BY total_searches DESC LIMIT 5",
    "Count of Stops by Gender": "SELECT driver_gender, COUNT(*) AS total_stops FROM traffic_stops WHERE driver_gender IS NOT NULL GROUP BY driver_gender",
    "Most Common Violation for Arrests": "SELECT violation, COUNT(*) AS violation_count FROM traffic_stops WHERE is_arrested = 1 GROUP BY violation ORDER BY violation_count DESC LIMIT 1",
    "Average Stop Duration for Each Violation": "SELECT violation, ROUND(AVG(stop_duration), 2) AS average_stop_duration FROM traffic_stops WHERE stop_duration IS NOT NULL GROUP BY violation ORDER BY average_stop_duration DESC",
    "Number of Drug-Related Stops by Year": "SELECT YEAR(stop_date) AS stop_year, COUNT(*) AS drug_related_stops FROM traffic_stops WHERE drugs_related_stop = 1 GROUP BY stop_year ORDER BY stop_year ASC",
    "Drivers with the Highest Number of Stops": "SELECT vechicle_number, COUNT(*) AS stop_count FROM traffic_stops GROUP BY vechicle_number ORDER BY stop_count DESC LIMIT 10",
    "Number of Stops Conducted at Night (Between 10 PM - 5 AM)": "SELECT COUNT(*) AS night_stops FROM traffic_stops WHERE (stop_time >= '22:00:00' OR stop_time <= '05:00:00')",
    "Number of Searches Conducted by Violation Type": "SELECT violation, COUNT(*) AS search_count FROM traffic_stops WHERE search_conducted = 1 GROUP BY violation ORDER BY search_count DESC",
    "Arrest Rate by Driver Gender": "SELECT driver_gender, COUNT(*) AS total_stops, SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END) AS total_arrests, (SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END) / COUNT(*)) * 100 AS arrest_rate FROM traffic_stops GROUP BY driver_gender ORDER BY arrest_rate DESC",
    "Violation Trends Over Time (Monthly Count of Violations)": "SELECT YEAR(stop_date) AS violation_year, MONTH(stop_date) AS violation_month, violation, COUNT(*) AS violation_count FROM traffic_stops GROUP BY violation_year, violation_month, violation ORDER BY violation_year, violation_month, violation_count DESC",
    "Most Common Stop Outcomes for Drug-Related Stops": "SELECT stop_outcome, COUNT(*) AS outcome_count FROM traffic_stops WHERE drugs_related_stop = 1 GROUP BY stop_outcome ORDER BY outcome_count DESC"
}


if st.button("Run Query", key="medium_level_query"):
    result = fetch_data(query_map[selected_query])
    if result is not None and not result.empty:
        st.write(result)
    else:
        st.warning("No result found for the selected query.")



st.header("Complex")
selected_query_complex = st.selectbox("Select a Query to run", [
    "Yearly Breakdown of Stops and Arrests by Country (Using Subquery and Window Functions)",
    "Driver Violation Trends Based on Age and Race (Join with Subquery)",
    "Time Period Analysis of Stops (Joining with Date Functions)",
    "Correlation Between Age, Violation, and Stop Duration (Subquery)",
    "Violations with High Search and Arrest Rates (Window Function)",
    "Driver Demographics by Country (Age, Gender, and Race)",
    "Top 5 Violations with Highest Arrest Rates"
])

#"Complex"
query_map_complex = {
     "Yearly Breakdown of Stops and Arrests by Country (Using Subquery and Window Functions)": "SELECT country_name, stop_year, total_stops, total_arrests, SUM(total_arrests) OVER (PARTITION BY country_name ORDER BY stop_year) AS cumulative_arrests FROM (SELECT country_name, YEAR(stop_date) AS stop_year, COUNT(*) AS total_stops, SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END) AS total_arrests FROM traffic_stops GROUP BY country_name, YEAR(stop_date)) AS yearly_data ORDER BY country_name, stop_year",
     "Driver Violation Trends Based on Age and Race (Join with Subquery)": "SELECT CASE WHEN driver_age BETWEEN 18 AND 25 THEN '18-25' WHEN driver_age BETWEEN 26 AND 35 THEN '26-35' WHEN driver_age BETWEEN 36 AND 45 THEN '36-45' WHEN driver_age BETWEEN 46 AND 60 THEN '46-60' WHEN driver_age > 60 THEN '60+' ELSE 'Unknown' END AS age_group, driver_race, violation, COUNT(*) AS violation_count FROM traffic_stops WHERE driver_age IS NOT NULL GROUP BY age_group, driver_race, violation ORDER BY age_group, driver_race, violation_count DESC",
     "Time Period Analysis of Stops (Joining with Date Functions)":"SELECT t.country_name, CASE WHEN HOUR(t.stop_time) BETWEEN 5 AND 11 THEN 'Morning' WHEN HOUR(t.stop_time) BETWEEN 12 AND 16 THEN 'Afternoon' WHEN HOUR(t.stop_time) BETWEEN 17 AND 20 THEN 'Evening' WHEN HOUR(t.stop_time) >= 21 OR HOUR(t.stop_time) <= 4 THEN 'Night' ELSE 'Unknown' END AS time_period, COUNT(*) AS stop_count FROM traffic_stops t WHERE t.stop_time IS NOT NULL GROUP BY t.country_name, time_period ORDER BY t.country_name, time_period",
     "Correlation Between Age, Violation, and Stop Duration (Subquery)":"SELECT age_group, violation, stop_duration, COUNT(*) AS count FROM (SELECT CASE WHEN driver_age BETWEEN 18 AND 25 THEN '18-25' WHEN driver_age BETWEEN 26 AND 35 THEN '26-35' WHEN driver_age BETWEEN 36 AND 45 THEN '36-45' WHEN driver_age BETWEEN 46 AND 60 THEN '46-60' WHEN driver_age > 60 THEN '60+' ELSE 'Unknown' END AS age_group, violation, stop_duration FROM traffic_stops WHERE driver_age IS NOT NULL AND violation IS NOT NULL AND stop_duration IS NOT NULL) AS age_violation_data GROUP BY age_group, violation, stop_duration ORDER BY age_group, violation, stop_duration",
     "Violations with High Search and Arrest Rates (Window Function)":"SELECT violation, total_stops, total_searches, total_arrests, ROUND((total_searches / total_stops) * 100, 2) AS search_rate_percent, ROUND((total_arrests / total_stops) * 100, 2) AS arrest_rate_percent, RANK() OVER (ORDER BY (total_searches / total_stops) DESC) AS search_rank, RANK() OVER (ORDER BY (total_arrests / total_stops) DESC) AS arrest_rank FROM (SELECT violation, COUNT(*) AS total_stops, SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) AS total_searches, SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END) AS total_arrests FROM traffic_stops WHERE violation IS NOT NULL GROUP BY violation) AS violation_stats ORDER BY search_rate_percent DESC",
     "Driver Demographics by Country (Age, Gender, and Race)": "SELECT country_name, driver_gender AS gender, driver_race AS race, CASE WHEN driver_age BETWEEN 18 AND 25 THEN '18-25' WHEN driver_age BETWEEN 26 AND 35 THEN '26-35' WHEN driver_age BETWEEN 36 AND 45 THEN '36-45' WHEN driver_age BETWEEN 46 AND 60 THEN '46-60' WHEN driver_age > 60 THEN '60+' ELSE 'Unknown' END AS age_group, COUNT(*) AS total_drivers FROM traffic_stops WHERE driver_age IS NOT NULL GROUP BY country_name, gender, race, age_group ORDER BY country_name, gender, race, age_group",
    "Top 5 Violations with Highest Arrest Rates":"SELECT violation, COUNT(*) AS total_stops, SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END) AS total_arrests, ROUND((SUM(CASE WHEN is_arrested = 1 THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2) AS arrest_rate FROM traffic_stops GROUP BY violation ORDER BY arrest_rate DESC LIMIT 5",
}


if st.button("Run Complex Query", key="complex_query"):
    result = fetch_data(query_map_complex[selected_query_complex])  # Use 'query_map_complex' here
    if result is not None and not result.empty:
        st.write(result)
    else:
        st.warning("No result found for the selected query.")



import streamlit as st
import mysql.connector
import pandas as pd

def create_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="mani",          
            password="1234",      
            database="police_post" 
        )
        return connection
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

def get_vehicle_info(vehicle_number):
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT country_name, stop_date, stop_time, driver_age, driver_gender, driver_race, search_conducted, search_type, stop_duration, drugs_related_stop, violation, stop_outcome, is_arrested 
                FROM traffic_stops 
                WHERE vechicle_number = %s 
                LIMIT 1
            """
            cursor.execute(query, (vehicle_number,))
            result = cursor.fetchone()
            return result
        except Exception as e:
            st.error(f"MySQL Error: {e}")
            return None
        
    else:
        return None



st.title("🚨 Vehicle Information Finder🔎")

vehicle_number_input = st.text_input("Enter Vehicle Number:")

if st.button("Run"):
    if vehicle_number_input.strip() == "":
        st.error("❌ Please enter a valid vehicle number!")
    else:
        with st.spinner('Fetching vehicle information...'):
            vehicle_info = get_vehicle_info(vehicle_number_input)
        
        if vehicle_info:
            country = vehicle_info['country_name']
            stop_date = vehicle_info['stop_date']
            stop_time = vehicle_info['stop_time']
            driver_age = vehicle_info['driver_age']
            driver_gender = "male" if vehicle_info['driver_gender'].lower()=="m" else "female"
            driver_race = vehicle_info["driver_race"]
            search_conducted = "search is conducted" if vehicle_info['search_conducted'] else "search not conducted"
            search_type = vehicle_info['search_type'] if vehicle_info['search_type'] else "No search conducted"
            stop_outcome = vehicle_info['stop_outcome']
            stop_duration = vehicle_info['stop_duration']
            drug_related = "related to drugs" if vehicle_info['drugs_related_stop'] else "not drug-related"
            violation = vehicle_info["violation"]
            is_arrested = "Person was arrested" if vehicle_info['is_arrested'] else "Person was not arrested"
            
   
            message = (
                f"🚗 The vehicle was stopped 🫸 in **{country}** on **{stop_date}** at **{stop_time}**. "
                f"The driver was a  **{driver_age}** years old **{driver_gender}** of **{driver_race}** race, "
                f" with a stop duration of **{stop_duration}**, "
                f"and a **{search_conducted}**. The search type is **{search_type}**."
                f" The order was filed as 📝 **{stop_outcome}**,  and the violation was classified as **{violation}**. "
                f"The stop was **{drug_related}**, "
                f"the **{is_arrested}**."
            )
            
            st.success(message)
            with st.expander("See Full Details"):
                st.json(vehicle_info)
        
        else:
            st.error("❌ No information found for the entered vehicle number or the data is mismatched.")
            

        

      











def fetch_analysis_result(country_name, driver_gender, driver_age, driver_race, search_type, drugs_related_stop, vechicle_number):
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = f"""
                SELECT stop_outcome, violation, stop_duration 
                FROM traffic_stops
                WHERE country_name = %s 
                  AND driver_gender = %s 
                  AND driver_age = %s 
                  AND driver_race = %s 
                  AND search_type = %s 
                  AND drugs_related_stop = %s 
                  AND vechicle_number = %s
                LIMIT 1
            """
            cursor.execute(query, (country_name, driver_gender, driver_age, driver_race, search_type, drugs_related_stop, vechicle_number))
            result = cursor.fetchone()
            if not result:
                return None  
            return result
        except Exception as e:
            st.error(f"MySQL Error: {e}")
            return None
        finally:
            connection.close()
    else:
        return None


st.title("🚨 Traffic Stop Prediction System 🔎")
with st.form(key='predict_form'):
    country_name = st.text_input("Country Name:")
    driver_gender = st.selectbox("Driver Gender:", ["M", "F"])
    driver_age = st.number_input("Driver Age:", min_value=0, max_value=120, value=30)
    driver_race = st.selectbox("Driver Race:", ["White", "Black", "Hispanic", "Asian", "Other"])
    search_type = st.selectbox("Search Type:", ["Vehicle Search", "Frisk"])
    drugs_related_stop = st.selectbox("Was it Drug Related?", ["Yes", "No"])
    vechicle_number = st.text_input("Vechicle Number:")
    
    submit_button = st.form_submit_button("Predict Stop Outcome & Violation")

    if submit_button:
        drugs_related_stop = True if drugs_related_stop == "Yes" else False
        result = fetch_analysis_result(country_name, driver_gender, driver_age, driver_race, search_type, drugs_related_stop, vechicle_number)
        
    if result:
        st.subheader("Prediction Result:")
        st.write(
        f" 🚗 The stop resulted in **{result['stop_outcome']}**, with a primary violation of **{result['violation']}**, "
        f"and the stop lasted for **{result['stop_duration']}**."
        )
    else:
            st.write("No matching record found in the database.")


































