from telethon import TelegramClient
from telethon.errors import (
    SessionPasswordNeededError,
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
)
from telethon.sessions import StringSession

from app.db.models import AccountStatus


class AccountAuthService:
    def __init__(self, account):
        self.account = account
        self.client = TelegramClient(
            self.account.session_name,
            self.account.api_id,
            self.account.api_hash,
        )

    async def send_code(self):
        await self.client.connect()
        try:
            sent = await self.client.send_code_request(self.account.phone)
            return {
                "success": True,
                "phone_code_hash": sent.phone_code_hash,
                "message": "Kod yuborildi.",
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Kod yuborishda xatolik: {e}",
            }
        finally:
            await self.client.disconnect()

    async def confirm_code(self, code: str, phone_code_hash: str):
        await self.client.connect()
        try:
            await self.client.sign_in(
                phone=self.account.phone,
                code=code,
                phone_code_hash=phone_code_hash,
            )

            return {
                "success": True,
                "status": AccountStatus.ACTIVE,
                "message": "Account muvaffaqiyatli aktiv qilindi.",
            }

        except SessionPasswordNeededError:
            return {
                "success": False,
                "need_password": True,
                "message": "Bu accountda 2-bosqichli parol bor. Parol kiriting.",
            }

        except PhoneCodeInvalidError:
            return {
                "success": False,
                "message": "Kod noto'g'ri.",
            }

        except PhoneCodeExpiredError:
            return {
                "success": False,
                "message": "Kod eskirib qolgan.",
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Tasdiqlashda xatolik: {e}",
            }
        finally:
            await self.client.disconnect()

    async def confirm_password(self, password: str):
        await self.client.connect()
        try:
            await self.client.sign_in(password=password)

            return {
                "success": True,
                "status": AccountStatus.ACTIVE,
                "message": "2FA parol bilan account aktiv qilindi.",
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Parolda xatolik: {e}",
            }
        finally:
            await self.client.disconnect()
