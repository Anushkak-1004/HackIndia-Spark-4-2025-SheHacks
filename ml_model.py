import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# Load the dataset
file_path =r"D:\Excelmate AI\output.xlsx"
df = pd.read_excel(file_path, sheet_name="Extracted Data")

# Define features and target variable
X = df.drop(columns=["StudentID", "GradeClass"])  # Features (excluding ID and target)
y = df["GradeClass"]  # Target variable (classification label)

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Normalize the data
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Train the model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy:.2f}")
print("Classification Report:\n", classification_report(y_test, y_pred))

# Add predictions to the original dataset
df["Predicted_Category"] = model.predict(scaler.transform(X))

# Save categorized data into separate Excel sheets
with pd.ExcelWriter(r"D:\Excelmate AI\categorized_students.xlsx") as writer:
    for category in df["Predicted_Category"].unique():
        df[df["Predicted_Category"] == category].to_excel(writer, sheet_name=f"Category_{category}", index=False)

print("Categorized data saved successfully!")