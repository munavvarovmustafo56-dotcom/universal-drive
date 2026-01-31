import logging
import asyncio
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo, ReplyKeyboardMarkup, KeyboardButton

# TOKENNI YOZING
TOKEN = "8528746370:AAH7K_PYqQWKMbLzRAjiWmkCjOOWNKMSdvk" 
# WEB APP URL (RENDER LINK)
WEB_APP_URL = "https://universal-drive.onrender.com" 

bot = Bot(token=TOKEN)
dp = Dispatcher()
routes = web.RouteTableDef()

@routes.get('/')
async def index(request):
    return web.FileResponse('./index.html')

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⚡️ Gelectronics Tizimiga Kirish", web_app=WebAppInfo(url=WEB_APP_URL))]],
        resize_keyboard=True
    )
    await message.answer(
        "👋 **Gelectronics Smart System**\n\nAvto-aniqlash va T9 tizimi bilan jihozlangan qidiruv.\nPastdagi tugmani bosing:",
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
    await asyncio.Event().wait()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
