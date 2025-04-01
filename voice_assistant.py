import speech_recognition as sr
import pyttsx3
import pandas as pd
import os
from vosk import Model, KaldiRecognizer
import pyaudio
import json

# ✅ Load Excel file
FILE_PATH = r"D:\Excelmate AI\output.xlsx"  # Update this if needed
df = pd.read_excel(FILE_PATH, engine="openpyxl")

# ✅ Initialize Text-to-Speech
engine = pyttsx3.init()
engine.setProperty("rate", 150)

# ✅ Initialize Recognizer
recognizer = sr.Recognizer()

# ✅ Check if Vosk model exists (for offline mode)
VOSK_MODEL_PATH = "vosk-model-small-en-us-0.15"  # Adjust path if needed
use_offline_mode = os.path.exists(VOSK_MODEL_PATH)

if use_offline_mode:
    vosk_model = Model(VOSK_MODEL_PATH)
    recognizer_vosk = KaldiRecognizer(vosk_model, 16000)

# ✅ Function to speak output
def speak(text):
    print(f"Assistant: {text}")
    engine.say(text)
    engine.runAndWait()

# ✅ Function to listen for voice command
def listen():
    with sr.Microphone() as source:
        print("🎤 Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

        try:
            if use_offline_mode:
                # 📴 Offline Mode (Vosk)
                if recognizer_vosk.AcceptWaveform(audio.get_raw_data()):
                    result = json.loads(recognizer_vosk.Result())
                    return result.get("text", "").lower()
            else:
                # 🌐 Online Mode (Google Speech API)
                return recognizer.recognize_google(audio).lower()

        except sr.UnknownValueError:
            speak("Sorry, I didn't understand.")
            return None
        except sr.RequestError:
            speak("Could not connect to the speech service.")
            return None

# ✅ Function to get student info
def get_student_info(student_id):
    student = df[df["StudentID"] == student_id]
    
    if student.empty:
        speak(f"No student found with ID {student_id}.")
        return

    info = student.iloc[0].to_dict()
    response = f"Student {info['StudentID']}: GPA is {info['GPA']}, has {info['Absences']} absences."
    speak(response)

# ✅ Function to update student data
def update_student_info(student_id, column, new_value):
    if column not in df.columns:
        speak(f"Invalid field: {column}. Try again.")
        return

    df.loc[df["StudentID"] == student_id, column] = new_value
    df.to_excel(FILE_PATH, index=False, engine="openpyxl")
    speak(f"Updated {column} for Student {student_id} to {new_value}.")

# ✅ Function to list all students
def list_students():
    student_list = df["StudentID"].tolist()
    if not student_list:
        speak("No students found in the database.")
    else:
        speak(f"Available students: {', '.join(map(str, student_list))}")

# ✅ Function to find students based on conditions
def find_students(condition):
    try:
        filtered_df = df.query(condition)
        if filtered_df.empty:
            speak("No students match your criteria.")
        else:
            results = ", ".join(filtered_df["StudentID"].astype(str))
            speak(f"Students matching the condition: {results}")
    except Exception as e:
        speak("Invalid condition format. Please try again.")

# ✅ Main Assistant Loop
def voice_assistant():
    speak("Hello! How can I assist you?")
    
    while True:
        command = listen()
        if not command:
            continue

        if "exit" in command or "stop" in command:
            speak("Goodbye!")
            break

        elif "get student" in command:
            speak("Please say the Student ID.")
            student_id = listen()
            if student_id and student_id.isdigit():
                get_student_info(int(student_id))
            else:
                speak("Invalid Student ID.")

        elif "update student" in command:
            speak("Say the Student ID.")
            student_id = listen()
            if not (student_id and student_id.isdigit()):
                speak("Invalid Student ID.")
                continue

            speak("Which field do you want to update?")
            field = listen()
            if not field:
                continue

            speak(f"What is the new value for {field}?")
            new_value = listen()
            if new_value:
                update_student_info(int(student_id), field, new_value)

        elif "list students" in command:
            list_students()

        elif "find students" in command:
            speak("State the condition, for example, 'GPA > 3.5'")
            condition = listen()
            if condition:
                find_students(condition)

# ✅ Run Assistant
if __name__ == "__main__":
    voice_assistant()
