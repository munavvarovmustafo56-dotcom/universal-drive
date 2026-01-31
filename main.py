import logging
import asyncio
import os
import urllib.parse
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from duckduckgo_search import DDGS

# --- SOZLAMALAR ---
# ⚠️ TOKENNI O'ZINGIZNIKIGA ALMASHTIRING!
TOKEN = "8528746370:AAH7K_PYqQWKMbLzRAjiWmkCjOOWNKMSdvk" 

# Renderdagi sayt manzilingiz (buni Deploy qilgandan keyin olasiz)
WEB_APP_URL = "https://universal-drive.onrender.com" 

bot = Bot(token=TOKEN)
dp = Dispatcher()

routes = web.RouteTableDef()

@routes.get('/')
async def index(request):
    try:
        return web.FileResponse('./index.html')
    except Exception:
        return web.Response(text="Index fayl topilmadi", status=404)

@routes.get('/search')
async def search_api(request):
    query = request.query.get('q', '')
    results = []
    
    # --- YANGI MANTIQ: Yumshoqroq qidiruv ---
    # filetype:pdf ni olib tashladik, chunki ba'zi manuallar oddiy sahifada bo'ladi
    search_queries = [
        f"{query} datasheet manual pdf",
        f"{query} application note circuit"
    ]

    try:
        ddgs = DDGS()
        seen_links = set()

        for q_text in search_queries:
            # 5 ta natija so'raymiz
            search_res = ddgs.text(q_text, max_results=5)
            
            if search_res:
                for r in search_res:
                    link = r['href']
                    title = r['title']
                    
                    if link not in seen_links:
                        # --- FILTRNI YUMSHATISH ---
                        # Linkda yoki Sarlavhada PDF/Manual so'zi bo'lsa olaveramiz
                        is_relevant = False
                        doc_type = "Hujjat"

                        check_str = (title + link).lower()
                        
                        if "pdf" in check_str: 
                            doc_type = "PDF Fayl"
                            is_relevant = True
                        elif "manual" in check_str: 
                            doc_type = "Manual (Kitob)"
                            is_relevant = True
                        elif "datasheet" in check_str: 
                            doc_type = "Texnik Pasport"
                            is_relevant = True
                        elif "download" in check_str:
                            doc_type = "Yuklash"
                            is_relevant = True
                        
                        # Agar "Delixi" so'zi sarlavhada bo'lsa ham olaveramiz (aniqlik uchun)
                        if query.lower().split()[0] in title.lower():
                            is_relevant = True

                        if is_relevant:
                            results.append({
                                "title": title,
                                "link": link,
                                "snippet": r['body'],
                                "type": doc_type
                            })
                            seen_links.add(link)

    except Exception as e:
        print(f"Qidiruv xatosi: {e}")
    
    # --- ZAXIRA REJASI (PLAN B) ---
    # Agar hech narsa topilmasa, Google Qidiruv linkini qo'shamiz
    if len(results) == 0:
        google_link = f"https://www.google.com/search?q={urllib.parse.quote(query + ' filetype:pdf')}"
        results.append({
            "title": "🔍 Google orqali qidirish (Zaxira)",
            "link": google_link,
            "snippet": "Bot avtomatik topa olmadi, lekin Google bazasidan ushbu havola orqali topishingiz mumkin.",
            "type": "Google Search"
        })

    return web.json_response(results)

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔎 Komponent Qidirish", web_app=WebAppInfo(url=WEB_APP_URL))]],
        resize_keyboard=True
    )
    await message.answer(
        "👋 **Universal Driver**\nInverter, PLC va Mikrosxemalar uchun hujjatlarni qidirish tizimi.\n\nPastdagi tugmani bosing:",
        reply_markup=kb
    )

async def on_startup(app):
    await bot.delete_webhook(drop_pending_updates=True)
    asyncio.create_task(dp.start_polling(bot))

async def main():
    app = web.Application()
    app.add_routes(routes)
    app.on_startup.append(on_startup)
    
    port = int(os.environ.get("PORT", 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    print(f"Server {port}-portda ishlayapti...")
    await asyncio.Event().wait()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
