import pytesseract
from pdf2image import convert_from_path
import ollama
from pypdf import PdfReader
import json
from typing import List
# Path to Tesseract executable if it's not in your PATH environment
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Define a character limit for the text to be processed at once (adjust as per the model’s input limit)
CHARACTER_LIMIT = 4000  # This is an example limit; adjust based on your model’s capabilities
model='llama3.1'
def extract_text_from_pdf_using_pypdf2(pdf_file_path):
    """Attempt to extract text directly from the PDF using PyPDF2."""
    reader = PdfReader(pdf_file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""  # Handle pages without text (e.g., images)
    return text.strip()

def extract_text_from_pdf_using_ocr(pdf_file_path):
    """Convert PDF to images and extract text from each page using Tesseract OCR."""
    pages = convert_from_path(pdf_file_path)
    text = ""
    for page in pages:
        text += pytesseract.image_to_string(page)
    return text

def handle_large_text(text):
    """Handle large text by splitting it into smaller parts and summarizing each."""
    # Split text into smaller parts if it exceeds the character limit
    chunks = [text[i:i + CHARACTER_LIMIT] for i in range(0, len(text), CHARACTER_LIMIT)]
    
    full_summary = ""
    for chunk in chunks:
        summary = generate_short_summary(chunk)
        full_summary += summary + "\n\n"
    
    return full_summary.strip()

def generate_short_summary(text):
    """Pass the extracted text to the local Llama 3 API for a short summary."""
    response = ollama.chat(model=model, messages=[{'role': 'user', 'content': f"Summarize this text: {text}"}])
    return response['message']['content']




def get_llama_recommendations(user_reviews: List[dict], books: List[dict]) -> List[dict]:
    """
    Send user reviews and all book summaries to Llama for recommendations.
    The input is a list of user reviews and book summaries.
    Llama will return a list of recommended book IDs in JSON format.
    """

    # Combine user reviews and book summaries into a message for Llama
    user_reviews_text = "\n".join([f"Review for book id {review['book_id']}: review {review['review_text']}" for review in user_reviews])
    book_summaries_text = "\n".join([f"book id {book['book_id']}: summary {book['summary']}" for book in books])

    # Create a prompt for Llama, instructing it to return a JSON response with book_ids
    prompt = f"""
    Recommend a book that aligns with the user's preferences based on their past reviews and reading history. Analyze the themes, genres, and writing style from their previous reviews, and suggest a book that matches those elements. Additionally, consider the key highlights and themes from the provided book summary to ensure the recommendation fits the user's interests and literary tastes.
    Here are some book reviews by a user:
    {user_reviews_text}
    
    Here are the summaries of available books:
    {book_summaries_text}
    
    Based on the user's reviews, please recommend books from the list of available books.
    Provide the recommendations in the following JSON format:
    {{
        "book_id": <book_id>
    }}
    """
    
    # Call the Llama model using ollama's chat function
    response = ollama.chat(model=model, messages=[{'role': 'user', 'content': prompt}])
    
    # Process the response from Llama
    response_text = response.get("content", "")
    
    # Example expected response: [{"book_id": 1}, {"book_id": 3}]
    try:
        # Parse the JSON-like response from Llama
        recommendations = json.loads(response_text)
    except json.JSONDecodeError:
        # In case of an invalid or unexpected response format, return an empty list or log the error
        print(f"Error decoding Llama response: {response_text}")
        recommendations = [{"book_id": 0}]

    return recommendations

