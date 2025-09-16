from check_user import *
from check_user import is_user_exists, is_order_exists
from telegram import (
    Bot,
    InputFile,
    InlineKeyboardButton,
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
    ContextTypes,
    ConversationHandler,
    ChatMemberHandler,
    CallbackQueryHandler,
)
from check_user import (
    validate_order_id,
    extract_last_4_digits,
    Batch,
    Order,
    SessionLocal,
)
from collections import defaultdict


# Define Gatherer and Dropper Privileges (example user IDs)
GATHERER_PRIVILEGES = {"sreypichun"}
DROPPER_PRIVILEGES = {"lengkimtry", }

# Telegram bot setup

TOKEN = '7402813091:AAH5xQ8w08YAX7NBKVjpqlgnz5livM4TwXE'
bot = Bot(TOKEN)
SCREENSHOT = range(1)


async def start(update: Update, context: CallbackContext):
    username = update.message.from_user.username

    if username in GATHERER_PRIVILEGES:
        welcome_message = "Welcome, Gatherer! You have the privilege to manage batches."
        keyboard = [["Pickup"], ["View Pending Batch"], ["Cancel"]]
        reply_markup = ReplyKeyboardMarkup(
            keyboard, one_time_keyboard=False, resize_keyboard=True
        )
        await update.message.reply_text(
            text=welcome_message, reply_markup=reply_markup, parse_mode="HTML"
        )
    elif username in DROPPER_PRIVILEGES:
        welcome_message = (
            "Welcome, Dropper! You have the privilege to start & end delivery."
        )
        keyboard = [["View Submitted Batch"],["View Delivering Batch"], ["Cancel"]]
        reply_markup = ReplyKeyboardMarkup(
            keyboard, one_time_keyboard=False, resize_keyboard=True
        )
        await update.message.reply_text(
            text=welcome_message, reply_markup=reply_markup, parse_mode="HTML"
        )
    else:
        welcome_message = "Welcome to foodpanda GIA FloorExpress Bot!\nស្វាគមន៍មកកាន់ការប្រើប្រាស់សេវាកម្មជញ្ជូនអារហារ FloorExpress នៅអគារ GIA!"
        keyboard = [["Use floorExpress", "Cancel"]]
        reply_markup = ReplyKeyboardMarkup(
            keyboard, one_time_keyboard=False, resize_keyboard=True
        )
        await update.message.reply_text(
            text=welcome_message, reply_markup=reply_markup, parse_mode="HTML"
        )


async def send_telegram_message(chat_id, message):
    await bot.send_message(chat_id=chat_id, text=message)
async def button(update: Update, context: CallbackContext):
    # Check if the update is a message or a callback query
    if update.message:
        text = update.message.text
        username = update.message.from_user.username
        chat_id = update.message.chat_id
    elif update.callback_query:
        text = update.callback_query.data
        username = update.callback_query.from_user.username
        chat_id = update.callback_query.message.chat_id
        await update.callback_query.answer()  # Acknowledge the callback query to prevent a loading indicator
    
    print(f"Received button text: {text}")  # Debug print

    if text == "Cancel":
        await context.bot.send_message(
            chat_id=chat_id,
            text="Action canceled. Please click /start to try again.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    if text == "Use floorExpress":
        # Assuming is_user_exists is implemented elsewhere in your code
        # if is_user_exists(chat_id, username):
        await context.bot.send_message(
            chat_id=chat_id,
            

            text="Please enter the following details, each on a new line:\nសូមវាយបញ្ចូលព័ត៌មានតាមលំដាប់ដូចខាងក្រោមនេះជាជួរៗ៖ \n\n1. Order ID (format: xxxx-xxxx-xxxx)លេខកូដ14ខ្ទង់(xxxx-xxxx-xxxx)\n\n2. Phone number លេខទូរស័ព្ទ\n\n3. Floor number លេខជាន់អគារ \n\nExample: \n\n1234-1234-1234 \n 0123456789 \n 33",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data["awaiting_order_details"] = True
        # else:
        #     await update.message.reply_text(
        #         "You are not authorized to use floorExpress."
        #     )

    elif text in ["Pickup", "View Pending Batch", "Submit Batch"]:
        if username in GATHERER_PRIVILEGES:
            if text == "Pickup":
                await pickup(update, context)
            elif text == "View Pending Batch":
                await view_pending_batch(update, context)
            elif text == "Submit Batch":
                await submit_batch(update, context)
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text="You are not authorized to perform this action.\nអ្នកមិនត្រូវបានអនុញ្ញាតអោយប្រើប្រាស់ទេ។"
            )

    elif text in ["View Submitted Batch", "View Delivering Batch", "Start Delivery", "End Delivery"]:
        if username in DROPPER_PRIVILEGES:
            if text == "View Submitted Batch":
                await view_submitted_batch(update, context)
            elif text== "View Delivering Batch":
                await view_delivering_batch(update, context)
            # elif text == "Start Delivery":
            #     await start_delivery(update, context)
            # elif text == "End Delivery":
            #     await end_delivery(update, context)
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text="You are not authorized to perform this action."
            )


async def pickup(update: Update, context: CallbackContext):
    db = SessionLocal()
    orders_to_pickup = db.query(Order).filter(Order.status == "Arrived at GIA").all()

    if not orders_to_pickup:
        await update.message.reply_text("No orders with 'Arrived at GIA' status.")
        db.close()
        return

    # Organize orders by floor number
    orders_by_floor = defaultdict(lambda: {'verification_ids': [], 'count': 0})
    for order in orders_to_pickup:
        orders_by_floor[order.gia_floor]['verification_ids'].append(order.verification_id)
        orders_by_floor[order.gia_floor]['count'] += 1

    # Build the message
    total_quantity = 0
    message = "*Orders to Pickup:*\n\n"
    for floor, data in sorted(orders_by_floor.items()):
        verification_ids = ', '.join(data['verification_ids'])
        message += (f"Floor Number {floor}\n"
                    f"Verify-ID: {verification_ids}\n"
                    f"Quantity Per Floor: {data['count']}\n\n")
        total_quantity += data['count']

    message += f"Total Quantity: {total_quantity}"
    keyboard = [[InlineKeyboardButton("Confirm Pickup", callback_data='confirm_pickup'), InlineKeyboardButton("Cancel", callback_data='cancel')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # keyboard = [[KeyboardButton("Confirm Pickup"), KeyboardButton("Cancel")]]
    # reply_markup = ReplyKeyboardMarkup(
    #     keyboard, one_time_keyboard=True, resize_keyboard=True
    # )
    await update.message.reply_text(
        message, reply_markup=reply_markup, parse_mode="Markdown"
    )
    context.user_data["orders_to_pickup"] = [order.id for order in orders_to_pickup]

    db.close()

# GATHERER
async def handle_pickup_confirmation(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    username = query.from_user.username

    if username in GATHERER_PRIVILEGES:
        if data == 'confirm_pickup':
            order_ids = context.user_data.get("orders_to_pickup", [])
            db = SessionLocal()
            for order_id in order_ids:
                order = db.query(Order).filter(Order.id == order_id).first()
                if order:
                    order.status = "Picked up by Gatherer"
                    db.add(order)
            db.commit()
            db.close()
            await query.message.reply_text(
                "Orders have been successfully marked as picked up by Gatherer.",
                reply_markup=ReplyKeyboardRemove(),
            )
            context.user_data.pop("orders_to_pickup", None)  # Clear orders_to_pickup after processing
        elif data == 'cancel':
            await query.message.reply_text(
                "Pickup action canceled.", reply_markup=ReplyKeyboardRemove()
            )
    else:
        await query.message.reply_text("You are not authorized to perform this action.")



async def view_pending_batch(update: Update, context: CallbackContext):
    db = SessionLocal()
    pending_orders = (
        db.query(Order).filter(Order.status == "Picked up by Gatherer").all()
    )

    if not pending_orders:
        await update.message.reply_text(
            "No orders with 'Picked up by Gatherer' status."
        )
        db.close()
        return

    # Organize orders by floor number
    orders_by_floor = defaultdict(lambda: {'order_ids': [], 'count': 0})
    for order in pending_orders:
        orders_by_floor[order.gia_floor]['order_ids'].append(order.order_id)
        orders_by_floor[order.gia_floor]['count'] += 1

    # Build the message
    total_quantity = 0
    message = "*Pending Orders:*\n\n"
    for floor, data in sorted(orders_by_floor.items()):
        order_ids = ', '.join(data['order_ids'])
        message += (f"Floor Number {floor}\n"
                    f"Verify-ID: {order_ids}\n"
                    f"Quantity Per Floor: {data['count']}\n\n")
        total_quantity += data['count']

    message += f"Total Quantity: {total_quantity}"

    # keyboard = [[KeyboardButton("Submit Batch"), KeyboardButton("Cancel")]]
    # reply_markup = ReplyKeyboardMarkup(
    #     keyboard, one_time_keyboard=True, resize_keyboard=True
    # )
    # await update.message.reply_text(message, parse_mode="Markdown", reply_markup=reply_markup)

    keyboard = [[InlineKeyboardButton("Submit Batch", callback_data='submit_batch'), InlineKeyboardButton("Cancel", callback_data='cancel')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        message, reply_markup=reply_markup, parse_mode="Markdown"
    )
    db.close()
async def submit_batch(update: Update, context: CallbackContext):
    db = SessionLocal()

    pending_batches = (
        db.query(Order).filter(Order.status == "Picked up by Gatherer").all()
    )

    if not pending_batches:
        # If called by a callback query, use `update.callback_query`
        if update.callback_query:
            await update.callback_query.answer("No pending batches to submit.")
            await update.callback_query.message.reply_text("No pending batches to submit.")
        else:
            await update.message.reply_text("No pending batches to submit.")
        db.close()
        return

    current_batch_number = (
        db.query(Batch)
        .filter(Batch.batch_number != None)
        .order_by(Batch.id.desc())
        .first()
    )
    if current_batch_number:
        current_batch_number = int(
            current_batch_number.batch_number.split("Batch Number ")[-1]
        )
        new_batch_number = f"Batch Number {current_batch_number + 1}"
    else:
        new_batch_number = "Batch Number 1"

    for order in pending_batches:
        order.status = "Submitted Batch"
        order.batch_number = new_batch_number
        db.add(
            Batch(
                verification_id=order.verification_id,
                gia_floor=order.gia_floor,
                status="Submitted Batch",
                batch_number=new_batch_number,
            )
        )

    db.commit()
    db.close()

    # Check if the update came from a callback query
    if update.callback_query:
        chat_id = update.callback_query.message.chat_id
    else:
        chat_id = update.message.chat_id

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"Submitted all pending batches with Batch Number {new_batch_number}."
    )




async def view_submitted_batch(update: Update, context: CallbackContext):
    db = SessionLocal()

    submitted_orders = db.query(Order).filter(Order.status == "Submitted Batch").all()

    if not submitted_orders:
        await update.message.reply_text("No submitted batches found.")
        db.close()
        return

    # Categorize orders by floor
    orders_by_floor = {}
    for order in submitted_orders:
        floor = order.gia_floor
        if floor not in orders_by_floor:
            orders_by_floor[floor] = []
        orders_by_floor[floor].append(order.order_id)

    # Prepare the response message
    message = "*Submitted Orders*\n\n"
    total_orders = 0
    for floor, order_ids in orders_by_floor.items():
        order_list = ", ".join(order_ids)
        order_quantity = len(order_ids)
        total_orders += order_quantity
        message += (
            f"Floor {floor}:\n"
            f"Order-ID: {order_list}\n"
            f"Order Quantity: {order_quantity}\n\n"
        )

    message += f"Total Orders: {total_orders}\n"

    # Add Inline Keyboard for "Start Delivery"
    keyboard = [[InlineKeyboardButton("Start Delivery", callback_data='start_delivery')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode="Markdown")
    db.close()


async def view_delivering_batch(update: Update, context: CallbackContext):
    db = SessionLocal()

    submitted_orders = db.query(Order).filter(Order.status == "Delivering").all()

    if not submitted_orders:
        await update.message.reply_text("No Delivering batches found.")
        db.close()
        return

    # Categorize orders by floor
    orders_by_floor = {}
    for order in submitted_orders:
        floor = order.gia_floor
        if floor not in orders_by_floor:
            orders_by_floor[floor] = []
        orders_by_floor[floor].append(order.order_id)

    # Prepare the response message
    message = "*Delivering Orders*\n\n"
    total_orders = 0
    for floor, order_ids in orders_by_floor.items():
        order_list = ", ".join(order_ids)
        order_quantity = len(order_ids)
        total_orders += order_quantity
        message += (
            f"Floor {floor}:\n"
            f"Order-ID: {order_list}\n"
            f"Order Quantity: {order_quantity}\n\n"
        )

    message += f"Total Orders: {total_orders}\n"

    # Add Inline Keyboard for "Start Delivery"
    keyboard = [[InlineKeyboardButton("End Delivery", callback_data='end_delivery')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode="Markdown")
    db.close()

async def start_delivery(update: Update, context: CallbackContext):
    if update.callback_query:
        query = update.callback_query
        await query.answer()  # Acknowledge the callback query
        
        db = SessionLocal()
        orders_to_update = db.query(Order).filter(Order.status == "Submitted Batch").all()

        if not orders_to_update:
            await query.message.reply_text("No orders to start delivery.")
            db.close()
            return

        # Track users to notify with multiple orders
        users_to_notify = {}

        for order in orders_to_update:
            order.status = "Delivering"
            db.add(order)
            if order.chat_id not in users_to_notify:
                users_to_notify[order.chat_id] = {
                    'username': order.telegram_name,
                    'orders': []
                }
            users_to_notify[order.chat_id]['orders'].append(order.verification_id)

        db.commit()
        db.close()
        
        await query.message.reply_text(
            "All submitted batches have been updated to 'Delivering'."
        )

        # Notify each user about their orders
        for chat_id, user_info in users_to_notify.items():
            username = user_info['username']
            orders = user_info['orders']
            order_list = ", ".join(orders)
            message = f"Hi {username}, your orders ({order_list}) have started to be delivered."
            await context.bot.send_message(
                chat_id=chat_id,
                text=message
            )

    else:
        await update.message.reply_text("Invalid request. Please click /start to try again.")
async def end_delivery(update: Update, context: CallbackContext):
    if update.callback_query:
        query = update.callback_query
        await query.answer()  # Acknowledge the callback query
        
        db = SessionLocal()
        orders_to_update = db.query(Order).filter(Order.status == "Delivering").all()

        if not orders_to_update:
            await query.message.reply_text("No orders to mark as delivered.")
            db.close()
            return

        # Update orders and track users to notify
        users_to_notify = {}

        for order in orders_to_update:
            order.status = "Delivered"
            db.add(order)
            if order.chat_id not in users_to_notify:
                users_to_notify[order.chat_id] = {
                    'username': order.telegram_name,
                    'orders': []
                }
            users_to_notify[order.chat_id]['orders'].append(order.verification_id)

        db.commit()
        db.close()

        # Notify each user that their orders have arrived
        for chat_id, user_info in users_to_notify.items():
            username = user_info['username']
            orders = user_info['orders']
            order_list = ", ".join(orders)
            message = (
                f"Greetings {username}, your order ({order_list}) have arrived."

                f"Please click Accept if you have received your order at your floor or Decline if you have not!\n\nជម្រាបសួរ! អាហាររបស់អ្នកត្រូវបានដឹកជញ្ជូនមកដល់ជាន់អ្នកហើយ\nសូមជួយចុច accept រឺ decline"
            )
            keyboard = [
                [InlineKeyboardButton("Accept", callback_data=f"confirm_{order_id}") for order_id in orders],
                [InlineKeyboardButton("Decline", callback_data=f"decline_{order_id}") for order_id in orders],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(
                chat_id=chat_id,
                text=message,
                reply_markup=reply_markup
            )

        await query.message.reply_text(
            "All delivering orders have been updated to 'Delivered'."
        )
    else:
        await update.message.reply_text("Invalid request.")
# async def confirm_order(update: Update, context: CallbackContext):
#     query = update.callback_query
#     await query.answer()  # Acknowledge the callback query

#     # Parse the callback data
#     callback_data = query.data
#     chat_id = query.from_user.id
#     action, order_id = callback_data.split('_', 1)  # Extract action and order_id

#     # Determine the status update based on the callback data
#     if action == "confirm":
#         status_update = "Confirmed"
#     elif action == "decline":
#         status_update = "Declined"
#     else:
#         await query.message.reply_text("Invalid action.")
#         return

#     # Update the order status in the database
#     db = SessionLocal()
#     order = db.query(Order).filter(Order.verification_id == order_id).first()
#     if not order:
#         await query.message.reply_text("Order not found.")
#         db.close()
#         return

#     order.status = status_update
#     db.add(order)
#     db.commit()
#     db.close()

#     # Notify the user about the action
#     await query.message.reply_text(f"Order {order_id} has been {status_update.lower()}.")

#     # Optionally, send a confirmation message to the user
#     await context.bot.send_message(
#         chat_id=chat_id,
#         text=f"Your order {order_id} has been {status_update.lower()}. Thank you for your response."
#     )

# async def decline_order(update: Update, context: CallbackContext):
#     pass


async def accept_order(update: Update, context: CallbackContext):
    query = update.callback_query
    callback_data = query.data
    order_id = callback_data.split("_")[1]  # Extract order ID

    # Update order status in the database
    db = SessionLocal()
    order = db.query(Order).filter(Order.verification_id == order_id).first()
    
    if order:
        order.status = "Accepted"
        db.add(order)
        db.commit()
        response_message = "Your order has been accepted. Thank you!"
    else:
        response_message = "Order not found."

    db.close()

    await query.answer()  # Acknowledge the callback query
    await query.edit_message_text(text=response_message)

async def decline_order(update: Update, context: CallbackContext):
    query = update.callback_query
    callback_data = query.data
    order_id = callback_data.split("_")[1]  # Extract order ID

    # Update order status in the database
    db = SessionLocal()
    order = db.query(Order).filter(Order.verification_id == order_id).first()
    
    if order:
        order.status = "Declined"
        db.add(order)
        db.commit()
        response_message = "Your order has been declined. We will contact you soon."
    else:
        response_message = "Order not found."

    db.close()

    await query.answer()  # Acknowledge the callback query
    await query.edit_message_text(text=response_message)

async def message_handler(update: Update, context: CallbackContext):
    user_message = update.message.text
    username = update.message.from_user.username
    if (username not in GATHERER_PRIVILEGES) or (username not in DROPPER_PRIVILEGES):
        if (
            "awaiting_order_details" in context.user_data
            and context.user_data["awaiting_order_details"]
        ):
            context.user_data["awaiting_order_details"] = False
            details = user_message.split("\n")
            if len(details) < 3:
                await update.message.reply_text(
                    "Please provide all required details: Order ID, Phone number, Floor number.\\"
                )
                return
            
            order_id, phone_number, floor_number = details
            
            if not validate_order_id(order_id):
                await update.message.reply_text(
                    "Invalid Order ID format. Please use the format xxxx-xxxx-xxxx."
                )
                return

            verification_id = extract_last_4_digits(order_id)
            # if is_order_exists(verification_id):
            #     await update.message.reply_text(
            #         "Order ID is not correct. Please input again"
            #     )
            #     return
            context.user_data['order_details'] = {
                'telegram_name':update.message.from_user.full_name,
                'username':update.message.from_user.username,
                'chat_id': update.message.from_user.id,
                'order_id':order_id,
                'verification_id':verification_id,
                'phone_number':phone_number,
                'gia_floor':floor_number,
                'status':"",
            }
            # Reduced Message: Summary
            summary_message = (
                f"*Summary:*\n\n"
                f"Order-ID: `{order_id}`\n"
                f"Phone Number: `{phone_number}`\n"
                f"Verification ID for Deliveryman & Picker: `{verification_id}`\n"
                f"Floor Number: `{floor_number}`\n"
            )
            keyboard = [
                [KeyboardButton("Confirm"), KeyboardButton("Cancel")]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text(summary_message, reply_markup=reply_markup, parse_mode='Markdown')
            
            context.user_data['awaiting_confirmation'] = True
            context.user_data['awaiting_order_details'] = False

            # await update.message.reply_text("Order details submitted successfully!")

        elif context.user_data.get('awaiting_confirmation'):
            if update.message.text == "Confirm":
                # Retrieve the stored order details
                order_details = context.user_data['order_details']
                
                # Save to SQLite database
                db = SessionLocal()
                new_order = Order(
                    telegram_name=order_details['telegram_name'],
                    username=order_details['username'],
                    chat_id = order_details["chat_id"],
                    order_id=order_details['order_id'],
                    verification_id=order_details['verification_id'],
                    phone_number=order_details['phone_number'],
                    gia_floor=order_details['gia_floor'],
                    status=order_details['status'] 
                )
                db.add(new_order)
                db.commit()

                
                # # Save to Batch table if GIA Arrival is Yes
                # if new_order.gia_arrival == 'Arrived at GIA':
                #     batch = Batch(
                #         verification_id=order_details['verification_id'],
                #         # gia_floor=order_details['gia_floor'],
                #         status='Arrived at GIA',
                #         batch_number=None  # You might want to adjust this if you handle batch numbers differently
                #     )
                #     db.add(batch)
                #     db.commit()

                # ADD: Optional option to send screenshot
                # with open("receipt.jpg", "rb") as img_file:
                #     await context.bot.send_photo(
                #         chat_id=update.effective_chat.id,
                #         photo=InputFile(img_file),
                #         caption=(
                #             "Attaching a screenshot of your order is optional, but it can help us ensure everything is correct\\. Thanks for considering it\\!"
                #             "\n_Please upload it now\\. Press 'Skip' if you prefer not to\\._"
                #         ),
                #         reply_markup=InlineKeyboardMarkup(
                #             [
                #                 [InlineKeyboardButton("Skip", callback_data="skip")],
                #             ]
                #         ),
                #         parse_mode="MarkdownV2",
                #     )
                # context.user_data["awaiting_screenshot"] = True
                await handle_driver_message(update, context)
            elif update.message.text == "Cancel":
                await update.message.reply_text("Order has been cancelled. Click /start to try again", reply_markup=ReplyKeyboardRemove())
                context.user_data.clear()
            else:
                await update.message.reply_text("Please choose either 'Confirm' or 'Cancel'.")
        else:
            await update.message.reply_text(
                "Invalid input or no action selected. Please use /start to try again."
            )
    else:
        await update.message.reply_text(
            "You are Admin"
        )


# LAST STEP: Send Message to user to copy to the driver
async def handle_driver_message(update: Update, context: CallbackContext) -> None:
    # Message for Copy to clipboard
    order_details = context.user_data['order_details']

    with open("pickup.jpg", "rb") as img_file:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=InputFile(img_file),
            caption=(
                f"សូមចុចលើពាក្យខាងក្រោមដើម្បីកូពីសារ\n\n"
                f"*`បងជួយយកកញ្ចប់អាហារខ្ញុំដាក់នៅតុជិតព្រះភូមិខាងមុខអគារ GIA និងបញ្ជាក់លេខកូដ4ខ្ទង់ {order_details['verification_id']} ប្រាប់បុគ្គលិកពាក់អាវ foodpanda ផងបង`*"
            ),
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="MarkdownV2",
        )

# async def screenshot_handler(update: Update, context: CallbackContext):
#     if (
#         "awaiting_screenshot" in context.user_data
#         and context.user_data["awaiting_screenshot"]
#     ):
#         if update.message.photo:
#             context.user_data["screenshot_file_id"] = update.message.photo[-1].file_id
#             # TODO: Save to database
#             print("DONE")
#             await update.message.reply_text(
#                 "Thank you for providing the screenshot. "
#             )
#             context.user_data["awaiting_screenshot"] = False
#             await handle_driver_message(update, context)
#         else:
#             await update.message.reply_text("Please upload a valid screenshot.")
    
#     else:
        
#         await update.message.reply_text(
#             "Unexpected photo upload. Please use /start to try again."
#         )


# async def skip_screenshot(update: Update, context: CallbackContext):
#     query = update.callback_query
#     await query.answer()
#     # await query.delete_message()
#     # await query.answer("Skipping screenshot upload.")
#     await handle_driver_message(update, context)
#     context.user_data['awaiting_screenshot'] = False
#     return ConversationHandler.END


async def cancel_button(update: Update, context: CallbackContext):
    query = update.callback_query
    query_data = query.data
    username = query.from_user.username
    # Check if the update came from a callback query
    if update.callback_query:
        chat_id = update.callback_query.message.chat_id
    else:
        chat_id = update.message.chat_id
    if query_data == 'cancel':
        await context.bot.send_message(chat_id=chat_id,text= "Action canceled. Please click /start to try again.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return
    
    # elif query_data == 'skip':
    #     await handle_driver_message(update, context)
    #     context.user_data['awaiting_screenshot'] = False
    #     return 