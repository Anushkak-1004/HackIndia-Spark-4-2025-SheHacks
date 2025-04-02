import os
import pandas as pd
import groq
import time
import json
import re
import streamlit as st

# Output directory and file paths
OUTPUT_DIR = r"D:\Excelmate AI"
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "output_classified.xlsx")

# Categories
CATEGORIES = ["High Risk Student", "Average Student", "Top Performer"]

# Initialize the GROQ client
groq_client = groq.Client(api_key="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")

# Function to extract JSON from raw text
def extract_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return json.loads(match.group()) if match else None

# Function to classify students
def classify_student(row):
    student_data = f"""
    Student ID: {row['StudentID']}
    Age: {row['Age']}
    Gender: {row['Gender']}
    Ethnicity: {row['Ethnicity']}
    Parental Education: {row['ParentalEducation']}
    Study Time Weekly: {row['StudyTimeWeekly']}
    Absences: {row['Absences']}
    Tutoring: {row['Tutoring']}
    Parental Support: {row['ParentalSupport']}
    Extracurricular: {row['Extracurricular']}
    Sports: {row['Sports']}
    Music: {row['Music']}
    Volunteering: {row['Volunteering']}
    GPA: {row['GPA']}
    Grade Class: {row['GradeClass']}
    """

    prompt = f"""
    Categorize the student based on academic performance, extracurricular activities, and attendance.

    Categories:
    - "High Risk Student": Low GPA, high absences, little extracurricular involvement.
    - "Average Student": Moderate GPA, average participation in activities.
    - "Top Performer": High GPA, strong extracurricular involvement.

    Respond in JSON format:
    {{"category": "CATEGORY_NAME", "reason": "Short explanation"}}

    {student_data}
    """

    for _ in range(3):
        try:
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=100
            )

            result = response.choices[0].message.content.strip()
            print(f"Raw API Response: {result}")  # Debugging

            json_data = extract_json(result)
            if not json_data:
                continue  # Retry if response is not JSON

            category = json_data.get("category", "Unknown")
            reason = json_data.get("reason", "No explanation provided.")

            return category if category in CATEGORIES else "Unknown", reason

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(2)

    return "Unknown", "Classification failed after retries."

# Streamlit UI
st.title("Student Performance Classification")
st.write("Upload a CSV file to classify student performance.")

# File uploader widget
uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
    # Read CSV file into DataFrame
    df = pd.read_csv(uploaded_file)

    # Show a preview of the data
    st.subheader("Preview of the Data")
    st.write(df.head())

    # Apply classification function to classify students
    df[['Category', 'Reason']] = df.apply(lambda row: classify_student(row), axis=1, result_type='expand')

    # Show the classified results
    st.subheader("Classified Data")
    st.write(df)

    # Download link for the output classified file
    classified_file = os.path.join(OUTPUT_DIR, "output_classified.csv")
    df.to_csv(classified_file, index=False)

    st.markdown(f"### [Download Classified Data](/{classified_file})")
