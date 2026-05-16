import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
from pymongo import MongoClient

# ================= CONFIG =================

BOT_TOKEN=os.getenv("BOT_TOKEN")

MONGO_URI="mongodb+srv://heliumrobin:crickzone@cluster0.gdlyiz9.mongodb.net/?appName=Cluster0"

CHANNEL_USERNAME="@pczofficial"
GROUP_USERNAME="@Panchayatgamezone"

CHANNEL_ID=-1003773332497
# registration data forwarded here

OWNER_IDS=[8346716845,7807828008]

# ==========================================

client=MongoClient(MONGO_URI)
db=client["cricket_bot"]

users=db.players


# ========= START =========

async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):

    keyboard=[
        [
            InlineKeyboardButton(
                "Join Channel",
                url=f"https://t.me/{CHANNEL_USERNAME.replace('@','')}"
            )
        ],
        [
            InlineKeyboardButton(
                "Join Group",
                url=f"https://t.me/{GROUP_USERNAME.replace('@','')}"
            )
        ],
        [
            InlineKeyboardButton(
                "I Have Joined ✅",
                callback_data="check_join"
            )
        ]
    ]

    await update.message.reply_text(
        "🏏 Welcome!\n\nJoin both below then click I Have Joined.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ========= CHECK JOIN =========

async def check_join(update:Update,context):

    query=update.callback_query
    user=query.from_user

    await query.answer()

    try:

        c=await context.bot.get_chat_member(
            CHANNEL_USERNAME,
            user.id
        )

        g=await context.bot.get_chat_member(
            GROUP_USERNAME,
            user.id
        )

        channel_ok=c.status in [
            "member",
            "administrator",
            "creator"
        ]

        group_ok=g.status in [
            "member",
            "administrator",
            "creator"
        ]

        if not channel_ok or not group_ok:

            return await query.message.reply_text(
                "❌ Join both channel and group first."
            )

    except:

        return await query.message.reply_text(
            "❌ Join both channel and group first."
        )


    keyboard=[
        [
            InlineKeyboardButton(
                "Register Me",
                callback_data="register"
            )
        ]
    ]

    await query.message.reply_text(
        "🏏 Register yourself as a player and be able to participate in auction as a player :) \n\n"
        " Prizes for both 1st ranked and runner up team and best batter .. blah blah blah awaits \nvc and ret. don't register \n\n"
        "Click below:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ========= REGISTER =========

async def register(update:Update,context):

    query=update.callback_query
    user=query.from_user

    await query.answer()

    already=users.find_one(
        {
            "user_id":user.id
        }
    )

    if already:

        return await query.message.reply_text(
            "✅ You already registered. Check your registration at @pczofficial"
        )

    data={

        "user_id":user.id,
        "first_name":user.first_name,
        "username":user.username
    }

    users.insert_one(data)

    text=(
        "🏏 NEW PLAYER REGISTERED\n\n"
        f"👤 Name: {user.first_name}\n"
        f"🔗 Username: @{user.username}\n"
        f"🆔 ID: {user.id}"
    )

    await context.bot.send_message(
        CHANNEL_ID,
        text
    )

    await query.message.reply_text(
        "✅ Registration successful. Check your registration at @pczofficial , and stay tuned :))"
    )


# ========= SHOW LIST =========

async def showlist(update:Update,context):

    if update.effective_user.id not in OWNER_IDS:
        return

    all_users=list(
        users.find()
    )

    if not all_users:

        return await update.message.reply_text(
            "No players."
        )

    chunk_size=10

    for i in range(
        0,
        len(all_users),
        chunk_size
    ):

        chunk=all_users[i:i+chunk_size]

        msg=f"🏏 Player List {i//10+1}\n\n"

        for n,user in enumerate(
            chunk,
            start=i+1
        ):

            uname=user.get(
                "username"
            )

            if uname:
                uname="@"+uname
            else:
                uname="No username"

            msg+=(
                f"{n}. "
                f"{user['first_name']} | "
                f"{uname}\n"
                f"ID: {user['user_id']}\n\n"
            )

        await update.message.reply_text(msg)



# ========= MAIN =========

app=Application.builder().token(
    BOT_TOKEN
).build()

app.add_handler(
    CommandHandler(
        "start",
        start
    )
)

app.add_handler(
    CommandHandler(
        "showlist",
        showlist
    )
)

app.add_handler(
    CallbackQueryHandler(
        check_join,
        pattern="check_join"
    )
)

app.add_handler(
    CallbackQueryHandler(
        register,
        pattern="register"
    )
)

print("Bot started...")

app.run_polling()
