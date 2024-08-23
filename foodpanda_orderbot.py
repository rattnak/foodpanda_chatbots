from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
import re

# Database setup using SQLite
DATABASE_URL = "sqlite:///./database.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Existing Order table
class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, index=True, nullable=False)
    verification_id = Column(String, nullable=False)
    gia_floor = Column(String, nullable=False)

# New ReceivedOrder table
class ReceivedOrder(Base):
    __tablename__ = "received_orders"
    id = Column(Integer, primary_key=True, index=True)
    verification_id = Column(String, index=True, nullable=False)
    gia_floor = Column(String, nullable=False)

Base.metadata.create_all(bind=engine)

# Telegram bot setup
TOKEN = '7402813091:AAH5xQ8w08YAX7NBKVjpqlgnz5livM4TwXE'

def validate_order_id(order_id):
    pattern = r'^[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}$'
    return re.match(pattern, order_id) is not None

def extract_last_4_digits(order_id):
    if validate_order_id(order_id):
        return order_id[-4:]
    else:
        return "Invalid format"

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text('Welcome to the foodpanda GIA Floor Delivery Bot! Use /help to proceed.')

async def help_command(update: Update, context: CallbackContext):
    await update.message.reply_text(
        'Copy-paste your foodpanda Order ID so we can have our picker drop off your order at your floor in GIA Tower.\n'
        'Click /floorExpress to get started.'
    )

async def floor_express(update: Update, context: CallbackContext):
    await update.message.reply_text('Please copy-paste your foodpanda Order ID (format: xxxx-xxxx-xxxx).')
    context.user_data['awaiting_order_id'] = True

async def handle_message(update: Update, context: CallbackContext):
    if context.user_data.get('awaiting_order_id'):
        context.user_data['order_id'] = update.message.text
        order_id = update.message.text
        
        if validate_order_id(order_id):
            await update.message.reply_text('Please enter the floor number (43 is the maximum floor number).')
            context.user_data['awaiting_order_id'] = False
            context.user_data['awaiting_gia_floor'] = True
        else:
            await update.message.reply_text("Invalid order ID format. Please enter a valid order ID (xxxx-xxxx-xxxx).")
    
    elif context.user_data.get('awaiting_gia_floor'):
        gia_floor = update.message.text
        
        if gia_floor.isdigit() and 1 <= int(gia_floor) <= 43:
            order_id = context.user_data.get('order_id')
            
            # Save to SQLite database
            db = SessionLocal()
            verification_id = extract_last_4_digits(order_id)
            db_order = Order(order_id=order_id, verification_id=verification_id, gia_floor=gia_floor)
            db.add(db_order)
            db.commit()
            
            # Save to received_orders table
            received_order = ReceivedOrder(verification_id=verification_id, gia_floor=gia_floor)
            db.add(received_order)
            db.commit()
            db.close()

            # Store verification_id in user_data
            context.user_data['verification_id'] = verification_id

            # Message 1: Summary
            summary_message = (f"*Summary:*\n\n"
                               f"Order-ID: `{order_id}`\n"
                               f"Verification ID for Deliveryman & Picker: `{verification_id}`\n"
                               f"Floor Number: `{gia_floor}`")
            await update.message.reply_text(summary_message, parse_mode='Markdown')
            
            # Message 2: Copy-Paste Message
            copymessage = "*Copy-Paste the following message to your Deliveryman!*"
            await update.message.reply_text(copymessage, parse_mode='Markdown')
            
            # Message 3: Verification Instruction
            # \nPlease leave my order at the front desk and verify the last 4 digits of the order-id *{verification_id}* with the staff there
            instruction_message = (f"បងជួយយកកញ្ចប់អាហារខ្ញុំដាក់តុផ្ដល់ព័ត៌មាននិងបញ្ជាក់លេខកូដ4ខ្ទង់*{verification_id}* ប្រាប់បុគ្កលិកផងបង")
            await update.message.reply_text(instruction_message, parse_mode='Markdown')
            
            context.user_data['awaiting_gia_floor'] = False
        else:
            await update.message.reply_text("Invalid floor number. Please enter a number between 1 and 43.")
    
    else:
        await update.message.reply_text('Please use /start or /help to begin.')

async def front_desk(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Your order has just arrived at the front desk. We'll be delivering it to you shortly!"
    )

async def elevator_arrive(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "We're on our way up in the elevator to deliver your food. Thank you for your patience!"
    )
async def almost_floor(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "We've just completed a delivery on the floor below yours. We'll be with you very soon!"
    )
async def floor_arrive(update: Update, context: CallbackContext):
    verification_id = context.user_data.get('verification_id', 'unknown')  # Default to 'unknown' if not set
    await update.message.reply_text(
        f"We've arrived at your floor!\nPlease look for the bag with this verification ID {verification_id}. \n\nClick /accept if you've received it, or /decline if you haven't."
    )

async def handle_response(update: Update, context: CallbackContext):
    user_response = update.message.text

    if user_response == "/accept":
        await update.message.reply_text("Thank you for confirming the receipt of your order!")
    elif user_response == "/decline":
        await update.message.reply_text(
            "We're sorry to hear that. Please provide details about the issue, and we'll address it promptly."
        )

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('floorExpress', floor_express))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Command handlers for additional actions
    application.add_handler(CommandHandler('check_in', front_desk))
    application.add_handler(CommandHandler('otw', elevator_arrive))
    application.add_handler(CommandHandler('almost', almost_floor))
    application.add_handler(CommandHandler('drop', floor_arrive))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_response))

    application.run_polling()

if __name__ == '__main__':
    main()
