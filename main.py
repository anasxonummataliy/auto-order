import os
from telethon import TelegramClient
import asyncio
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


API_HASH = os.getenv("API_HASH")
API_ID = os.getenv("API_ID")
BOT_USERNAME = os.getenv("BOT_USERNAME")
ORDER_TIME = os.getenv("BOT_USERNAME")
PHONE = os.getenv("PHONE")

client = TelegramClient("food_order_session", API_ID, API_HASH)


async def place_order():
    try:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Buyurtma boshlandi...")

        bot = await client.get_entity(BOT_USERNAME)
        print(f"Bot: {bot.username}")

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
                print("Ertangi buyurtma tugmasi topilmadi")
                return False

            print(f"'{ertangi_button}' bosilmoqda...")
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
                print("Ovqat tugmalari topilmadi")
                return False

            print("Ovqatlar tanlanmoqda...")
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
                                print(f"  ✅ {button.text} - allaqachon tanlangan")
                            else:
                                print(f"  - {button.text}")

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

            print(f"Ovqatlar tanlandi: {clicked} ta")
            await asyncio.sleep(2)

            print("Buyurtma tasdiqlanmoqda...")
            messages = await client.get_messages(bot, limit=5)

            for msg in messages:
                if msg.reply_markup:
                    for row in msg.reply_markup.rows:
                        for button in row.buttons:
                            if (
                                "ertangi" in button.text.lower()
                                and "buyurtma" in button.text.lower()
                            ):
                                print(f"'{button.text}' yana bosilmoqda...")
                                await conv.send_message(button.text)
                                await asyncio.sleep(1)
                                break

            print("Buyurtma muvaffaqiyatli!")
            return True

    except Exception as e:
        print(f"Xatolik: {e}")
        import traceback

        traceback.print_exc()
        return False


async def schedule_daily_order():
    print("=" * 60)
    print("TELEGRAM BOT AVTOMATIK BUYURTMA")
    print("=" * 60)
    print(f"Vaqt: {ORDER_TIME}")
    print(f"Bot: {BOT_USERNAME}")
    print("=" * 60)

    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M")

        if current_time == ORDER_TIME:
            print(f"\nBuyurtma vaqti: {ORDER_TIME}")
            success = await place_order()
            print("Tugadi\n" if success else "Xato\n")
            await asyncio.sleep(61)
        else:
            await asyncio.sleep(30)


async def main():
    try:
        await client.start(phone=PHONE)
        me = await client.get_me()
        print(f"\nTelegram: {me.first_name}\n")

        print("Test buyurtma...")
        await place_order()

        print("\nAvtomat rejim yoqildi...\n")
        await schedule_daily_order()

    except KeyboardInterrupt:
        print("\n\nTo'xtatildi")
    except Exception as e:
        print(f"\nXatolik: {e}")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
