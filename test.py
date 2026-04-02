import logging
import os
from telethon import TelegramClient
import asyncio
from datetime import datetime
from dotenv import load_dotenv
import sys
import pytz

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

tz = pytz.timezone("Asia/Tashkent")
now = datetime.now(tz)

logger = logging.getLogger(__name__)

API_HASH = os.getenv("API_HASH")
API_ID = int(os.getenv("API_ID").strip())
BOT_USERNAME = os.getenv("BOT_USERNAME")
ORDER_TIME = os.getenv("ORDER_TIME")
PHONE = os.getenv("PHONE")

client = TelegramClient("food_order_session", API_ID, API_HASH)


async def place_order():
    try:
        logger.info("Buyurtma boshlandi...")

        bot = await client.get_entity(BOT_USERNAME)
        logger.info(f"Bot: {bot.username}")

        async with client.conversation(bot) as conv:
            await conv.send_message("/start")
            await conv.get_response()
            await asyncio.sleep(1)

            messages = await client.get_messages(bot, limit=5)
            ertangi_button = None

            for msg in messages:
                if msg.reply_markup:
                    for row in msg.reply_markup.rows:
                        for button in row.buttons:
                            if (
                                "ertangi" in button.text.lower()
                                and "buyurtma" in button.text.lower()
                            ):
                                ertangi_button = button.text
                                break
                        if ertangi_button:
                            break
                if ertangi_button:
                    break

            if not ertangi_button:
                logger.warning("Ertangi buyurtma tugmasi topilmadi")
                return False

            logger.info(f"'{ertangi_button}' bosilmoqda...")
            await conv.send_message(ertangi_button)
            response = await conv.get_response()
            await asyncio.sleep(2)

            if not response.reply_markup:
                new_messages = await client.get_messages(bot, limit=3)
                for msg in new_messages:
                    if msg.reply_markup:
                        response = msg
                        break

            if not response.reply_markup:
                logger.warning("Ovqat tugmalari topilmadi")
                return False

            logger.info("Ovqatlar tanlanmoqda...")
            clicked = 0

            for row in response.reply_markup.rows:
                for button in row.buttons:
                    btn_lower = button.text.lower()

                    if any(
                        k in btn_lower
                        for k in ["nonushta", "tushlik", "kechki", "ovqat"]
                    ):
                        if not any(
                            s in btn_lower
                            for s in [
                                "orqaga",
                                "bekor",
                                "chiqish",
                                "back",
                                "cancel",
                                "qaytish",
                            ]
                        ):

                            if "✅" in button.text:
                                logger.info(f"✅ {button.text} - allaqachon tanlangan")
                            else:
                                logger.info(f"- {button.text}")

                                if hasattr(button, "data"):
                                    await response.click(data=button.data)
                                else:
                                    await conv.send_message(button.text)
                                    try:
                                        await conv.get_response(timeout=2)
                                    except asyncio.TimeoutError:
                                        pass

                                clicked += 1
                                await asyncio.sleep(1.5)

            logger.info(f"Ovqatlar tanlandi: {clicked} ta")
            await asyncio.sleep(2)

            logger.info("Buyurtma tasdiqlanmoqda...")
            messages = await client.get_messages(bot, limit=5)

            for msg in messages:
                if msg.reply_markup:
                    for row in msg.reply_markup.rows:
                        for button in row.buttons:
                            if (
                                "ertangi" in button.text.lower()
                                and "buyurtma" in button.text.lower()
                            ):
                                logger.info(f"'{button.text}' yana bosilmoqda...")
                                await conv.send_message(button.text)
                                await asyncio.sleep(1)
                                break

            logger.info("Buyurtma muvaffaqiyatli!")
            return True

    except Exception as e:
        logger.error(f"Xatolik: {e}")
        import traceback

        traceback.print_exc()
        return False


async def schedule_daily_order():
    logger.info("=" * 60)
    logger.info("TELEGRAM BOT AVTOMATIK BUYURTMA")
    logger.info("=" * 60)
    logger.info(f"Vaqt: {ORDER_TIME}")
    logger.info(f"Bot: {BOT_USERNAME}")
    logger.info("=" * 60)

    while True:
        now = datetime.now(tz)
        current_time = now.strftime("%H:%M")

        if current_time == ORDER_TIME:
            logger.info(f"Buyurtma vaqti: {ORDER_TIME}")
            success = await place_order()
            logger.info("Tugadi" if success else "Xato")
            await asyncio.sleep(61)
        else:
            await asyncio.sleep(30)


async def main():
    try:
        await client.start(phone=PHONE)
        me = await client.get_me()
        logger.info(f"Telegram: {me.first_name}")

        logger.info("Test buyurtma...")
        # await place_order()

        logger.info("Avtomat rejim yoqildi...")
        await schedule_daily_order()

    except KeyboardInterrupt:
        logger.info("To'xtatildi")
    except Exception as e:
        logger.error(f"Xatolik: {e}")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
