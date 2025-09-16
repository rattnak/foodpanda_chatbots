
from telegram import InputFile, Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ContextTypes,ConversationHandler, ChatMemberHandler



# LAST STEP: Send Message to user to copy to the driver
async def handle_driver_message(update: Update, context: CallbackContext) -> None:
    # Message for Copy to clipboard
    with open("pickup.png", "rb") as img_file:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=InputFile(img_file),
            caption=(
                f"សូមចុចលើពាក្យខាងក្រោមដើម្បីកូពីសារ\n\n"
                f"`បងជួយយកកញ្ចប់អាហារខ្ញុំដាក់នៅតុជិតព្រះភូមិខាងមុខអគារ GIA និងបញ្ជាក់លេខកូដ4ខ្ទង់ test ប្រាប់បុគ្គលិកពាក់អាវ foodpanda ផងបង`"
            ),
            parse_mode="MarkdownV2",
        )


async def handle_screenshot(update: Update, context: CallbackContext):
    if update.message.photo:
        context.user_data["screenshot_file_id"] = update.message.photo[-1].file_id
        # TODO: Save to database
        
        await update.message.reply_text(
            "Thank you for providing the screenshot. We will review it and get back to you shortly."
        )
        await handle_driver_message(update, context)
        context.user_data['awaiting_screenshot'] = False
    else:
        await update.message.reply_text("Please upload a valid screenshot.")
    # return ConversationHandler.END


async def handle_skip_screenshot(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    await query.delete_message()
    # await query.answer("Skipping screenshot upload.")
    await handle_driver_message(update, context)
    context.user_data['awaiting_screenshot'] = False
    return ConversationHandler.END
