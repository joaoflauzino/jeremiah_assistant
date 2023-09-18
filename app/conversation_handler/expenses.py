import ast
import json

from choices.finance import Finance
from telegram import ReplyKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)

(
    EXECUTE_CHOICE,
    GET_AMOUNT,
    REGISTER_BUDGET,
    UPDATE_BUDGET,
    REGISTER_AMOUNT,
    UPDATE_AMOUNT,
    CHOOSE_TRANSACTION,
    DELETE_TRANSACTION,
    CHOOSE_INTERACTION,
) = range(9)


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
    chat_id = update.message.chat_id
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

        import pandas as pd

        table = pd.DataFrame(response_dict)
        table.columns = ["valor", "categoria", "transação", "data"]

        import plotly.graph_objects as go
        import plotly
        import base64

        fig = go.Figure(
            data=[
                go.Table(
                    header=dict(values=list(table.columns), align="center"),
                    cells=dict(
                        values=table.values.transpose(),
                        fill_color=[["white", "lightgrey"] * table.shape[0]],
                        align="center",
                    ),
                )
            ]
        )

        # convert graph to PNG and encode it
        png = plotly.io.to_image(fig)
        png_base64 = base64.b64encode(png).decode("ascii")

        image_bytes = base64.b64decode(png_base64)

        from telegram import InputFile
        import io

        await context.bot.send_message(chat_id=chat_id, text="Os gastos são: \n")

        await context.bot.send_photo(
            chat_id=chat_id,
            photo=InputFile(io.BytesIO(image_bytes)),
        )

        await update.message.reply_text(
            "Você gostaria de realizar outra operação?",
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
    # chat_id = update.message.chat_id

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

    # import pandas as pd

    # table = pd.DataFrame(response_dict)
    # table.columns = ["categoria", "transação", "data", "valor"]

    # import plotly.graph_objects as go
    # import plotly
    # import base64

    # fig = go.Figure(
    #     data=[
    #         go.Table(
    #             header=dict(values=list(table.columns), align="center"),
    #             cells=dict(
    #                 values=table.values.transpose(),
    #                 fill_color=[["white", "lightgrey"] * table.shape[0]],
    #                 align="center",
    #             ),
    #         )
    #     ]
    # )

    # # convert graph to PNG and encode it
    # png = plotly.io.to_image(fig)
    # png_base64 = base64.b64encode(png).decode("ascii")

    # image_bytes = base64.b64decode(png_base64)

    # from telegram import InputFile
    # import io

    # await update.message.reply_text(
    #     f"Os gastos são: \n\n Qual gasto você deseja atualizar? Ex.1",
    #     parse_mode=ParseMode.HTML,
    # )

    # await context.bot.send_message(chat_id=chat_id, text="Os gastos são: \n")

    # await context.bot.send_photo(
    #     chat_id=chat_id,
    #     photo=InputFile(io.BytesIO(image_bytes)),
    # )

    # await context.bot.send_message(
    #     chat_id=chat_id, text="Qual gasto você deseja atualizar? Ex.1"
    # )

    await update.message.reply_text(
        f"Os gastos são: {response_dict} \n\n Qual gasto você deseja atualizar? Ex.1",
        parse_mode=ParseMode.HTML,
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
            text="Clique em dos itens que necessita de ajuda: \n\n /gastos -> Consulta e Registros dos limites e gastos mensais \n\n /cartoes -> Consulta e Registros de cartão de crédito",
        )
        return ConversationHandler.END
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Fico feliz em ter ajudado, qualquer coisa pode me chamar!",
        )
        return ConversationHandler.END
