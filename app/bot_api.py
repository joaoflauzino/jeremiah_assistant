import ast
import json
import logging

from config import config
from finance_choice.finance import Finance
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.constants import ParseMode
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
    UPDATE_BUDGET,
    REGISTER_AMOUNT,
    UPDATE_AMOUNT,
    CHOOSE_TRANSACTION,
    DELETE_TRANSACTION,
    CHOOSE_INTERACTION,
) = range(10)

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
        ["atualizar limite de gastos", "registrar gastos", "consultar gastos"],
        ["atualizar gastos", "deletar gastos"],
    ]
    await update.message.reply_text(
        "Ok. Sobre o assunto *Gastos*, o que você _gostaria_ de fazer?",
        parse_mode=ParseMode.MARKDOWN,
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

    # Cleaning transaction object for no conflicts
    finance.clean_transaction()

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

    budget = finance.get_transaction()

    if budget["action"] == "consultar limite de gastos":
        response = finance.get_budget_database(budget["category_id"])

        if response.status_code == 404:
            await update.message.reply_text(
                f'Categoria "{budget.get("category_name")}" ainda não foi cadastrada! \n\n Você gostaria de realizar outra operação?',
                reply_markup=ReplyKeyboardMarkup(
                    [["Sim", "Não"]],
                    one_time_keyboard=True,
                ),
            )

            return CHOOSE_INTERACTION

        response_dict = json.loads(response.text)

        await update.message.reply_text(
            f'O limite para "{budget.get("category_name")}" é R${response_dict.get("budget")}! \n\n Você gostaria de realizar outra operação?',
            reply_markup=ReplyKeyboardMarkup(
                [["Sim", "Não"]],
                one_time_keyboard=True,
            ),
        )

        return CHOOSE_INTERACTION

    elif budget["action"] == "cadastrar limite de gastos":
        await update.message.reply_text(
            "Qual o limite de gastos?",
        )
        return REGISTER_BUDGET

    elif budget["action"] == "atualizar limite de gastos":
        await update.message.reply_text(
            "Qual o novo limite de gastos?",
        )
        return UPDATE_BUDGET

    elif budget["action"] == "registrar gastos":
        await update.message.reply_text(
            "Qual o valor do gasto?",
        )
        return REGISTER_AMOUNT

    elif budget["action"] == "consultar gastos":
        response = finance.get_amount_database(budget["category_id"])

        if response.status_code == 404:
            await update.message.reply_text(
                f'Ainda não houve gastos para a categoria "{budget.get("category_name")}". \n\n Você gostaria de realizar outra operação?',
                reply_markup=ReplyKeyboardMarkup(
                    [["Sim", "Não"]],
                    one_time_keyboard=True,
                ),
            )
            return CHOOSE_INTERACTION
        response_dict = json.loads(response.text)

        await update.message.reply_text(
            f"Os gastos são: {response_dict}. \n\n Você gostaria de realizar outra operação?",
            reply_markup=ReplyKeyboardMarkup(
                [["Sim", "Não"]],
                one_time_keyboard=True,
            ),
        )
        return CHOOSE_INTERACTION

    elif budget["action"] == "atualizar gastos":
        await update.message.reply_text(
            "Qual o novo gasto?",
        )
        return UPDATE_AMOUNT

    elif budget["action"] == "deletar gastos":
        response = finance.get_amount_database(budget["category_id"])

        if response.status_code == 404:
            await update.message.reply_text(
                f'Você tem certeza que houve gastos pra essa categoria: "{budget.get("category_name")}"? Não encontrei no banco de dados. \n\n Você gostaria de realizar outra operação?',
                reply_markup=ReplyKeyboardMarkup(
                    [["Sim", "Não"]],
                    one_time_keyboard=True,
                ),
            )
            return CHOOSE_INTERACTION

        response_dict = json.loads(response.text)

        ids = [transaction["transaction_id"] for transaction in response_dict]
        finance.set_transaction_id(ids)

        await update.message.reply_text(
            f"Os gastos são: {response_dict}. Qual transação você deseja deletar? Ex: 2",
        )

        return DELETE_TRANSACTION


async def register_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    budget = finance.save_amount(msg)
    response = finance.save_register()
    if response == 201:
        await update.message.reply_text(
            f"Ok. Registrei seu cadastro-> {budget} \n\n Você gostaria de realizar outra operação?",
            reply_markup=ReplyKeyboardMarkup(
                [["Sim", "Não"]],
                one_time_keyboard=True,
            ),
        )
    else:
        await update.message.reply_text(
            f"Houve algum problema com o cadastro do seu limite de gastos. Erro: {response} \n\n Você gostaria de realizar outra operação?",
            reply_markup=ReplyKeyboardMarkup(
                [["Sim", "Não"]],
                one_time_keyboard=True,
            ),
        )

    return CHOOSE_INTERACTION


async def update_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    budget = finance.save_amount(msg)
    response = finance.update_register()
    if response == 201:
        await update.message.reply_text(
            f"Ok. Atualizei seu cadastro-> {budget}  \n\n Você gostaria de realizar outra operação?",
            reply_markup=ReplyKeyboardMarkup(
                [["Sim", "Não"]],
                one_time_keyboard=True,
            ),
        )

    else:
        await update.message.reply_text(
            f"Houve algum problema com a atualização do seu limite de gastos. Erro: {response} \n\n Você gostaria de realizar outra operação?",
            reply_markup=ReplyKeyboardMarkup(
                [["Sim", "Não"]],
                one_time_keyboard=True,
            ),
        )

    return CHOOSE_INTERACTION


async def register_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    budget = finance.save_amount(msg)
    response = finance.save_amount_register()
    if response == 201:
        await update.message.reply_text(
            f"Ok. Registrei seus gastos-> {budget} \n\n Você gostaria de realizar outra operação?",
            reply_markup=ReplyKeyboardMarkup(
                [["Sim", "Não"]],
                one_time_keyboard=True,
            ),
        )

    else:
        await update.message.reply_text(
            f"Houve algum problema com o cadastro do seu gasto. Erro: {response} \n\n Você gostaria de realizar outra operação?",
            reply_markup=ReplyKeyboardMarkup(
                [["Sim", "Não"]],
                one_time_keyboard=True,
            ),
        )
    return CHOOSE_INTERACTION


async def update_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    budget = finance.save_amount(msg)

    response = finance.get_amount_database(budget["category_id"])

    if response.status_code == 404:
        await update.message.reply_text(
            f'Ainda não houve gastos para a categoria "{budget.get("category_name")}". \n\n Você gostaria de realizar outra operação?',
            reply_markup=ReplyKeyboardMarkup(
                [["Sim", "Não"]],
                one_time_keyboard=True,
            ),
        )

        return CHOOSE_INTERACTION

    response_dict = json.loads(response.text)

    ids = [transaction["transaction_id"] for transaction in response_dict]
    finance.set_transaction_id(ids)

    await update.message.reply_text(
        f"Os gastos são: {response_dict}. Qual gasto você deseja atualizar? Ex.1"
    )

    return CHOOSE_TRANSACTION


async def choose_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    msg_eval = ast.literal_eval(msg)

    transactions_ids = finance.get_transactions_ids()

    if not isinstance(msg_eval, int) or msg_eval not in transactions_ids:
        await update.message.reply_text(
            f"Você não digitou um número válido: {msg_eval}. Os números de transações são: {transactions_ids} \n\n Você gostaria de realizar outra operação?",
            reply_markup=ReplyKeyboardMarkup(
                [["Sim", "Não"]],
                one_time_keyboard=True,
            ),
        )
        return CHOOSE_INTERACTION

    finance.save_transactions_ids(msg_eval)

    response = finance.update_amount()
    if response == 201:
        await update.message.reply_text(
            "Ok. Atualizei sua transação. \n\n Você gostaria de realizar outra operação?",
            reply_markup=ReplyKeyboardMarkup(
                [["Sim", "Não"]],
                one_time_keyboard=True,
            ),
        )
    else:
        await update.message.reply_text(
            f"Houve algum problema com a atualização da sua transação. Erro: {response} \n\n Você gostaria de realizar outra operação?",
            reply_markup=ReplyKeyboardMarkup(
                [["Sim", "Não"]],
                one_time_keyboard=True,
            ),
        )

    finance.clean_transaction_id()

    return CHOOSE_INTERACTION


async def delete_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    msg_eval = ast.literal_eval(msg)

    transactions_ids = finance.get_transactions_ids()

    if not isinstance(msg_eval, int) or msg_eval not in transactions_ids:
        await update.message.reply_text(
            f"Você não digitou um número válido: {msg_eval}. Os números de transações são: {transactions_ids} \n\n Você gostaria de realizar outra operação?",
            reply_markup=ReplyKeyboardMarkup(
                [["Sim", "Não"]],
                one_time_keyboard=True,
            ),
        )
        return CHOOSE_INTERACTION

    finance.save_transactions_ids(msg_eval)

    response = finance.delete_amount()
    if response == 200:
        await update.message.reply_text(
            "Ok. Deletei sua transação. \n\n Você gostaria de realizar outra operação?",
            reply_markup=ReplyKeyboardMarkup(
                [["Sim", "Não"]],
                one_time_keyboard=True,
            ),
        )
    else:
        await update.message.reply_text(
            f"Houve algum problema com a exclusão da sua transação. Erro: {response} \n\n Você gostaria de realizar outra operação?",
            reply_markup=ReplyKeyboardMarkup(
                [["Sim", "Não"]],
                one_time_keyboard=True,
            ),
        )
    return CHOOSE_INTERACTION


async def choose_interaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text

    if msg == "Sim":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Clique em dos itens que necessita de ajuda: \n\n /gastos -> Consulta e Registros dos limites e gastos mensais",
        )
        return ConversationHandler.END
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Fico feliz em ter ajudado, qualquer coisa pode me chamar!",
        )
        return ConversationHandler.END


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

    application.add_handler(finance_handler)

    application.add_handler(options_handler)

    application.run_polling()
