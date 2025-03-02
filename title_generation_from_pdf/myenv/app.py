import gradio as gr
import google.generativeai as genai
import PyPDF2
import os
from dotenv import load_dotenv


#Loading gemini api key from environment variable
load_dotenv()
api_key=os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("API Key not found! Set GOOGLE_API_KEY in a .env file or environment variable.")

# Configure Gemini API
genai.configure(api_key=api_key)

# Text Extraction from PDF
def extract_text_from_pdf_file(user_input_pdf):
    
    try:
       reader = PyPDF2.PdfReader(user_input_pdf)
       text = "".join([page.extract_text() or "" for page in reader.pages])
       user_story = text.strip()
            
    except FileNotFoundError:
        print("Print Not Found")

    except Exception as e:
        print(f"Error Occured : {e}")

    return user_story

#Using LLM for title generation
def generate_title(user_input_pdf):

    user_story = extract_text_from_pdf_file(user_input_pdf)
    if not user_story:
        return "No text found in the file. Please Upload a valid file"
    
    model = genai.GenerativeModel("gemini-2.0-pro-exp")
    response = model.generate_content(f"Generate one appropriate title for the given story : {user_story}")
    return response.text if response.text else "Output Failed"

# Gradio Interface
with gr.Blocks() as demo:
    pdf_input = gr.File(label="Upload Your Story")
    title_output = gr.Textbox(label="AI Generated Title", interactive=False)
    generate_btn = gr.Button("Generate Title")
    
    generate_btn.click(generate_title, inputs=pdf_input, outputs=title_output)

# Run the Gradio app
demo.launch()






