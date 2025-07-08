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
        "🌙 أرسل رقم الصفحة (1–620) لعرض صورة المصحف.\n"
        "🎧 أو اكتب: `ترتيل 45` لسماع التلاوة.\n"
        "🧠 أو اكتب اسم حكم مثل: `ن الإظهار`، `مد طبيعي`، `بسملة`\n"
        "❓ اكتب `مساعدة` أو `الأوامر` لعرض القائمة الكاملة.",
        parse_mode="Markdown"
    )
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()

    if text == "السلام عليكم":
        return await update.message.reply_text("وعليكم السلام ورحمة الله")

    if "صلوات" in text and "محمد" in text:
        return await update.message.reply_text("اللهم صَلِّ عَلَى مُحَمَّدٍ وَآلِ مُحَمَّدٍ")

    # عرض صورة الصفحة + التلاوة إن وُجدت
    if text.isdigit():
        n = int(text)
        if 1 <= n <= 620:
            image_path = os.path.join(QURAN_PAGES_DIR, f"{n}.jpg")
            audio_path = os.path.join(QURAN_PAGES_DIR, f"{n}.ogg")

            if os.path.exists(image_path):
                with open(image_path, "rb") as photo:
                    await update.message.reply_photo(photo=photo)

            if os.path.exists(audio_path):
                with open(audio_path, "rb") as audio:
                    await update.message.reply_voice(voice=audio)

    # أمر ترتيل فقط
    if text.startswith("ترتيل "):
        parts = text.split()
        if len(parts) == 2 and parts[1].isdigit():
            n = int(parts[1])
            if 1 <= n <= 604:
                audio_path = os.path.join(QURAN_PAGES_DIR, f"{n}.ogg")
                if os.path.exists(audio_path):
                    with open(audio_path, "rb") as audio:
                        return await update.message.reply_voice(voice=audio)
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
            "🧠 الحروف: (ي، ر، م، ل، و، ن)\n"
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
            "يُمد بمقدار حركتين دون سبب.\n"
            "🧪 *أمثلة:*\n"
            "• ﴿قَالَ﴾\n"
            "• ﴿يَقُولُ﴾\n"
            "• ﴿فِيهِ﴾",
            parse_mode="Markdown"
        )

    if text == "مد لازم":
        return await update.message.reply_text(
            "📏 *المد اللازم:*\n"
            "يأتي بعده حرف ساكن أصلي ويُمد 6 حركات.\n"
            "🧪 *أمثلة:*\n"
            "• ﴿الضَّالِّينَ﴾\n"
            "• ﴿الْحَاقَّةُ﴾",
            parse_mode="Markdown"
        )

    if text == "مد متصل":
        return await update.message.reply_text(
            "📏 *المد المتصل:*\n"
            "يأتي حرف المد وبعده همزة في نفس الكلمة.\n"
            "🧪 *أمثلة:*\n"
            "• ﴿جَاءَ﴾\n"
            "• ﴿سُوءَ﴾",
            parse_mode="Markdown"
        )

    if text == "مد منفصل":
        return await update.message.reply_text(
            "📏 *المد المنفصل:*\n"
            "يأتي حرف المد في آخر الكلمة، والهمزة في أول الكلمة التالية.\n"
            "🧪 *أمثلة:*\n"
            "• ﴿يَا أَيُّهَا﴾\n"
            "• ﴿إِنَّا أَنْزَلْنَاهُ﴾",
            parse_mode="Markdown"
        )

    # البسملة
    if text == "بسملة":
        return await update.message.reply_text(
            "🌸 *البسملة:*\n"
            "﴿بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ﴾\n\n"
            "📖 *تعريفها:*\n"
            "آية من الفاتحة، وتُقرأ في بداية كل سورة ما عدا التوبة.\n"
            "📌 *أحكامها:*\n"
            "• لا يجوز وصل آخر السورة بالبسملة ثم الوقوف.\n"
            "• تُقال عند بدء التلاوة.\n"
            "🧪 *مثال:* ﴿بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ * الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ﴾",
            parse_mode="Markdown"
        )
    # المساعدة
    if text in ["مساعدة", "الأوامر"]:
        return await update.message.reply_text(
            "📜 *قائمة الأوامر التي يدعمها البوت:*\n\n"
            "🔹 *عرض صفحات المصحف:*\n"
            "أرسل رقم الصفحة من 1 إلى 620\n"
            "مثال: `45`\n\n"
            "🎧 *تشغيل التلاوة الصوتية:*\n"
            "اكتب: `ترتيل 45` لإرسال الصوت فقط\n\n"
            "🧠 *أحكام النون الساكنة والتنوين:*\n"
            "• `ن الإظهار`\n"
            "• `ن الإدغام`\n"
            "• `ن الإقلاب`\n"
            "• `ن الإخفاء`\n\n"
            "🧠 *أحكام الميم الساكنة:*\n"
            "• `م الإظهار`\n"
            "• `م الإدغام`\n"
            "• `م الإخفاء`\n\n"
            "📏 *المدود:*\n"
            "• `مد طبيعي`\n"
            "• `مد لازم`\n"
            "• `مد متصل`\n"
            "• `مد منفصل`\n\n"
            "🌸 *أوامر إضافية:*\n"
            "• `بسملة`\n"
            "• `السلام عليكم`\n"
            "• `صلوات على محمد`\n\n"
            "✳️ *ملاحظة:* يجب كتابة الأوامر كما هي تمامًا بدون تغيير.",
            parse_mode="Markdown"
        )

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
