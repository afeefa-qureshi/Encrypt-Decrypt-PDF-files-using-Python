import streamlit as st
import PyPDF2
import fitz
import base64
from io import BytesIO

def is_encrypted(pdf_content):
    """Check if a PDF file is encrypted."""
    reader = PyPDF2.PdfReader(BytesIO(pdf_content))
    return reader.is_encrypted

def encrypt_pdf(pdf_content, password):
    """Encrypt a PDF file with the given password."""
    pdf_writer = PyPDF2.PdfWriter()
    pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_content))

    # Check if the PDF is already encrypted
    if is_encrypted(pdf_content):
        return None, "The PDF file is already encrypted."

    # Copy pages from original PDF to the encrypted PDF
    for page_num in range(len(pdf_reader.pages)):
        pdf_writer.add_page(pdf_reader.pages[page_num])

    # Encrypt the PDF
    pdf_writer.encrypt(user_pwd=password, owner_pwd=None)

    # Write encrypted PDF to BytesIO buffer
    output_pdf = BytesIO()
    pdf_writer.write(output_pdf)
    output_pdf.seek(0)  # Reset the file pointer to the beginning

    return output_pdf, "PDF encrypted successfully!"

def decrypt_pdf(pdf_content, password):
    """Decrypt a password-protected PDF."""
    doc = fitz.open(stream=pdf_content, filetype="pdf")
    
    # Check if the PDF is not encrypted
    if not doc.is_encrypted:
        return None, "The PDF file is not encrypted."

    if doc.authenticate(password):
        output_pdf = BytesIO()
        doc.save(output_pdf)
        output_pdf.seek(0)  # Reset the file pointer to the beginning
        return output_pdf, "PDF decrypted successfully!"
    else:
        return None, "Incorrect password! Unable to decrypt PDF."

def get_download_link(pdf_content, filename):
    """Generate a download link for the PDF."""
    encoded_pdf = base64.b64encode(pdf_content.getvalue()).decode()
    href = f'<a href="data:application/pdf;base64,{encoded_pdf}" download="{filename}">Download {filename}</a>'
    return href

# Streamlit interface
st.title("Encrypt/Decrypt PDF Documents")

# Upload PDF file
pdf_file = st.file_uploader("Upload PDF file")

if pdf_file:
    # Check if the uploaded file is a PDF
    if pdf_file.type == "application/pdf":
        st.write("PDF file uploaded successfully!")

        # Display PDF file details
        st.write("Filename:", pdf_file.name)
        st.write("Size:", pdf_file.size, "bytes")

        # Option for encryption or decryption
        option = st.radio("Choose an option:", ("Encrypt", "Decrypt"))

        if option == "Encrypt":
            # Ask for password
            password = st.text_input("Enter password to encrypt PDF:", type="password")

            # Encrypt PDF if password is provided
            if st.button("Encrypt PDF") and password:
                encrypted_pdf, message = encrypt_pdf(pdf_file.getvalue(), password)
                if encrypted_pdf:
                    st.success(message)
                    # Display download link for the encrypted PDF
                    st.markdown(get_download_link(encrypted_pdf, "encrypted.pdf"), unsafe_allow_html=True)
                else:
                    st.error(message)

        elif option == "Decrypt":
            # Ask for password
            password = st.text_input("Enter password to decrypt PDF:", type="password")

            # Decrypt PDF if password is provided
            if st.button("Decrypt PDF") and password:
                decrypted_pdf, message = decrypt_pdf(pdf_file.getvalue(), password)
                if decrypted_pdf:
                    st.success(message)
                    # Display download link for the decrypted PDF
                    st.markdown(get_download_link(decrypted_pdf, "decrypted.pdf"), unsafe_allow_html=True)
                else:
                    st.error(message)
                    
    else:
        st.error("Please upload a valid PDF file!")
