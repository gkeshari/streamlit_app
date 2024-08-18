import streamlit as st
import os
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv
import cv2

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def get_gemini_response(image, input=""):
    if input:
        response = model.generate_content([input, image])
    else:
        response = model.generate_content(image)
    return response.text

def show_response(image, prompt):
    if image is not None:
        with st.spinner('Generating response...'):
            response = get_gemini_response(image, prompt)
        return response
    return None

def reset_state():
    for key in list(st.session_state.keys()):
        del st.session_state[key]

def main():
    st.markdown(
        """
        <style>
        body {
            background-color: #f9c2ff;
            font-family: Arial, sans-serif;
        }
        .stButton {
            color: blue;
            text-decoration: none;
            border-radius: 5px;
            padding: 0px;
            width: 200px;
        }
        h1 {
            color: #8e44ad;
        }
        .stButton::after {
            background-color: transparent;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("Image Processor")
    st.subheader("Gemini Vision Application")

    # Initialize session state
    if 'stage' not in st.session_state:
        st.session_state.stage = 'input'

    if st.session_state.stage == 'input':
        image_source = st.radio("Choose image source:", ("Upload Image", "Take Photo"))
        
        if image_source == "Upload Image":
            with st.expander("Upload Image"):
                upload = st.file_uploader('Choose an image', type=['jpg', 'jpeg', 'png'], key='image')
            if upload is not None:
                st.session_state.captured_image = Image.open(upload)
                st.session_state.stage = 'process'
                st.rerun()
        
        elif image_source == "Take Photo":
            st.write("Webcam Live Feed")
            camera = cv2.VideoCapture(0)
            FRAME_WINDOW = st.image([])
            capture_button = st.button('Capture Image')

            if capture_button:
                _, frame = camera.read()
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                st.session_state.captured_image = Image.fromarray(frame)
                st.session_state.stage = 'process'
                camera.release()
                st.rerun()
            else:
                while not capture_button:
                    _, frame = camera.read()
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    FRAME_WINDOW.image(frame)
                    if capture_button:
                        break
                camera.release()

    elif st.session_state.stage == 'process':
        st.image(st.session_state.captured_image, caption='Image', use_column_width=True)
        prompt = st.text_input("Ask something about the image:", "")
        if st.button('🔥 Process Image 🔥'):
            response = show_response(st.session_state.captured_image, prompt)
            if response:
                st.session_state.gemini_response = response
                st.session_state.stage = 'result'
            st.st.rerun()

    elif st.session_state.stage == 'result':
        st.image(st.session_state.captured_image, caption='Image', use_column_width=True)
        st.header('Response')
        st.write(st.session_state.gemini_response)
        if st.button('Start Over', key='start_over_button'):
            reset_state()
            st.rerun()

if __name__ == "__main__":
    main()
