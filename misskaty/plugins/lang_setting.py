from functools import partial
from typing import Union

from pyrogram import Client, filters
from pyrogram.enums import ChatType
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from misskaty.vars import COMMAND_HANDLER
from misskaty import app
from database.locale_db import set_db_lang
from ..core.decorator.permissions import require_admin
from ..helper.localization import (
    default_language,
    get_locale_string,
    langdict,
    use_chat_lang,
)


def gen_langs_kb():
    langs = list(langdict)
    kb = []
    while langs:
        lang = langdict[langs[0]]["main"]
        a = [
            InlineKeyboardButton(
                f"{lang['language_flag']} {lang['language_name']}",
                callback_data=f"set_lang {langs[0]}",
            )
        ]

        langs.pop(0)
        if langs:
            lang = langdict[langs[0]]["main"]
            a.append(
                InlineKeyboardButton(
                    f"{lang['language_flag']} {lang['language_name']}",
                    callback_data=f"set_lang {langs[0]}",
                )
            )

            langs.pop(0)
        kb.append(a)
    return kb


@app.on_callback_query(filters.regex("^chlang$"))
@app.on_message(filters.command(["setchatlang", "setlang"], COMMAND_HANDLER))
@require_admin(allow_in_private=True)
@use_chat_lang()
async def chlang(c: Client, m: Union[CallbackQuery, Message], strings):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            *gen_langs_kb(),
            [InlineKeyboardButton(strings("back_btn", context="general"), callback_data="start_back")],
        ]
    )

    if isinstance(m, CallbackQuery):
        msg = m.message
        sender = msg.edit_text
    else:
        msg = m
        sender = msg.reply_text

    res = strings("language_changer_private") if msg.chat.type == ChatType.PRIVATE else strings("language_changer_chat")

    await sender(res, reply_markup=keyboard)


@app.on_callback_query(filters.regex("^set_lang "))
@require_admin(allow_in_private=True)
@use_chat_lang()
async def set_chat_lang(c: Client, m: CallbackQuery, strings):
    lang = m.data.split()[1]
    await set_db_lang(m.message.chat.id, m.message.chat.type, lang)

    strings = partial(
        get_locale_string,
        langdict[lang].get("lang_setting", langdict[default_language]["lang_setting"]),
        lang,
        "lang_setting",
    )

    if m.message.chat.type == ChatType.PRIVATE:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        strings("back_btn", context="general"),
                        callback_data="start_back",
                    )
                ]
            ]
        )
    else:
        keyboard = None
    await m.message.edit_text(strings("language_changed_successfully"), reply_markup=keyboard)
