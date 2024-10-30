import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv, find_dotenv
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from handlers.usr_handler import user_handler_router
from handlers.callback_handler import callback_router
from database.FSM_core import fsm_router


logger = logging.getLogger(__name__)
load_dotenv(find_dotenv())
bot = Bot(token=os.getenv('BOT_TOKEN'), default=DefaultBotProperties(parse_mode='HTML'))


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s'
               '[%(asctime)s] - %(name)s - %(message)s')
    logging.info('Start working...')
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(user_handler_router)
    dp.include_router(callback_router)
    dp.include_router(fsm_router)
    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    asyncio.run(main())
