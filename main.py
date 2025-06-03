import logging
from telegram import Update, ForceReply
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import openai
import config

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

openai.api_key = config.OPENAI_API_KEY

SUBSCRIBERS = set()  # کاربرانی که اشتراک دارند

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_html(
        rf"سلام {user.mention_html()}! به Nuvana خوش آمدید. لطفا برای استفاده اشتراک بگیرید.",
        reply_markup=ForceReply(selective=True),
    )

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id in SUBSCRIBERS:
        await update.message.reply_text("شما قبلا اشتراک دارید.")
    else:
        await update.message.reply_text(
            "درخواست اشتراک شما ثبت شد. لطفا منتظر تایید مدیر بمانید."
        )
        # ارسال پیام به مدیر
        for admin_id in config.ADMIN_USER_IDS:
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"کاربر @{user.username} درخواست اشتراک داده است. برای تایید /approve {user.id} را بزنید."
            )

async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in config.ADMIN_USER_IDS:
        await update.message.reply_text("شما اجازه این کار را ندارید.")
        return
    if len(context.args) != 1:
        await update.message.reply_text("لطفا آیدی کاربر را وارد کنید.")
        return
    try:
        user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("آیدی نامعتبر است.")
        return
    SUBSCRIBERS.add(user_id)
    await update.message.reply_text(f"کاربر با آیدی {user_id} تایید و اشتراک فعال شد.")
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text="اشتراک شما تایید شد! حالا می‌توانید سوالات خود را بپرسید."
        )
    except:
        pass

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in SUBSCRIBERS:
        await update.message.reply_text("لطفا ابتدا اشتراک خود را فعال کنید.")
        return
    question = update.message.text

    # درخواست به OpenAI GPT
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional psychologist."},
                {"role": "user", "content": question}
            ],
            max_tokens=500,
            temperature=0.7,
        )
        answer = response['choices'][0]['message']['content']
    except Exception as e:
        answer = "متاسفانه مشکلی پیش آمد. لطفا بعدا تلاش کنید."

    await update.message.reply_text(answer)

def main():
    app = ApplicationBuilder().token(config.TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("subscribe", subscribe))
    app.add_handler(CommandHandler("approve", approve))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
