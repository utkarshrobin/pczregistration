import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler
)

from pymongo import MongoClient


# ================= CONFIG =================

BOT_TOKEN=os.getenv("BOT_TOKEN")

MONGO_URI="mongodb+srv://heliumrobin:crickzone@cluster0.gdlyiz9.mongodb.net/?appName=Cluster0"

CHANNEL_USERNAME="@pczofficial"
GROUP_USERNAME="@panchayatgamezone"

CHANNEL_ID=-1003773332497

OWNER_IDS=[8346716845,7807828008]

# ==========================================


client=MongoClient(MONGO_URI)

db=client["cricket_bot"]

users=db.players
joined=db.joined
banned=db.banned
logs=db.logs


# ========= START =========

async def start(update:Update,context):

    user=update.effective_user

    already_joined=joined.find_one(
        {"user_id":user.id}
    )

    if already_joined:

        already_registered=users.find_one(
            {"user_id":user.id}
        )

        if already_registered:

            return await update.message.reply_text(
                "🏏✨ You are already registered!\n\n"
                "📢 Check your registration at\n"
                "@pczofficial"
            )

        keyboard=[
            [
                InlineKeyboardButton(
                    "🔥 Register Me",
                    callback_data="register"
                )
            ]
        ]

        return await update.message.reply_text(
            "🏏 PLAYER ENTRY\n\n"
            "⚠️ VC + RET don't register\n\n"
            "👇 Ready?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


    keyboard=[

        [
            InlineKeyboardButton(
                "📢 Join Channel",
                url=f"https://t.me/{CHANNEL_USERNAME.replace('@','')}"
            )
        ],

        [
            InlineKeyboardButton(
                "💬 Join Group",
                url=f"https://t.me/{GROUP_USERNAME.replace('@','')}"
            )
        ],

        [
            InlineKeyboardButton(
                "✅ I Have Joined",
                callback_data="check_join"
            )
        ]
    ]

    await update.message.reply_text(
        "🏏 Welcome Champion!\n\n"
        "⚡ Join both below first\n"
        "👇 Then tap button",
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
                "❌ Join both first 😶"
            )

    except:

        return await query.message.reply_text(
            "❌ Join both first 😶"
        )


    joined.update_one(
        {
            "user_id":user.id
        },
        {
            "$set":{
                "user_id":user.id
            }
        },
        upsert=True
    )


    keyboard=[
        [
            InlineKeyboardButton(
                "🔥 Register Me",
                callback_data="register"
            )
        ]
    ]

    await query.message.reply_text(

        "🏆 A mega tournament is going on by Panchayat Zone "
        "@panchayatgamezone 🔥\n\n"

        "🥇 1st Team Prize: ₹2000\n"
        "🥈 Runner Up Prize: ₹1000\n"
        "🏏 Best Batter Award\n"
        "🎯 Best Bowler Award\n"
        "🎁 And much more awaits!\n\n"

        " VC aur CAP don't register\n\n"

        "👇 Register below now",

        reply_markup=InlineKeyboardMarkup(
            keyboard
        )
    )


# ========= REGISTER =========

async def register(update:Update,context):

    query=update.callback_query
    user=query.from_user

    await query.answer()

    blocked=banned.find_one(
        {
            "user_id":user.id
        }
    )

    if blocked:

        return await query.message.reply_text(
            "🚫 Registration blocked"
        )


    already=users.find_one(
        {
            "user_id":user.id
        }
    )

    if already:

        return await query.message.reply_text(
            "✅ You have already registered!\n\n"
            "📢 Check your registration here:\n"
            "@pczofficial"
        )


    data={

        "user_id":user.id,
        "first_name":user.first_name,
        "username":user.username
    }

    users.insert_one(data)


    username=(
        "@"+user.username
        if user.username
        else "No username"
    )


    text=(

        "🎉 NEW PLAYER REGISTRATION \n\n"

        f"👤Name: {user.first_name}\n"
        f"🔗Username: {username}\n"
        f"🆔Id num: {user.id}"

    )


    sent=await context.bot.send_message(
        CHANNEL_ID,
        text
    )


    logs.insert_one({

        "user_id":user.id,
        "message_id":sent.message_id

    })


    await query.message.reply_text(

        "🎉 Registration Successful!\n\n"
        "🏏 Welcome Champion\n\n"
        "📢 View your registration at:\n"
        "@pczofficial"

    )


# ========= PLAYER LIST =========

async def showlist(update:Update,context):

    if update.effective_user.id not in OWNER_IDS:
        return


    all_users=list(
        users.find()
    )


    if not all_users:

        return await update.message.reply_text(
            "😶 No players"
        )


    chunk_size=10


    for i in range(
        0,
        len(all_users),
        chunk_size
    ):


        chunk=all_users[i:i+chunk_size]


        msg=f"🏏 PLAYER LIST {i//10+1}\n\n"


        for n,user in enumerate(
            chunk,
            start=1
        ):


            uname=user.get(
                "username"
            )

            if uname:
                uname="@"+uname
            else:
                uname="No username"


            msg+=(

                f"{n}. {user['first_name']}\n"
                f"🔗 {uname}\n"
                f"🆔 {user['user_id']}\n\n"

            )


        await update.message.reply_text(
            msg
        )


# ========= DELETE =========

async def delete(update:Update,context):

    if update.effective_user.id not in OWNER_IDS:
        return


    try:

        list_no=int(
            context.args[0]
        )

        player_no=int(
            context.args[1]
        )

    except:

        return await update.message.reply_text(
            "Use:\n/delete 1 1"
        )


    all_users=list(
        users.find()
    )


    index=((list_no-1)*10)+(player_no-1)


    if index>=len(all_users):

        return await update.message.reply_text(
            "❌ Invalid player"
        )


    user=all_users[index]


    users.delete_one(
        {
            "user_id":user["user_id"]
        }
    )


    banned.insert_one(
        {
            "user_id":user["user_id"]
        }
    )


    log=logs.find_one(
        {
            "user_id":user["user_id"]
        }
    )


    try:

        if log:

            await context.bot.delete_message(
                CHANNEL_ID,
                log["message_id"]
            )

    except:
        pass


    await update.message.reply_text(
        f"🗑 Deleted {user['first_name']}\n"
        "🚫 User banned from registration"
    )


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
    CommandHandler(
        "delete",
        delete
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

print("Bot Started 🔥")

app.run_polling()
