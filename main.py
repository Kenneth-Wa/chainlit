import os
import chainlit as cl
from chainlit.types import AskFileResponse
from chainlit.input_widget import Select, Switch
from app.build_index import create_faiss_index
from app.chat_handler import ChatHandler
from app.document_processor import DocumentProcessor
from app.speech_handler import SpeechHandler
from function_manager.function_manager import FunctionManager
from app.utils.oai import CustomEndpoint  # Update this import path

# Initialize components
function_manager = FunctionManager()
document_processor = DocumentProcessor()
speech_handler = SpeechHandler()
custom_endpoint = CustomEndpoint()
chat_handler = ChatHandler(function_manager, document_processor, speech_handler)

@cl.on_chat_start
async def start():
    # Set default settings
    cl.user_session.set("use_voice", False)
    cl.user_session.set("model", "ollama/phi3")

    # Create settings elements
    voice_switch = Switch(id="voice_switch", label="Enable Voice", initial=False)
    model_selector = Select(
        id="model_selector",
        label="Select Model",
        values=["ollama/phi3", "gpt-3.5-turbo", "gpt-4"],
        initial_index=0
    )

    # Send chat settings
    settings = await cl.ChatSettings([voice_switch, model_selector]).send()

    # Send welcome message
    await cl.Message(content="Welcome to the AI Assistant. How can I help you today?").send()

@cl.on_message
async def handle_message(message: cl.Message):
    # Handle the incoming message and respond accordingly
    if message.content.lower() == "upload file":
        # Ask the user to upload a file
        response = await cl.AskFileMessage(content="Please upload a file", accept=[".txt", ".pdf"]).send()

        # Process the uploaded file
        if isinstance(response, AskFileResponse):
            file = response.files[0]  # Assuming one file upload
            result = await process_file(file)
            await cl.Message(content=result).send()
    else:
        # Process the message using ChatHandler
        await chat_handler.handle_message(message)

@cl.on_settings_update
async def setup_agent(settings):
    # Update user settings when changed
    cl.user_session.set("use_voice", settings["voice_switch"])
    cl.user_session.set("model", settings["model_selector"])

    # Notify user of changes
    await cl.Message(
        content=f"Settings updated. Voice: {'enabled' if settings['voice_switch'] else 'disabled'}. "
        f"Model: {settings['model_selector']}."
    ).send()

async def process_file(file: AskFileResponse):
    # Your file processing logic here
    if file.type not in ["text/plain", "application/pdf"]:
        raise ValueError(f"Unsupported file type: {file.type}")

    # Assuming create_faiss_index is defined elsewhere
    index_path = create_faiss_index(file.path)
    return f"Processed {file.name} and added to the FAISS index."

if __name__ == "__main__":
    cl.run()