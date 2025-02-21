import streamlit as st
from pathlib import Path

# st.title("LOL!!!")

# File uploader
uploaded_file = st.file_uploader(
    "Upload a file", type=["txt", "csv", "png", "jpg", "pdf"]
)

if uploaded_file:
    # Define path to save file (outside "views/")
    data_folder = Path(__file__).parent.parent / "data"
    data_folder.mkdir(parents=True, exist_ok=True)  # Ensure the folder exists

    file_path = data_folder / uploaded_file.name  # Full path for saving

    # Save file
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"File saved to: {file_path}")
