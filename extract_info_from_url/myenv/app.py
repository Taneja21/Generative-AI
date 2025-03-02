import gradio as gr
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from dotenv import load_dotenv
import os


# Configure Gemini API 
load_dotenv()
api_key=os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("API Key not found! Set GOOGLE_API_KEY in a .env file or environment variable.")

genai.configure(api_key=api_key)


#Get the source code HTML
def get_HTML(input_URL):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    try:
        response= requests.get(input_URL, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the source HTML: {e}")
        return None

#Extract text from HTML
def extract_text_from_HTML(input_URL):
    
    mansion_details = ""
    para_tags = []
    html = get_HTML(input_URL)
    if not html:
        print("Source HTML not returned")
        return None
    try:
       soup = BeautifulSoup(html, "html.parser")
       conatiner = soup.find('div', id='article_sector')   
       para_tags = conatiner.find_all('p')
       if para_tags:
           print("Got para tags")
           for p in para_tags:
               mansion_details += p.text
       return mansion_details
      
    except Exception as e:
        print(f"Exception raised in text extraction from source HTML: {e}")
      
#Extract information from text using LLM Model
def extract_information_from_text(input_URL):
    # extracted_text = extract_text_from_HTML(input_URL)
    extracted_text = extract_text_from_HTML(input_URL)
    
    if not extracted_text:
        return "text extraction from source HTML failed"
     
    
    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = f"""
    You are an AI assistant helping extract structured information about a mansion for sale.
    The text below contains details of a mansion, including keytags, amenities, facilities, seller name, and location.
    Extract the relevant details for the mansion and present them in a structured format.

    Text:
    {extracted_text}

    Please provide the output in the following structured JSON format:
    [
        {{
            "Keytags": ["Luxury", "Ocean View", "Modern"],
            "Amenities": ["Swimming Pool", "Home Theater", "Garden"],
            "Facilities": ["24/7 Security", "Gym", "Parking"],
            "Seller Name": "John Doe",
            "Location": "Beverly Hills, Los Angeles, CA"
        }},
    ]
    """
    
    response = model.generate_content(prompt)
    return response.text

#Gradio Interface
iface = gr.Interface(
    fn=extract_information_from_text,
    inputs=gr.Textbox(label="Enter the URL"),
    outputs=gr.Textbox(label="Output"),
    title="Information Extraction",
    description="Enter the URL and see the extracted information"
)

iface.launch()

