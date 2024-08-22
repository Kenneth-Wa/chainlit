import chainlit as cl
from function_manager.function_manager import FunctionManager
from app.document_processor import DocumentProcessor
from app.speech_handler import SpeechHandler
from app.utils.oai import CustomEndpoint  # Update this import path

class ChatHandler:
    def __init__(self, function_manager: FunctionManager, document_processor: DocumentProcessor, speech_handler: SpeechHandler):
        self.function_manager = function_manager
        self.document_processor = document_processor
        self.speech_handler = speech_handler
        self.custom_endpoint = CustomEndpoint()

    async def handle_message(self, message: cl.Message):
        if message.elements and isinstance(message.elements[0], cl.Audio):
            text = await self.speech_handler.speech_to_text(message.elements[0])
        else:
            text = message.content

        response = await self.process_message(text)

        if cl.user_session.get("use_voice", False):
            audio = await self.speech_handler.text_to_speech(response)
            await cl.Message(content=response, elements=[audio]).send()
        else:
            await cl.Message(content=response).send()

    async def process_message(self, text: str):
        doc_answer = await self.document_processor.query(text)
        if doc_answer:
            return doc_answer

        # Use CustomEndpoint instead of OpenAI directly
        messages = [{"role": "user", "content": text}]
        try:
            response = self.custom_endpoint.generate(messages)
            return response
        except Exception as e:
            return f"An error occurred while processing your request: {str(e)}"

    async def stream_response(self, text: str):
        messages = [{"role": "user", "content": text}]
        try:
            async for chunk in self.custom_endpoint.stream(messages):
                yield chunk
        except Exception as e:
            yield f"An error occurred while streaming the response: {str(e)}"