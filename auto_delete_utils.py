from telegram import Update
from telegram.ext import  CallbackContext

async def new_member(update: Update, context: CallbackContext) -> None:
    for new_member in update.message.new_chat_members:
        await update.message.delete()

async def member_left(update: Update, context: CallbackContext) -> None:
    left_member = update.message.left_chat_member
    await update.message.delete()