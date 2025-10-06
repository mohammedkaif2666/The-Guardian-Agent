# guardian_agent.py

import os
import json
import easyocr
from PIL import Image
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

## --- 1. SET UP YOUR API KEY ---
#
# IMPORTANT: Paste your Gemini API Key here.
#
os.environ["GOOGLE_API_KEY"] = "#"


## --- 2. CONFIGURE THE AGENT'S "BRAIN" (GEMINI LLM) ---

# We configure the Gemini model that will perform the analysis.
# The model name you provided is 'gemini-2.0-flash', which is fast and efficient.
try:
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.1)
except Exception as e:
    print(f"Error initializing the language model: {e}")
    llm = None

# Initialize the OCR reader for English. This will be loaded into memory once.
try:
    ocr_reader = easyocr.Reader(['en'])
except Exception as e:
    print(f"Error initializing the OCR reader: {e}")
    ocr_reader = None

## --- 3. DEFINE THE CORE ANALYSIS FUNCTION ---

def analyze_text_for_cyberbullying(text_to_analyze: str) -> dict:
    """
    Analyzes a given text for cyberbullying using a structured prompt with the Gemini LLM.

    Args:
        text_to_analyze: The string of text to be analyzed.

    Returns:
        A dictionary containing the analysis results, or an error message.
    """
    if not llm:
        return {"error": "Language model is not available."}
        
    # This is the master prompt that defines the agent's persona, task, and output format.
    # It is crucial for getting reliable, structured JSON output.
    prompt = f"""
    You are 'Guardian', a personal AI agent dedicated to detecting and analyzing cyberbullying.
    Your task is to analyze the following text for any form of cyberbullying, hate speech, or toxic content.
    Do not identify yourself as a large language model or mention Gemini. Your identity is 'Guardian'.

    Analyze the following text:
    ---
    {text_to_analyze}
    ---

    After your analysis, you MUST provide the output in a single, clean JSON object with the following keys:
    - "is_bullying": A boolean value (true or false).
    - "category": One of the following strings: "Harassment", "Hate Speech", "Threats", "Impersonation", "Exclusion", "Gossip/Rumors", or "Not Cyberbullying".
    - "severity_score": An integer from 0 (not bullying) to 100 (severe bullying).
    - "analysis": A brief, neutral explanation of your reasoning for the classification and score.

    JSON Output:
    """

    try:
        message = HumanMessage(content=prompt)
        response = llm.invoke([message])
        
        # Clean the response to ensure it's valid JSON
        cleaned_response = response.content.strip().replace("```json", "").replace("```", "")
        
        # Parse the JSON string into a Python dictionary
        result = json.loads(cleaned_response)
        return result

    except json.JSONDecodeError:
        return {"error": "Failed to get a valid analysis from the AI. The response was not in the expected format."}
    except Exception as e:
        return {"error": f"An unexpected error occurred during analysis: {e}"}


## --- 4. DEFINE THE IMAGE PROCESSING FUNCTION (OCR) ---

def extract_text_from_image(image_path: str) -> str | None:
    """
    Extracts text from an image file using EasyOCR.

    Args:
        image_path: The file path to the image.

    Returns:
        A string containing all extracted text, or None if an error occurs.
    """
    if not ocr_reader:
        print("OCR reader is not available.")
        return None

    try:
        # Verify the image is valid before processing
        Image.open(image_path).verify() 
        
        # Read the text from the image
        result = ocr_reader.readtext(image_path, paragraph=True)
        
        # The result is a list of strings when paragraph=True
        if result:
            full_text = " ".join(result)
            print(f"\n--- Extracted Text from Image ---\n{full_text}\n---------------------------------")
            return full_text
        else:
            return "" # Return an empty string if no text is found
            
    except FileNotFoundError:
        print(f"Error: The file was not found at the path: {image_path}")
        return None
    except Exception as e:
        print(f"Error processing image file: {e}")
        return None


## --- 5. MAIN INTERACTIVE LOOP ---

if __name__ == "__main__":
    print("✅ Guardian Agent is online.")
    print("   Provide text or a local image path for cyberbullying analysis.")
    print("   Type 'exit' or 'quit' to stop.")

    while True:
        user_input = input("\n> Enter text or image path: ")

        if user_input.lower() in ["exit", "quit"]:
            print("Guardian Agent shutting down. Stay safe online.")
            break

        text_to_analyze = ""
        # Check if the input is a valid file path
        if os.path.exists(user_input):
            print("Image path detected. Extracting text...")
            extracted_text = extract_text_from_image(user_input)
            if extracted_text is not None:
                if extracted_text == "":
                    print("No text could be found in the image.")
                    continue
                text_to_analyze = extracted_text
            else:
                # Error message was already printed by the function
                continue
        else:
            # Assume it's direct text input
            text_to_analyze = user_input

        # Perform the analysis
        print("\nGuardian is analyzing...")
        analysis_result = analyze_text_for_cyberbullying(text_to_analyze)

        # Display the results in a clean format
        print("\n--- Guardian Analysis ---")
        if "error" in analysis_result:
            print(f"An error occurred: {analysis_result['error']}")
        else:
            is_bullying = analysis_result.get('is_bullying', False)
            category = analysis_result.get('category', 'N/A')
            severity = analysis_result.get('severity_score', 0)
            explanation = analysis_result.get('analysis', 'No explanation provided.')

            print(f"Cyberbullying Detected: {'Yes' if is_bullying else 'No'}")
            print(f"Category: {category}")
            print(f"Severity Score: {severity}/100")
            print(f"Explanation: {explanation}")
        print("-------------------------")
