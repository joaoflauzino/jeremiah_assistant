from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)

from telegram import ReplyKeyboardMarkup, Update
from telegram.constants import ParseMode

from choices.credit_card import CreditCard
from conversation_handler.expenses import CHOOSE_INTERACTION


(
    EXECUTE_CREDIT_CARD_CHOICE,
    CREATE_CREDIT_CARD,
    GET_CREDIT_CARD,
    GET_CREDIT_CARD_LIMIT,
    GET_CREDIT_CARD_CLOSING_DATE,
) = range(5)


async def credit_card_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [
        ["cadastrar cartão de crédito", "consultar limite do cartão de crédito"],
        [
            "atualizar limite do cartão de crédito",
            "atualizar data de fechamento da fatura",
        ],
    ]
    await update.message.reply_text(
        "Ok. Sobre o assunto *Cartões*, o que você gostaria de fazer?",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
        ),
    )

    return EXECUTE_CREDIT_CARD_CHOICE


async def get_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    global credit_card
    credit_card = CreditCard(msg)

    # Cleaning transaction object for no conflicts
    credit_card.clean_transaction()

    credit_card.save_step_name(msg)

    if msg == "cadastrar cartão de crédito":
        await update.message.reply_text(
            "Digite o nome do cartão de crédito. Ex: Itau - JL",
        )
        return CREATE_CREDIT_CARD

    return ConversationHandler.END


async def create_credit_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    credit_card.save_credit_card_name(msg)

    await update.message.reply_text(
        "Qual o limite do cartão?",
    )
    return GET_CREDIT_CARD_LIMIT


async def get_credit_card_limit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    credit_card.save_credit_card_limit(msg)
    await update.message.reply_text(
        "Qual a data de fechamento da fatura?",
    )
    return GET_CREDIT_CARD_CLOSING_DATE


async def get_credit_card_closing_date(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    msg = update.message.text
    credit_card.save_credit_card_closing_date(msg)
    response = credit_card.create_credit_card_database()

    if response.status_code == 201:
        await update.message.reply_text(
            "Cartão de crédito cadastrado com sucesso! \n\n Você gostaria de realizar outra operação?",
            reply_markup=ReplyKeyboardMarkup(
                [["Sim", "Não"]],
                one_time_keyboard=True,
            ),
        )

        return CHOOSE_INTERACTION

    await update.message.reply_text(
        "Houve algum problema na hora de cadastrar o cartão de crédito. \n Gostaria de realizar outra operação?",
        reply_markup=ReplyKeyboardMarkup(
            [["Sim", "Não"]],
            one_time_keyboard=True,
        ),
    )
    return CHOOSE_INTERACTION
