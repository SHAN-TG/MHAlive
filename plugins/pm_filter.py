import asyncio, re, ast
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from Script import script
from info import ADMINS, AUTH_CHANNEL, CUSTOM_FILE_CAPTION, SPELL_CHECK_REPLY
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from utils import get_size, is_subscribed
from database.users_chats_db import db
from database.ia_filterdb import Media, get_file_details, get_search_results
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

BUTTONS = {}
PM_BUTTONS = {}

@Client.on_message(filters.group & filters.text & filters.incoming)
async def give_filter(client, message):
    await auto_filter(client, message)

@Client.on_message(filters.private & filters.text & filters.incoming)
async def pm_give_filter(client, message):
    await pm_auto_filter(client, message)


@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer("മറ്റുള്ളവർ search ലിസ്റ്റിൽ കൈ ഇടാതെ സ്വന്തമായ്  search ചെയ്തിട്ട്  അതിൽ  നോക്കുക. Don't try to click on others searched file.Search it yourself first, like others🙂", show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = BUTTONS.get(key)
    if not search:
        await query.answer("നിങ്ങൾ എന്റെ പഴയ സന്ദേശങ്ങളിലൊന്നാണ് ഉപയോഗിക്കുന്നത്, ദയവായി വീണ്ടും request അയയ്‌ക്കുക 🙂 You are using one of my old messages, please send the request again.", show_alert=True)
        return

    files, n_offset, total = await get_search_results(search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    btn = [[InlineKeyboardButton(text=f"{get_size(file.file_size)} {file.file_name}", callback_data=f'file#{file.file_id}'),] for file in files]
    
    if 0 < offset <= 10:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 10
    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"),
             InlineKeyboardButton(f"⌧ Tʜᴇ Eɴᴅ {round(int(offset) / 10) + 1} / {round(total / 10)}",
                                  callback_data="pages")]
        )
    elif off_set is None:
        btn.append(
            [InlineKeyboardButton(f"🎭 {round(int(offset) / 10) + 1} / {round(total / 10)}", callback_data="pages"),
             InlineKeyboardButton("ɴᴇxᴛ", callback_data=f"next_{req}_{key}_{n_offset}")])
    else:
        btn.append(
            [
                InlineKeyboardButton("ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}"),
                InlineKeyboardButton(f"🎭 {round(int(offset) / 10) + 1} / {round(total / 10)}", callback_data="pages"),
                InlineKeyboardButton("ɴᴇxᴛ", callback_data=f"next_{req}_{key}_{n_offset}")
            ],
        )
    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass
    await query.answer()



@Client.on_callback_query(filters.regex(r"^pmnext"))
async def pm_next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer("മറ്റുള്ളവർ search ലിസ്റ്റിൽ കൈ ഇടാതെ സ്വന്തമായ്  search ചെയ്തിട്ട്  അതിൽ  നോക്കുക. Don't try to click on others searched file.Search it yourself first, like others🙂", show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = PM_BUTTONS.get(key)
    if not search:
        await query.answer("നിങ്ങൾ എന്റെ പഴയ സന്ദേശങ്ങളിലൊന്നാണ് ഉപയോഗിക്കുന്നത്, ദയവായി വീണ്ടും request അയയ്‌ക്കുക 🙂 You are using one of my old messages, please send the request again.", show_alert=True)
        return

    files, n_offset, total = await get_search_results(search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    btn = [[InlineKeyboardButton(text=f"{get_size(file.file_size)} {file.file_name}", callback_data=f'pmfile#{file.file_id}'),] for file in files]
    
    if 0 < offset <= 10:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 10
    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data=f"pmnext_{req}_{key}_{off_set}"),
             InlineKeyboardButton(f"⌧ Tʜᴇ Eɴᴅ {round(int(offset) / 10) + 1} / {round(total / 10)}",
                                  callback_data="pages")]
        )
    elif off_set is None:
        btn.append(
            [InlineKeyboardButton(f"🎭 {round(int(offset) / 10) + 1} / {round(total / 10)}", callback_data="pages"),
             InlineKeyboardButton("ɴᴇxᴛ", callback_data=f"pmnext_{req}_{key}_{n_offset}")])
    else:
        btn.append(
            [
                InlineKeyboardButton("ʙᴀᴄᴋ", callback_data=f"pmnext_{req}_{key}_{off_set}"),
                InlineKeyboardButton(f"🎭 {round(int(offset) / 10) + 1} / {round(total / 10)}", callback_data="pages"),
                InlineKeyboardButton("ɴᴇxᴛ", callback_data=f"pmnext_{req}_{key}_{n_offset}")
            ],
        )
    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass
    await query.answer()


@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        await query.message.delete()
   
    if query.data.startswith("file"):
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')                   
        await query.answer(url=f"https://t.me/{client.username}?start={ident}_{file_id}")
                
    if query.data.startswith("pmfile"):
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)       
        try:
            f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title, file_size='' if size is None else size)
        except:                                             
            f_caption = f"{title}"                                               
        try:
            if AUTH_CHANNEL and not await is_subscribed(client, query):
                await query.answer(url=f"https://t.me/{client.username}?start={ident}_{file_id}")
                return            
            else:
                await client.send_cached_media(
                    chat_id=query.from_user.id,
                    file_id=file_id,
                    caption=f_caption                    
                )                       
        except Exception as err:
            await query.answer(f"X0X ERROR: {err}", show_alter=True)
            await query.answer(url=f"https://t.me/{client.username}?start={ident}_{file_id}")

    elif query.data.startswith("checksub"):
        if AUTH_CHANNEL and not await is_subscribed(client, query):
            await query.answer("I Like Your Smartness, But Don't Be Oversmart 😒 SUBSCRIBE ചെയ്ത ശേഷം ഫയൽ എടുക്കുക", show_alert=True)
            return
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)        
        try:
            f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title, file_size='' if size is None else size)
        except:                                             
            f_caption = f"{title}"
                                                       
        await client.send_cached_media(
            chat_id=query.from_user.id,
            file_id=file_id,
            caption=f_caption,            
        )
    elif query.data == "pages":
        await query.answer("കൗതുകം അല്പം കൂടുതലാണല്ലേ 🤨", show_alert=True)
    elif query.data == "start":
        buttons = [[
            InlineKeyboardButton('➕ ADD ME TO YOUR GROUPS  ➕', url=f'http://t.me/{client.username}?startgroup=true')
            ],[
            InlineKeyboardButton('HELP', callback_data='help'),
            InlineKeyboardButton('ABOUT', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.START_TXT.format(query.from_user.mention, client.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        await query.answer('°°°°')
    elif query.data == "help":
        buttons = [[            
            InlineKeyboardButton('🏠 HOME', callback_data='start'),
            InlineKeyboardButton('🔮 STATUS', callback_data='stats')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "about":
        buttons = [[
            InlineKeyboardButton('🏠 HOME', callback_data='start'),
            InlineKeyboardButton('🔐 CLOSE', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ABOUT_TXT.format(client.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.SOURCE_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        ) 
    elif query.data == "stats":
        buttons = [[
            InlineKeyboardButton('👩‍🦯 BACK', callback_data='help'),
            InlineKeyboardButton('♻️', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = "not found"
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "rfrsh":
        await query.answer("Fetching MongoDb DataBase")
        buttons = [[
            InlineKeyboardButton('👩‍🦯 BACK', callback_data='help'),
            InlineKeyboardButton('♻️', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = "not found"
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    

async def auto_filter(client, msg):
    message = msg
    if message.text.startswith("/"): return  # ignore commands
    if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
        return
    if 2 < len(message.text) < 100:   
        search = message.text
        files, offset, total_results = await get_search_results(search.lower(), offset=0, filter=True)
        if not files:
            if SPELL_CHECK_REPLY:
                return await msg.reply_text(text="I couldn't find any movie in that name please check your spelling in Google",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💬 GOOGLE SEARCH", url=f"https://www.google.com/search?q={search}")]]))
            else:
                return     
    else:
        return         
    btn = [[
        InlineKeyboardButton(text=f"{get_size(file.file_size)} {file.file_name}",
            callback_data=f'file#{file.file_id}')
        ] for file in files ]               
                                   
    if offset != "":
        key = f"{message.chat.id}-{message.id}"
        BUTTONS[key] = search
        req = message.from_user.id if message.from_user else 0
        btn.append([InlineKeyboardButton(text=f"🎭 1/{round(int(total_results) / 10)}", callback_data="pages"), InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ⏩", callback_data=f"next_{req}_{key}_{offset}")])
    else:
        btn.append( [InlineKeyboardButton(text="🎭 1/1", callback_data="pages")])    
    cap = f"Here is what i found for your query {search}"
    try:
        await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(btn))
    except Exception as e:
        logger.exception(e)
        await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(btn))
    


async def pm_auto_filter(client, msg):
    message = msg
    if message.text.startswith("/"): return  # ignore commands
    if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
        return
    if 2 < len(message.text) < 100:   
        search = message.text
        files, offset, total_results = await get_search_results(search.lower(), offset=0, filter=True)
        if not files:
            if SPELL_CHECK_REPLY:
                return await msg.reply_text(text="I couldn't find any movie in that name please check your spelling in Google",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💬 GOOGLE SEARCH", url=f"https://www.google.com/search?q={search}")]]))
            else:
                return     
    else:
        return         
    btn = [[
        InlineKeyboardButton(text=f"{get_size(file.file_size)} {file.file_name}",
            callback_data=f'pmfile#{file.file_id}')
        ] for file in files ]               
                                   
    if offset != "":
        key = f"{message.chat.id}-{message.id}"
        PM_BUTTONS[key] = search
        req = message.from_user.id if message.from_user else 0
        btn.append([InlineKeyboardButton(text=f"🎭 1/{round(int(total_results) / 10)}", callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ", callback_data=f"pmnext_{req}_{key}_{offset}")])
    else:
        btn.append( [InlineKeyboardButton(text="🎭 1/1", callback_data="pages")])    
    cap = f"Here is what i found for your query {search}"
    try:
        await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(btn))
    except Exception as e:
        logger.exception(e)
        await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(btn))
    









