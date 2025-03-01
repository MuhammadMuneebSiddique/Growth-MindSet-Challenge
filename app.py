import streamlit as st
import pandas as pd
import os
from io import BytesIO

# Configure the app
st.set_page_config(page_title="Data Sweeper", layout="wide", initial_sidebar_state="expanded")
st.title("Data Sweeper")
st.markdown("#### Transform, clean, and visualize your data with ease! Convert between CSV and Excel formats effortlessly.")

# Sidebar Navigation
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to:", ["Upload Files", "Data Cleaning", "Visualization", "Text Extractor"])

st.sidebar.markdown("### Quick Tips:")
st.sidebar.info("Upload CSV or Excel files to get started.")
st.sidebar.info("Use the 'Data Cleaning' section to remove duplicates or fill missing values.")
st.sidebar.info("Convert files between CSV and Excel formats seamlessly.")

st.sidebar.markdown("### Feedback")
feedback = st.sidebar.text_area("Share your suggestions or feedback:")
if st.sidebar.button("Submit Feedback"):
    st.sidebar.success("Thank you for your feedback!")

# File Uploader
if page == "Upload Files":
    uploaded_files = st.file_uploader("Upload your files (CSV or Excel):", type=["csv", "xlsx"], accept_multiple_files=True)

    if uploaded_files:
        for file in uploaded_files:
            file_extension = os.path.splitext(file.name)[-1].lower()

            # Read the file based on its format
            if file_extension == ".csv":
                df = pd.read_csv(file)
            elif file_extension == ".xlsx":
                df = pd.read_excel(file)
            else:
                st.error(f"Unsupported file format: {file_extension}")
                continue

            st.write(f"**File Name:** {file.name}")
            st.write(f"**File Size:** {file.size / 1024:.2f} KB")

            # Display a preview of the data
            st.subheader("Data Preview")
            st.dataframe(df.head())

            # Data Cleaning Options
            st.subheader("Data Cleaning Options")
            if st.checkbox(f"Clean data for {file.name}"):
                col1, col2 = st.columns(2)

                with col1:
                    if st.button(f"Remove Duplicates from {file.name}"):
                        df.drop_duplicates(inplace=True)
                        st.success("Duplicates removed successfully!")

                with col2:
                    if st.button(f"Fill Missing Values for {file.name}"):
                        numeric_columns = df.select_dtypes(include=['number']).columns
                        df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].mean())
                        st.success("Missing values filled successfully!")

            # Select columns to keep
            st.subheader("Select Columns to Keep")
            selected_columns = st.multiselect(f"Choose columns for {file.name}", df.columns, default=df.columns)
            df = df[selected_columns]

            # Data Visualization
            st.subheader("Data Visualization")
            if st.checkbox(f"Show Visualization for {file.name}"):
                st.bar_chart(df.select_dtypes(include='number').iloc[:, :2])

            # File Conversion Options
            st.subheader("File Conversion")
            conversion_format = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)
            if st.button(f"Convert {file.name}"):
                buffer = BytesIO()
                if conversion_format == "CSV":
                    df.to_csv(buffer, index=False)
                    file_name = file.name.replace(file_extension, ".csv")
                    mime_type = "text/csv"
                elif conversion_format == "Excel":
                    df.to_excel(buffer, index=False)
                    file_name = file.name.replace(file_extension, ".xlsx")
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                buffer.seek(0)

                # Download Button
                st.download_button(
                    label=f"Download {file_name} as {conversion_format}",
                    data=buffer,
                    file_name=file_name,
                    mime=mime_type,
                )

# Text Extractor Section
if page == "Text Extractor":
    st.subheader("Text Extractor")
    text_file = st.file_uploader("Upload a file (TXT, CSV, Excel, or PDF):", type=["txt", "csv", "xlsx", "pdf"])

    if text_file:
        file_extension = os.path.splitext(text_file.name)[-1].lower()
        extracted_text = ""

        # Extract text based on file type
        if file_extension == ".txt":
            extracted_text = text_file.read().decode("utf-8")
        elif file_extension == ".csv":
            df = pd.read_csv(text_file)
            extracted_text = df.to_string(index=False)
        elif file_extension == ".xlsx":
            df = pd.read_excel(text_file)
            extracted_text = df.to_string(index=False)
        elif file_extension == ".pdf":
            import fitz  # PyMuPDF
            pdf_reader = fitz.open(stream=text_file.read(), filetype="pdf")
            extracted_text = "\n".join([page.get_text("text") for page in pdf_reader])

        # Display extracted text
        st.text_area("Extracted Text:", extracted_text, height=300)

        # Download extracted text
        if extracted_text:
            st.download_button(
                label="Download Extracted Text",
                data=extracted_text,
                file_name="extracted_text.txt",
                mime="text/plain"
            )

# Success message
st.success("All files processed successfully!")
