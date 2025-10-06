# # guardian_agent_telegram_vision.py

# import os
# import json
# import base64
# import easyocr
# from PIL import Image
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_core.messages import HumanMessage
# from telegram import Update
# from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# # --- 1. CONFIGURATION ---

# # IMPORTANT: Paste your Telegram Bot Token from BotFather here.
# TELEGRAM_BOT_TOKEN = "8252957842:AAFyJUuq1oTdHXwRqet-kBJGtylkHFSQc8w"

# # IMPORTANT: Paste your Gemini API Key here.
# os.environ["GOOGLE_API_KEY"] = "AIzaSyAUew6PSAgc7n6r51HKe64kGhwO7LCM85Q"

# # --- 2. INITIALIZE AI & OCR MODELS ---

# print("Initializing models, please wait...")
# try:
#     # Configure the Gemini model. 'gemini-pro-vision' is excellent for this.
#     # We will use your 'gemini-2.0-flash' as it's also a strong multimodal model.
#     llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.1)
#     print("✅ Gemini model initialized.")
# except Exception as e:
#     print(f"❌ Error initializing the language model: {e}")
#     llm = None

# try:
#     # Initialize the OCR reader.
#     ocr_reader = easyocr.Reader(['en'])
#     print("✅ OCR reader initialized.")
# except Exception as e:
#     print(f"❌ Error initializing the OCR reader: {e}")
#     ocr_reader = None

# # --- 3. CORE AI ANALYSIS & OCR FUNCTIONS (UPGRADED FOR VISION) ---

# def analyze_content_for_cyberbullying(text_to_analyze: str, image_bytes: bytes = None) -> dict:
#     """
#     Analyzes text and/or an image for cyberbullying using a multimodal prompt.
#     """
#     if not llm:
#         return {"error": "Language model is not available."}

#     # The prompt is now more advanced, instructing the AI to consider both visuals and text.
#     prompt_text = f"""
#     You are 'Guardian', a personal AI agent for detecting and analyzing cyberbullying.
#     Your identity is 'Guardian'. Do not mention Gemini or being a language model.

#     Your task is to perform a multimodal analysis of the provided content.
#     1.  **Analyze the image:** Look for hateful symbols, threatening gestures, humiliating situations, or any other visual cues of bullying.
#     2.  **Analyze the text:** Read any text provided, which may have been extracted from the image or sent with it.
#     3.  **Combine your findings:** Based on both the image and the text, determine if cyberbullying is occurring.

#     Text for analysis: "{text_to_analyze if text_to_analyze else 'No text provided.'}"

#     Provide your final analysis in a single, clean JSON object with the following keys:
#     - "is_bullying": A boolean value (true or false).
#     - "category": One of the following strings: "Harassment", "Hate Speech", "Threats", "Impersonation", "Exclusion", "Gossip/Rumors", "Visual Mockery", or "Not Cyberbullying".
#     - "severity_score": An integer from 0 (not bullying) to 100 (severe bullying).
#     - "analysis": A brief, neutral explanation of your reasoning, mentioning both visual and textual evidence if present.

#     JSON Output:
#     """

#     try:
#         content_parts = [{"type": "text", "text": prompt_text}]
#         if image_bytes:
#             encoded_image = base64.b64encode(image_bytes).decode("utf-8")
#             image_part = {
#                 "type": "image_url",
#                 "image_url": f"data:image/jpeg;base64,{encoded_image}"
#             }
#             content_parts.insert(0, image_part) # Insert image before the prompt

#         message = HumanMessage(content=content_parts)
#         response = llm.invoke([message])
        
#         cleaned_response = response.content.strip().replace("```json", "").replace("```", "")
#         result = json.loads(cleaned_response)
#         return result
        
#     except json.JSONDecodeError:
#         return {"error": "Failed to get a valid analysis from the AI. The response was not in the expected format."}
#     except Exception as e:
#         return {"error": f"An unexpected error occurred during analysis: {e}"}

# def extract_text_from_image(image_path: str) -> str | None:
#     """
#     Extracts text from an image file using EasyOCR.
#     This function is now fixed to handle the library's output format correctly.
#     """
#     if not ocr_reader: return None
#     try:
#         Image.open(image_path).verify()
        
#         # --- FIX APPLIED HERE ---
#         # We now use the standard readtext call and extract the text (item[1]) from each result.
#         result = ocr_reader.readtext(image_path)
#         return " ".join([item[1] for item in result]) if result else ""
    
#     except Exception as e:
#         print(f"Error during OCR: {e}")
#         return None

# # --- 4. TELEGRAM BOT HANDLERS (UPDATED FOR VISION) ---

# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Sends a welcome message."""
#     welcome_text = (
#         "Hello! I am Guardian, your personal AI agent for cyberbullying detection.\n\n"
#         "Send me any text or image, and I will perform a comprehensive analysis for you."
#     )
#     await update.message.reply_text(welcome_text)

# async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Analyzes text messages sent by the user."""
#     user_text = update.message.text
#     print(f"Received text from {update.effective_user.first_name}: '{user_text}'")
    
#     await update.message.reply_text("Guardian is analyzing the text...")
    
#     # Call the main analysis function (without an image)
#     analysis_result = analyze_content_for_cyberbullying(user_text)
#     await send_analysis_response(update, analysis_result)

# async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Analyzes photos with both vision and OCR."""
#     print(f"Received photo from {update.effective_user.first_name}")
#     await update.message.reply_text("Image received. Guardian is performing a full visual and text analysis...")

#     photo_file = await update.message.photo[-1].get_file()
#     temp_photo_path = "temp_photo.jpg"
#     await photo_file.download_to_drive(temp_photo_path)

#     # 1. Extract text using OCR
#     extracted_text = extract_text_from_image(temp_photo_path)
#     if extracted_text is None:
#         await update.message.reply_text("Guardian had an issue reading the image file.")
#         return
    
#     # 2. Read the image file as bytes for vision analysis
#     with open(temp_photo_path, "rb") as image_file:
#         image_bytes = image_file.read()

#     # 3. Call the multimodal analysis function
#     analysis_result = analyze_content_for_cyberbullying(extracted_text, image_bytes)
#     await send_analysis_response(update, analysis_result)
    
#     # 4. Clean up the temporary file
#     if os.path.exists(temp_photo_path):
#         os.remove(temp_photo_path)

# async def send_analysis_response(update: Update, result: dict) -> None:
#     """Formats and sends the final analysis back to the user."""
#     if "error" in result:
#         response_text = f"An error occurred: {result['error']}"
#     else:
#         is_bullying = result.get('is_bullying', False)
#         category = result.get('category', 'N/A')
#         severity = result.get('severity_score', 0)
#         explanation = result.get('analysis', 'No explanation provided.')

#         response_text = (
#             f"*--- Guardian Analysis ---*\n\n"
#             f"*Cyberbullying Detected:* {'Yes' if is_bullying else 'No'}\n"
#             f"*Category:* {category}\n"
#             f"*Severity Score:* {severity}/100\n"
#             f"*Explanation:* {explanation}"
#         )
    
#     await update.message.reply_text(response_text, parse_mode='Markdown')

# # --- 5. MAIN APPLICATION ---

# def main() -> None:
#     """Start the bot."""
#     if not all([TELEGRAM_BOT_TOKEN != "PASTE_YOUR_TELEGRAM_BOT_TOKEN_HERE", os.getenv("GOOGLE_API_KEY"), llm, ocr_reader]):
#         print("❌ Critical component failed to initialize. Please check your API tokens and installations. Bot cannot start.")
#         return

#     print("Starting Telegram bot with Vision capabilities...")
#     application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

#     application.add_handler(CommandHandler("start", start))
#     application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
#     application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

#     application.run_polling()

# if __name__ == "__main__":
#     main()
