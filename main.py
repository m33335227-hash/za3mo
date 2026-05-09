import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

TOKEN = "7836876315:AAE1SG9JUuQu6AtTuq92wioUiWYR3z5_cQE"
bot = Bot(token=TOKEN)
dp = Dispatcher()

class TaxiOrder(StatesGroup):
    waiting_for_location = State()
    waiting_for_dest = State()
    waiting_for_phone = State()

def main_menu():
    kb = [
        [types.KeyboardButton(text="🚕 Заказать Такси")],
        [types.KeyboardButton(text="📦 Курьер"), types.KeyboardButton(text="🛍 Магазин")],
        [types.KeyboardButton(text="💊 Аптека"), types.KeyboardButton(text="☕️ Кафе")]
    ]
    return types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Салом! Выберите услугу:", reply_markup=main_menu())

# --- НАЧАЛО ЗАКАЗА ТАКСИ ---
@dp.message(F.text == "🚕 Заказать Такси")
async def taxi_start(message: types.Message, state: FSMContext):
    # Создаем кнопку для отправки локации
    kb = [[types.KeyboardButton(text="📍 Отправить местоположение", request_location=True)]]
    markup = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
    
    await message.answer("Пожалуйста, отправьте вашу геолокацию, чтобы водитель вас нашел:", reply_markup=markup)
    await state.set_state(TaxiOrder.waiting_for_location)

# --- ПОЛУЧЕНИЕ ЛОКАЦИИ ---
@dp.message(TaxiOrder.waiting_for_location, F.location)
async def get_location(message: types.Message, state: FSMContext):
    lat = message.location.latitude
    lon = message.location.longitude
    # Сохраняем ссылку на карты
    map_link = f"https://google.com{lat},{lon}"
    await state.update_data(location_link=map_link)
    
    await message.answer("Отлично! Теперь напишите, куда вам нужно ехать?", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(TaxiOrder.waiting_for_dest)

# --- КУДА ЕДЕМ ---
@dp.message(TaxiOrder.waiting_for_dest)
async def get_dest(message: types.Message, state: FSMContext):
    await state.update_data(destination=message.text)
    
    # Кнопка для отправки телефона
    kb = [[types.KeyboardButton(text="📱 Отправить номер телефона", request_contact=True)]]
    markup = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
    
    await message.answer("И последний шаг: отправьте ваш номер телефона для связи:", reply_markup=markup)
    await state.set_state(TaxiOrder.waiting_for_phone)

# --- ФИНАЛ ---
@dp.message(TaxiOrder.waiting_for_phone, F.content_type.in_({'text', 'contact'}))
async def taxi_done(message: types.Message, state: FSMContext):
    data = await state.get_data()
    phone = message.contact.phone_number if message.contact else message.text
    
    result = (f"✅ ЗАКАЗ ТАКСИ ОФОРМЛЕН!\n\n"
              f"📍 Место встречи: {data['location_link']}\n"
              f"🏁 Куда: {data['destination']}\n"
              f"📞 Тел: {phone}")
    
    await message.answer(result, reply_markup=main_menu())
    print(f"НОВЫЙ ЗАКАЗ:\n{result}") # Видно в логах Render
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
