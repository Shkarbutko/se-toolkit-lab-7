try:
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
except ImportError:
    InlineKeyboardButton = None
    InlineKeyboardMarkup = None


def build_main_keyboard():
    if InlineKeyboardButton is None:
        return None

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Labs", callback_data="what labs are available"),
            InlineKeyboardButton("Lowest pass rate", callback_data="which lab has the lowest pass rate"),
        ],
        [
            InlineKeyboardButton("Top learners", callback_data="who are the top 5 students in lab 4"),
            InlineKeyboardButton("Groups", callback_data="which group is doing best in lab 3"),
        ],
    ])
