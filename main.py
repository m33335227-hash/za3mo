import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

# Вставь сюда свой токен из BotFather полностью:
TOKEN = "8736876315:AAEisG9jUwQu6AtTUq92wioUJwYRJz5_cQE"

bot = Bot(token=TOKEN)
dp = Dispatcher()

class OrderState(StatesGroup):
    choosing_service = State()
    waiting_for_details = State()
    waiting_for_phone = State()

def main_menu():
    kb = [
        [types.KeyboardButton(text="🚕 Такси"), types.KeyboardButton(text="📦 Курьер")],
        [types.KeyboardButton(text="🛍 Магазин"), types.KeyboardButton(text="💊 Аптека")],
        [types.KeyboardButton(text="☕️ Кафе")]
    ]
    return types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Салом! Выберите нужную услугу:", reply_markup=main_menu())

@dp.message(F.text.in_({"🚕 Такси", "📦 Курьер", "🛍 Магазин", "💊 Аптека", "☕️ Кафе"}))
async def service_chosen(message: types.Message, state: FSMContext):
    await state.update_data(chosen_service=message.text)
    await message.answer(f"Вы выбрали {message.text}. Введите адрес или детали заказа:")
    await state.set_state(OrderState.waiting_for_details)

@dp.message(OrderState.waiting_for_details)
async def process_details(message: types.Message, state: FSMContext):
    await state.update_data(details=message.text)
    await message.answer("Теперь отправьте ваш номер телефона:")
    await state.set_state(OrderState.waiting_for_phone)

@dp.message(OrderState.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(f"✅ Заказ на '{data['chosen_service']}' принят!\nДетали: {data['details']}\nТел: {message.text}")
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
