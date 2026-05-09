import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

TOKEN = "8736876315:AAEisG9jUwQu6AtTUq92wioUJwYRJz5_cQE"
bot = Bot(token=TOKEN)
dp = Dispatcher()

class OrderProcess(StatesGroup):
    waiting_for_location = State()
    waiting_for_details = State()
    waiting_for_phone = State()

def main_menu():
    kb = [
        [types.KeyboardButton(text="🚕 Заказать Такси")],
        [types.KeyboardButton(text="📦 Вызвать Курьера")],
        [types.KeyboardButton(text="🛍 Магазин"), types.KeyboardButton(text="💊 Аптека")],
        [types.KeyboardButton(text="☕️ Кафе")]
    ]
    return types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Салом! Выберите нужную услугу:", reply_markup=main_menu())

# --- НАЧАЛО ЗАКАЗА (ТАКСИ И КУРЬЕР) ---
@dp.message(F.text.in_({"🚕 Заказать Такси", "📦 Вызвать Курьера"}))
async def order_start(message: types.Message, state: FSMContext):
    service = "ТАКСИ" if "Такси" in message.text else "КУРЬЕР"
    await state.update_data(service_type=service)
    
    kb = [[types.KeyboardButton(text="📍 Отправить местоположение", request_location=True)]]
    markup = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
    
    await message.answer(f"Вы выбрали {service}. Отправьте вашу геолокацию:", reply_markup=markup)
    await state.set_state(OrderProcess.waiting_for_location)

# --- ПОЛУЧЕНИЕ ЛОКАЦИИ ---
@dp.message(OrderProcess.waiting_for_location, F.location)
async def get_location(message: types.Message, state: FSMContext):
    map_link = f"https://google.com{message.location.latitude},{message.location.longitude}"
    await state.update_data(location=map_link)
    
    data = await state.get_data()
    msg = "Куда вам нужно ехать?" if data['service_type'] == "ТАКСИ" else "Что нужно доставить?"
    
    await message.answer(msg, reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(OrderProcess.waiting_for_details)

# --- ПОЛУЧЕНИЕ ДЕТАЛЕЙ ---
@dp.message(OrderProcess.waiting_for_details)
async def get_details(message: types.Message, state: FSMContext):
    await state.update_data(details=message.text)
    
    kb = [[types.KeyboardButton(text="📱 Отправить номер телефона", request_contact=True)]]
    markup = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
    
    await message.answer("Отправьте ваш номер телефона для связи:", reply_markup=markup)
    await state.set_state(OrderProcess.waiting_for_phone)

# --- ФИНАЛ ---
@dp.message(OrderProcess.waiting_for_phone, F.content_type.in_({'text', 'contact'}))
async def order_done(message: types.Message, state: FSMContext):
    data = await state.get_data()
    phone = message.contact.phone_number if message.contact else message.text
    
    result = (f"✅ НОВЫЙ ЗАКАЗ: {data['service_type']}\n\n"
              f"📍 Локация: {data['location']}\n"
              f"📝 Детали: {data['details']}\n"
              f"📞 Тел: {phone}")
    
    await message.answer(result, reply_markup=main_menu())
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
