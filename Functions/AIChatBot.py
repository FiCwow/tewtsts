# Functions/AIChatBot.py
import logging
from transformers import pipeline

chatbot = None

def init():
    global chatbot
    try:
        logging.info("Ładowanie AI ChatBota...")
        chatbot = pipeline("conversational", model="microsoft/DialoGPT-small")
        logging.info("AI ChatBot gotowy!")
    except Exception as e:
        logging.error(f"AI nie załadowany: {e}")

def respond(message: str) -> str:
    if not chatbot:
        return "AI nie działa."
    try:
        resp = chatbot(message)
        return resp[-1]['generated_text']
    except:
        return "Błąd AI."