import logging

from config import config
from telegram import ReplyKeyboardRemove, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from conversation_handler.credit_card import (
    credit_card_choice,
    get_action,
    create_credit_card,
    get_credit_card_limit,
    get_credit_card_closing_date,
    EXECUTE_CREDIT_CARD_CHOICE,
    CREATE_CREDIT_CARD,
    GET_CREDIT_CARD_LIMIT,
    GET_CREDIT_CARD_CLOSING_DATE,
)

from conversation_handler.expenses import (
    finance_choice,
    get_category,
    get_amount,
    register_budget,
    update_budget,
    register_amount,
    update_amount,
    choose_transaction,
    delete_transaction,
    choose_interaction,
    EXECUTE_CHOICE,
    GET_AMOUNT,
    REGISTER_BUDGET,
    UPDATE_BUDGET,
    REGISTER_AMOUNT,
    UPDATE_AMOUNT,
    CHOOSE_TRANSACTION,
    DELETE_TRANSACTION,
    CHOOSE_INTERACTION,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

url = "http://localhost:5000"


async def options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Olá, sou seu assistente virtual! Clique em dos itens que necessita de ajuda: \n\n /gastos -> Consulta e Registros dos limites e gastos mensais \n\n /cartoes -> Consulta e Registros de cartão de crédito",
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    logger.info("Usuário %s cancelou a conversa.", user.first_name)

    await update.message.reply_text(
        "Tchau. Precisando me chama!", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


if __name__ == "__main__":
    application = ApplicationBuilder().token(config.TOKEN_TELEGRAM).build()

    options_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & (~filters.COMMAND), options)],
        states={},
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    credit_card_handler = ConversationHandler(
        entry_points=[CommandHandler("cartoes", credit_card_choice)],
        states={
            EXECUTE_CREDIT_CARD_CHOICE: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), get_action)
            ],
            CREATE_CREDIT_CARD: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), create_credit_card)
            ],
            GET_CREDIT_CARD_LIMIT: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), get_credit_card_limit)
            ],
            GET_CREDIT_CARD_CLOSING_DATE: [
                MessageHandler(
                    filters.TEXT & (~filters.COMMAND), get_credit_card_closing_date
                )
            ],
            CHOOSE_INTERACTION: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), choose_interaction)
            ],
        },
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
            UPDATE_BUDGET: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), update_budget)
            ],
            REGISTER_AMOUNT: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), register_amount)
            ],
            UPDATE_AMOUNT: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), update_amount)
            ],
            CHOOSE_TRANSACTION: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), choose_transaction)
            ],
            DELETE_TRANSACTION: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), delete_transaction)
            ],
            CHOOSE_INTERACTION: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), choose_interaction)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(credit_card_handler)

    application.add_handler(finance_handler)

    application.add_handler(options_handler)

    application.run_polling()
