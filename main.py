import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

TOKEN = import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

TOKEN = "7836876315:AAE1SG9JUuQu6AtTuq92wioUiWYR3z5_cQE"
bot = Bot(token=TOKEN)
dp = Dispatcher()


# --- СОСТОЯНИЯ ---
class OrderState(StatesGroup):
    choosing_service = State()
    waiting_for_details = State() # Описание заказа или адрес
    waiting_for_phone = State()   # Номер телефона

# --- КЛАВИАТУРЫ ---
def main_menu():
    kb = [
        [types.KeyboardButton(text="🚕 Такси"), types.KeyboardButton(text="📦 Курьер")],
        [types.KeyboardButton(text="🛍 Магазин"), types.KeyboardButton(text="💊 Аптека")],
        [types.KeyboardButton(text="☕️ Кафе")]
    ]
    return types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# --- ОБРАБОТЧИКИ ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        f"Салом, {message.from_user.first_name}!\nДобро пожаловать в сервис Каттакургана.\nВыберите нужную услугу:",
        reply_markup=main_menu()
    )

# Обработка выбора ЛЮБОЙ услуги
@dp.message(F.text.in_({"🚕 Такси", "📦 Курьер", "🛍 Магазин", "💊 Аптека", "☕️ Кафе"}))
async def service_chosen(message: types.Message, state: FSMContext):
    service = message.text
    await state.update_data(chosen_service=service)
    
    if service == "🚕 Такси":
        await message.answer("Введите адрес, куда подать машину:")
    elif service == "📦 Курьер":
        await message.answer("Что нужно доставить и откуда?")
    else:
        await message.answer(f"Напишите список товаров или название из раздела {service}:")
    
    await state.set_state(OrderState.waiting_for_details)

# Принимаем детали (адрес или список товаров)
@dp.message(OrderState.waiting_for_details)
async def process_details(message: types.Message, state: FSMContext):
    await state.update_data(details=message.text)
    await message.answer("Теперь отправьте ваш номер телефона (или нажмите кнопку)", 
                         reply_markup=types.ReplyKeyboardMarkup(
                             keyboard=[[types.KeyboardButton(text="📱 Отправить контакт", request_contact=True)]],
                             resize_keyboard=True, one_time_keyboard=True))
    await state.set_state(OrderState.waiting_for_phone)

# Финал заказа
@dp.message(OrderState.waiting_for_phone, F.content_type.in_({'text', 'contact'}))
async def process_phone(message: types.Message, state: FSMContext):
    data = await state.get_data()
    phone = message.contact.phone_number if message.contact else message.text
    
    # Формируем отчет
    report = (f"🔔 НОВЫЙ ЗАКАЗ!\n"
              f"🛠 Услуга: {data['chosen_service']}\n"
              f"📝 Детали: {data['details']}\n"
              f"📞 Телефон: {phone}\n"
              f"👤 Клиент: @{message.from_user.username or 'нет username'}")

    await message.answer(f"✅ Спасибо! Ваш заказ на '{data['chosen_service']}' принят.\nСкоро мы с вами свяжемся!", 
                         reply_markup=main_menu())
    
    # Печатаем заказ в консоль (потом сюда добавим отправку админу)
    print(report)
    await state.clear()

async def main():
    print("Бот запущен и ждет заказов...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
