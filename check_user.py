TOKEN = "7429990932:AAEuaRrwIYJex23WS6JptodKUNoRQ-uI9Mw"
from telegram import Bot, Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ContextTypes,ConversationHandler, ChatMemberHandler

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
import re
from auto_delete_utils import new_member, member_left
# Database setup using SQLite
DATABASE_URL = "sqlite:///./database.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)  # Chat ID
    username = Column(String)
    joined_at = Column(String, nullable=True)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=False)
    chat_id = Column(Integer, nullable=False)
    telegram_name = Column(String, nullable=False)  # LN + FN
    username = Column(String, nullable=True)  # Optional: Some accounts don't have usernames
    order_id = Column(String, index=True, nullable=False)  # foodpanda order-ID
    verification_id = Column(String, nullable=False)  # Extracted 4 digits
    phone_number = Column(String, nullable=False)
    gia_floor = Column(String, nullable=False)  # Floor number
    status = Column(String, nullable=False)  # Status: Payment Confirmed, Arrived at GIA, Picked up by Gatherer, Pending Batch, Submitted Batch, Started Delivery, Delivered
    batch_number = Column(String, nullable=True)  # Only display Batch Number when status is changed to "Submitted Batch"

class Batch(Base):
    __tablename__ = "batch"
    id = Column(Integer, primary_key=True, index=True)
    verification_id = Column(String, ForeignKey("orders.verification_id"))
    gia_floor = Column(String, ForeignKey("orders.gia_floor"))
    status = Column(String, ForeignKey("orders.status")) 
    batch_number = Column(String, ForeignKey("orders.batch_number"))

Base.metadata.create_all(bind=engine)


''''''
def get_session():
    """
    Utility function to create and return a new SQLAlchemy session.
    
    Returns:
        session (Session): A new session object.
    """
    return SessionLocal()
session = SessionLocal()
# Function to add and delete users from the database
async def handle_message_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_member_update = update.chat_member
    if chat_member_update.new_chat_member.status == 'member':
        user = chat_member_update.new_chat_member.user
        print(f"User {user.full_name} joined the group")
        
        user_id = user.id
        username = user.username

        await save_user_info(user_id, username)
        print(f"New member joined: (@{username})")
        # await context.bot.send_message(
        #     chat_id=update.effective_chat.id,
        #     text=f"Welcome {user.full_name} to the group!"
        # )
    elif chat_member_update.old_chat_member.status == 'member':
            user = chat_member_update.old_chat_member.user
            print(f"User {user.full_name} left the group")
            
            user_id = user.id

            await remove_user(user_id)
            print(f"User left: {user.first_name} {user.last_name} (@{user.username})")
            # await context.bot.send_message(
            #     chat_id=update.effective_chat.id,
            #     text=f"Goodbye {user.full_name}!"
            # )
async def remove_user(user_id):
    user = session.query(User).filter_by(user_id=user_id).first()
    if user:
        session.delete(user)
        session.commit()
    
async def save_user_info(user_id, username):
    user = User(user_id=user_id, username=username)
    print("user")
    session.merge(user) 
    session.commit()


def is_user_exists(user_id, username):
    session = get_session()  
    try:
        print(user_id)
        user = session.query(User).filter_by(user_id=user_id).first()
        if not user:
            user = session.query(User).filter_by(username=username).first()
        return user is not None  
    except SQLAlchemyError as e:
        # Handle exceptions (e.g., log errors)
        print(f"An error occurred: {e}")
        return False
    finally:
        session.close()  

def is_order_exists(verification_id):
    # session = get_session()  
    db = SessionLocal()
    try:
        print("order id: ",verification_id)
        order = db.query(Order).filter_by(verification_id=verification_id)
        return order is not None  
    except SQLAlchemyError as e:
        # Handle exceptions (e.g., log errors)
        print(f"An error occurred: {e}")
        return False
    finally:
        db.close()  
''''''
def extract_last_4_digits(order_id):
    if validate_order_id(order_id):
        return order_id[-4:]
    else:
        return "Invalid format"

def validate_order_id(order_id):
    pattern = r'^[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}$'
    return re.match(pattern, order_id) is not None
