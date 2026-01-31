import logging
import asyncio
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from duckduckgo_search import DDGS

# --- SOZLAMALAR ---
# ⚠️ TOKENNI SHU YERGA QO'YING:
TOKEN = "8528746370:AAH7K_PYqQWKMbLzRAjiWmkCjOOWNKMSdvk" 

# Render linkni keyin o'zgartiramiz, hozircha shunday tursin
WEB_APP_URL = "https://universal-drive.onrender.com" 

bot = Bot(token=TOKEN)
dp = Dispatcher()

routes = web.RouteTableDef()

@routes.get('/')
async def index(request):
    return web.FileResponse('./index.html')

@routes.get('/search')
async def search_api(request):
    query = request.query.get('q', '')
    results = []
    
    search_queries = [
        f"{query} datasheet filetype:pdf",
        f"{query} user manual filetype:pdf",
        f"{query} application note circuit filetype:pdf"
    ]

    try:
        ddgs = DDGS()
        seen_links = set()

        for q_text in search_queries:
            search_res = ddgs.text(q_text, max_results=2)
            if search_res:
                for r in search_res:
                    if r['href'] not in seen_links:
                        if "pdf" in r['href'].lower() or "download" in r['href'].lower():
                            doc_type = "Datasheet"
                            if "manual" in r['title'].lower(): doc_type = "Manual"
                            if "application" in r['title'].lower(): doc_type = "App Note"
                            
                            results.append({
                                "title": r['title'],
                                "link": r['href'],
                                "snippet": r['body'],
                                "type": doc_type
                            })
                            seen_links.add(r['href'])
    except Exception as e:
        print(f"Xato: {e}")

    return web.json_response(results)

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔎 Komponent Qidirish", web_app=WebAppInfo(url=WEB_APP_URL))]],
        resize_keyboard=True
    )
    await message.answer(
        "👋 **Universal Driver**\nIGBT, Inverter va boshqa elektronika uchun 15,000 betlik kitoblarni topib beruvchi tizim.\n\nPastdagi tugmani bosing:",
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
