from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import google.generativeai as genai
import os
from dotenv import load_dotenv
import gradio as gr


# Configure Gemini API 
load_dotenv()
api_key=os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("API Key not found! Set GOOGLE_API_KEY in a .env file or environment variable.")

genai.configure(api_key=api_key)

#Extract get from the URL
def get_content_from_URL(input_URL):
    para_tags = []
    extracted_content = ""
    options = Options()
    options.add_argument("--headless")  
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--ignore-certificate-errors")
    
    service = Service(ChromeDriverManager().install()) 
    
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(input_URL)
    
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    container = soup.find('div', id='obtext')
    if container:
        print("Got Conatiner")
        para_tags = container.find_all('p')
        if para_tags:
            print("Got paras")
            for p in para_tags:
                extracted_content += p.text.strip()
            
    driver.quit()
    return extracted_content
        
#Gettting structured text from unstructured text using LLM model
def get_structured_text(input_URL):
   
    extracted_content = get_content_from_URL(input_URL)
    
    if not extracted_content:
        return "text extraction from source HTML failed"
     
    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = f"""
    You are an AI assistant helping to convert unstructured text to structured text.
    The text below contains details of a person.
    Extract the relevant details about that person and present them a tabular format. 
    Headers of the output should be : Name, Birthday, Husband Name, Children, Marraige Date, Grandchildren, Greatgrand Children

    Text:
    {extracted_content}

    Please provide the output in tabular format as below with table headers as stated above.
    """
    response = model.generate_content(prompt)
    return response.text 

#Gradio Interface
with gr.Blocks() as demo:
    url_input = gr.Textbox(label="Paste URL here")
    submit_button = gr.Button("Generate Output")
    output_box = gr.Textbox(label="Output", interactive=False)
    
    submit_button.click(get_structured_text, inputs=url_input, outputs=output_box)
    
#Launch Gradio App
demo.launch()
    