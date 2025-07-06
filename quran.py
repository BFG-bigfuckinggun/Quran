import os
import asyncio
import threading
from aiohttp import web
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = os.environ.get("TOKEN")
QURAN_PAGES_DIR = os.path.join(os.path.dirname(__file__), "pages")
PORT = int(os.environ.get("PORT", 10000))

# —— Health‐check endpoint
async def health(request):
    return web.Response(text="OK")

async def start_health_server():
    app = web.Application()
    app.add_routes([web.get("/", health)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

def spawn_health_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_health_server())
    loop.run_forever()

# —— Telegram handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *تقدمة السيد حيدر الموسوي*\n"
        "بسم الله الرحمن الرحيم، وبه نستعين.\n"
        "🌙 أرسل رقم الصفحة (1–620) أو اكتب اسم حكم مثل:\n"
        "`ن الإظهار`، `ن الإدغام`، `م الإخفاء`، `مد طبيعي`، `بسملة`...",
        parse_mode="Markdown"
    )
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()

    if text == "السلام عليكم":
        return await update.message.reply_text("وعليكم السلام ورحمة الله")

    if "صلوات" in text and "محمد" in text:
        return await update.message.reply_text("اللهم صَلِّ عَلَى مُحَمَّدٍ وَآلِ مُحَمَّدٍ")

    if text.isdigit():
        n = int(text)
        if 1 <= n <= 620:
            path = os.path.join(QURAN_PAGES_DIR, f"{n}.jpg")
            if os.path.exists(path):
                with open(path, "rb") as photo:
                    return await update.message.reply_photo(photo=photo)

    # أحكام النون الساكنة والتنوين
    if text == "ن الإظهار":
        return await update.message.reply_text(
            "🔹 *الإظهار الحلقي (في النون الساكنة والتنوين):*\n"
            "هو نطق النون الساكنة أو التنوين بوضوح دون غنة، إذا جاء بعدها أحد حروف الحلق.\n"
            "🧠 الحروف: (ء، هـ، ع، ح، غ، خ)\n"
            "🧪 *أمثلة:*\n"
            "• ﴿مِنْ هَادٍ﴾\n"
            "• ﴿إِنْ هُوَ﴾\n"
            "• ﴿مِنْ عِلْمٍ﴾",
            parse_mode="Markdown"
        )

    if text == "ن الإدغام":
        return await update.message.reply_text(
            "🔄 *الإدغام (في النون الساكنة والتنوين):*\n"
            "هو إدخال النون أو التنوين في الحرف التالي، بحيث يصيران حرفًا واحدًا مشددًا.\n"
            "🧠 الحروف: (ي، ر، م، ل، و، ن) — مجموعة في كلمة *يرملون*\n"
            "• إدغام بغنة: (ي، ن، م، و)\n"
            "• إدغام بغير غنة: (ر، ل)\n"
            "🧪 *أمثلة:*\n"
            "• ﴿مِنْ مَالٍ﴾ → مِمَّالٍ\n"
            "• ﴿مِنْ يَقُولُ﴾ → مِـيَّقُولُ\n"
            "• ﴿غَفُورٌ رَّحِيمٌ﴾ → غَفُورُرَّحِيمٌ",
            parse_mode="Markdown"
        )

    if text == "ن الإقلاب":
        return await update.message.reply_text(
            "🔁 *الإقلاب (في النون الساكنة والتنوين):*\n"
            "هو قلب النون الساكنة أو التنوين إلى ميم خفيفة إذا جاء بعدها حرف الباء.\n"
            "🧠 الحرف الوحيد: (ب)\n"
            "🧪 *أمثلة:*\n"
            "• ﴿سَمِيعٌ بَصِيرٌ﴾ → سَمِيعٌمْ بَصِيرٌ\n"
            "• ﴿مِنْ بَعْدِ﴾ → مِمْ بَعْدِ\n"
            "• ﴿إِنْ بُعِثَ﴾ → إِمْ بُعِثَ",
            parse_mode="Markdown"
        )

    if text == "ن الإخفاء":
        return await update.message.reply_text(
            "🎧 *الإخفاء الحقيقي (في النون الساكنة والتنوين):*\n"
            "هو نطق النون أو التنوين بصوت خافت بين الإظهار والإدغام مع غنة.\n"
            "🧠 الحروف: باقي الحروف (15 حرفًا) ما عدا حروف الإظهار والإدغام والإقلاب.\n"
            "🧪 *أمثلة:*\n"
            "• ﴿مِنْ صَلَاةٍ﴾\n"
            "• ﴿أَنْذَرْتَهُمْ﴾\n"
            "• ﴿يُنْفِقُونَ﴾",
            parse_mode="Markdown"
        )
    # أحكام الميم الساكنة
    if text == "م الإظهار":
        return await update.message.reply_text(
            "🔹 *الإظهار الشفوي (في الميم الساكنة):*\n"
            "هو نطق الميم الساكنة بوضوح إذا جاء بعدها أي حرف ما عدا الباء والميم.\n"
            "🧠 الحروف: جميع الحروف ما عدا (ب، م)\n"
            "🧪 *أمثلة:*\n"
            "• ﴿لَهُمْ أَجْرٌ﴾\n"
            "• ﴿فَهُمْ خَالِدُونَ﴾\n"
            "• ﴿عَلَيْهِمْ قِتَالٌ﴾",
            parse_mode="Markdown"
        )

    if text == "م الإدغام":
        return await update.message.reply_text(
            "🔄 *الإدغام الشفوي (في الميم الساكنة):*\n"
            "هو إدغام الميم الساكنة في ميم متحركة بعدها، بحيث تصيران ميمًا مشددة.\n"
            "🧠 الحرف الوحيد: (م)\n"
            "🧪 *أمثلة:*\n"
            "• ﴿كَمْ مِثْلِهِ﴾ → كَمْمِثْلِهِ\n"
            "• ﴿لَهُمْ مَغْفِرَةٌ﴾ → لَهُمْمَغْفِرَةٌ\n"
            "• ﴿فَهُمْ مُّهْتَدُونَ﴾ → فَهُمْمُهْتَدُونَ",
            parse_mode="Markdown"
        )

    if text == "م الإخفاء":
        return await update.message.reply_text(
            "🎧 *الإخفاء الشفوي (في الميم الساكنة):*\n"
            "هو نطق الميم الساكنة بصوت خافت مع غنة إذا جاء بعدها حرف الباء.\n"
            "🧠 الحرف الوحيد: (ب)\n"
            "🧪 *أمثلة:*\n"
            "• ﴿تَرْمِيهِمْ بِحِجَارَةٍ﴾\n"
            "• ﴿هُمْ بِرَبِّهِمْ﴾\n"
            "• ﴿عَلَيْهِمْ بُرُوقٌ﴾",
            parse_mode="Markdown"
        )

    # المدود
    if text == "مد طبيعي":
        return await update.message.reply_text(
            "📏 *المد الطبيعي (الأصلي):*\n"
            "هو الذي لا يتوقف على سبب، ويُمد بمقدار حركتين.\n"
            "🧠 حروفه: الألف، الواو، الياء الساكنة المسبوقة بحركة من جنسها.\n"
            "🧪 *أمثلة:*\n"
            "• ﴿قَالَ﴾\n"
            "• ﴿يَقُولُ﴾\n"
            "• ﴿فِيهِ﴾",
            parse_mode="Markdown"
        )

    if text == "مد لازم":
        return await update.message.reply_text(
            "📏 *المد اللازم:*\n"
            "هو الذي يأتي بعده حرف ساكن أصلي، ويُمد 6 حركات وجوبًا.\n"
            "🧠 أنواعه: كلمي مثقل، كلمي مخفف، حرفي مثقل، حرفي مخفف.\n"
            "🧪 *أمثلة:*\n"
            "• ﴿الضَّالِّينَ﴾\n"
            "• ﴿الْحَاقَّةُ﴾\n"
            "• ﴿الصَّاخَّةُ﴾",
            parse_mode="Markdown"
        )

    if text == "مد متصل":
        return await update.message.reply_text(
            "📏 *المد المتصل:*\n"
            "هو أن يأتي حرف المد وبعده همزة في نفس الكلمة، ويُمد 4–5 حركات.\n"
            "🧪 *أمثلة:*\n"
            "• ﴿جَاءَ﴾\n"
            "• ﴿سُوءَ﴾\n"
            "• ﴿بَرِيءٌ﴾",
            parse_mode="Markdown"
        )

    if text == "مد منفصل":
        return await update.message.reply_text(
            "📏 *المد المنفصل:*\n"
            "هو أن يأتي حرف المد في آخر الكلمة، والهمزة في أول الكلمة التالية.\n"
            "🧠 يُمد 4–5 حركات.\n"
            "🧪 *أمثلة:*\n"
            "• ﴿يَا أَيُّهَا﴾\n"
            "• ﴿إِنَّا أَنْزَلْنَاهُ﴾\n"
            "• ﴿قُولُوا آمَنَّا﴾",
            parse_mode="Markdown"
        )
    if text == "بسملة":
        return await update.message.reply_text(
            "🌸 *البسملة:*\n"
            "﴿بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ﴾\n\n"
            "📖 *تعريفها:*\n"
            "البسملة تُقال عند بدء التلاوة، وهي آية من سورة الفاتحة.\n\n"
            "📌 *أحكامها:*\n"
            "• تُقرأ في بداية كل سورة ما عدا التوبة.\n"
            "• إذا بدأت من وسط السورة، فالقارئ مُخيّر بين الإتيان بها أو تركها.\n"
            "• لا يجوز وصل آخر السورة بالبسملة ثم الوقوف.\n\n"
            "🧪 *مثال:* ﴿بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ * الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ﴾",
            parse_mode="Markdown"
        )

# لا يوجد else أو رد افتراضي — إذا لم يتحقق أي شرط، لا يرد البوت

# —— تشغيل البوت
def main():
    if not TOKEN:
        print("❌ TOKEN not set.")
        return

    threading.Thread(target=spawn_health_server, daemon=True).start()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print(f"✅ Bot started — health endpoint on port {PORT}")
    app.run_polling()

if __name__ == "__main__":
    main()
