from main import *
from main import (
    button,
    accept_order,
    decline_order,
    handle_pickup_confirmation,
    message_handler,
    # screenshot_handler,
    # skip_screenshot,
)

# from screenshot import handle_screenshot, handle_skip_screenshot
from check_user import handle_message_group


# def main():
#     application = Application.builder().token(TOKEN).build()

#     application.add_handler(CommandHandler("start", start))
#     application.add_handler(
#         MessageHandler(filters.TEXT & filters.Regex("Use floorExpress|Cancel"), button)
#     )
#     application.add_handler(
#         MessageHandler(
#             filters.TEXT & filters.Regex("Pickup|View Pending Batch|Cancel"), button
#         )
#     )
#     application.add_handler(
#         MessageHandler(
#             filters.TEXT & ~filters.Regex("View Submitted Batch|Cancel"), button
#         )
#     )
#     application.add_handler(
#         MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)
#     )

#     application.add_handler(
#         CallbackQueryHandler(
#             callback=handle_pickup_confirmation, pattern="^confirm_pickup$"
#         )
#     )
#     application.add_handler(
#         CallbackQueryHandler(callback=submit_batch, pattern="^submit_batch$")
#     )
#     # application.add_handler(CallbackQueryHandler(callback=submit_batch, pattern='^submit_batch$'))

#     # application.add_handler(MessageHandler(filters.TEXT & ~filters.Regex("Start Delivery|Cancel"), start_delivery))
#     # application.add_handler(MessageHandler(filters.TEXT & ~filters.Regex("End Delivery"), end_delivery))
#     # application.add_handler(
#     #     ChatMemberHandler(handle_message_group, ChatMemberHandler.CHAT_MEMBER)
#     # )

#     # application.add_handler(CallbackQueryHandler(callback=cancel_button, pattern='^cancel$'))
#     # application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member))
#     # application.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, member_left))
#     # application.add_handler(MessageHandler(filters.PHOTO, screenshot_handler))
#     # application.add_handler(CallbackQueryHandler(skip_screenshot, pattern="^skip$"))
#     # application.run_polling(allowed_updates=Update.ALL_TYPES, timeout=60)


def main():
    application = Application.builder().token(TOKEN).build()

    # Add more specific handlers first
    application.add_handler(CommandHandler("start", start))

    # Specific text handlers for button interactions
    application.add_handler(
        MessageHandler(filters.TEXT & filters.Regex("Use floorExpress|Cancel"), button)
    )
    application.add_handler(
        MessageHandler(
            filters.TEXT
            & filters.Regex("Pickup|View Pending Batch|Submit Batch|Cancel"),
            button,
        )
    )
    application.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex("View Submitted Batch|View Delivering Batch"),
            button,
        )
    )

    # Callback query handlers
    application.add_handler(
        CallbackQueryHandler(
            callback=handle_pickup_confirmation, pattern="^confirm_pickup$"
        )
    )
    application.add_handler(
        CallbackQueryHandler(callback=submit_batch, pattern="^submit_batch$")
    )
    application.add_handler(
        CallbackQueryHandler(callback=start_delivery, pattern="^start_delivery$")
    )
    application.add_handler(
        CallbackQueryHandler(callback=end_delivery, pattern="^end_delivery$")
    )

    # Accept / Decline
    # application.add_handler(CallbackQueryHandler(callback=confirm_order, pattern='^confirm_order$'))
    # application.add_handler(CallbackQueryHandler(callback=decline_order, pattern='^decline_order$'))
    application.add_handler(
        CallbackQueryHandler(callback=accept_order, pattern="^confirm_")
    )
    application.add_handler(
        CallbackQueryHandler(callback=decline_order, pattern="^decline_")
    )

    application.add_handler(
        CallbackQueryHandler(callback=cancel_button, pattern="^cancel$")
    )
    # application.add_handler(CallbackQueryHandler(skip_screenshot, pattern="^skip$"))

    

    # Screenshot handler
    # application.add_handler(MessageHandler(filters.PHOTO, screenshot_handler))

    # General message handler, place this last
    application.add_handler(
        MessageHandler(
            filters.TEXT
            & ~filters.Regex(
                "Use floorExpress|Cancel|Pickup|View Pending Batch|Submit Batch|View Submitted Batch|Start Delivery|End Delivery"
            ),
            message_handler,
        )
    )
    # Message handler for status updates and new members
    application.add_handler(
        ChatMemberHandler(handle_message_group, ChatMemberHandler.CHAT_MEMBER)
    )
    application.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member)
    )
    application.add_handler(
        MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, member_left)
    )

    application.run_polling(allowed_updates=Update.ALL_TYPES, timeout=60)


if __name__ == "__main__":
    main()


