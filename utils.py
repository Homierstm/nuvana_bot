from telegram import Update
from telegram.ext import ContextTypes

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    return update.effective_user.id in context.bot_data.get("admin_user_ids", [])

def lang_code(text: str) -> str:
    # فرض ساده، مثلا از کاربر زبان رو دریافت کنیم یا بعدا گسترش بدیم
    return "fa"  # به طور پیش‌فرض فارسی
