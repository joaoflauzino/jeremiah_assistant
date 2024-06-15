import json
import os

import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    filters,
)

load_dotenv()


ASSISTANT_URL = os.environ["ASSISTANT_URL"]
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]


async def start(update: Update, context: CallbackContext) -> None:
    if update.message:
        await update.message.reply_text("Olá! Eu sou o Jeremias, seu assistente financeiro. Como posso ajudar?")


async def handle_message(update: Update, context: CallbackContext) -> None:
    if update.message:
        user_message = update.message.text
        response = requests.post(url=f"{ASSISTANT_URL}/assistant", data=json.dumps({"text": user_message}))
        await update.message.reply_text(response.text)


def main() -> None:
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()


if __name__ == "__main__":
    main()
