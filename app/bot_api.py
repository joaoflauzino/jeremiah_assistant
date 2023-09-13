import json
import logging

from config import config
from finance_choice.finance import Finance
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

(
    EXECUTE_CHOICE,
    GET_CATEGORY,
    GET_AMOUNT,
    REGISTER_BUDGET,
) = range(4)

url = "http://localhost:5000"

d_category_name = {
    "Comida - Final de Semana": 1,
    "Mercado": 2,
    "Farmácia": 3,
    "Sacolão": 4,
    "Outros": 5,
}


async def options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Olá, sou seu assistente virtual! Clique em dos itens que necessita de ajuda: \n\n /gastos -> Consulta e Registros dos limites e gastos mensais",
    )


async def finance_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [
        ["cadastrar limite de gastos", "consultar limite de gastos"],
        ["atualizar limite de gastos", "registrar gastos"],
        ["atualizar gastos"],
    ]
    await update.message.reply_text(
        "Ok. Sobre o assunto 'Gastos', o que você gostaria de fazer?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
        ),
    )

    return EXECUTE_CHOICE


async def get_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    global finance
    finance = Finance(msg)
    reply_keyboard = finance.set_board()
    await update.message.reply_text(
        "De qual categoria de gastos estamos falando?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
        ),
    )

    finance.save_step_name(msg)

    return GET_AMOUNT


async def get_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    finance.save_category_name(msg)

    budget = finance.get_budget()

    if budget["action"] == "consultar limite de gastos":
        response = finance.get_budget_database(budget["category_id"])

        if response.status_code == 404:
            await update.message.reply_text(
                f'Categoria "{budget.get("category_name")}" ainda não foi cadastrada!',
            )

            return ConversationHandler.END

        response_dict = json.loads(response.text)

        await update.message.reply_text(
            f'O limite para "{budget.get("category_name")}" é R${response_dict.get("budget")}!',
        )

        return ConversationHandler.END

    elif budget["action"] == "cadastrar limite de gastos":
        await update.message.reply_text(
            "Qual o limite de gastos?",
        )
        return REGISTER_BUDGET


async def register_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    budget = finance.save_amount(msg)
    response = finance.save_register()
    if response == 201:
        await update.message.reply_text(
            f"Ok. Registrei seu cadastro-> {budget}",
        )
    else:
        await update.message.reply_text(
            f"Houve algum problema com o cadastro do seu gasto. Erro: {response}",
        )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    logger.info("Usuário %s cancelou a conversa.", user.first_name)

    await update.message.reply_text(
        "Tchau. Precisando me chama!", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


async def not_implemented_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import pdb

    pdb.set_trace()
    await update.message.reply_text(
        "Esse item ainda não foi implementado.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


if __name__ == "__main__":
    application = ApplicationBuilder().token(config.TOKEN_TELEGRAM).build()

    options_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & (~filters.COMMAND), options)],
        states={},
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    finance_handler = ConversationHandler(
        entry_points=[CommandHandler("gastos", finance_choice)],
        states={
            EXECUTE_CHOICE: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), get_category)
            ],
            GET_AMOUNT: [MessageHandler(filters.TEXT & (~filters.COMMAND), get_amount)],
            REGISTER_BUDGET: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), register_budget)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(finance_handler)

    application.add_handler(options_handler)

    application.run_polling()
