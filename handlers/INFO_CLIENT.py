from aiogram import Router, F, types, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, FSInputFile
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

AUDIO_PATH = 'energocouch_tgBot\energocouch_tgBot\handlers\Энергопрактика_Саши_Белякова.mp3'
CHANNEL_ID=-1002485471071
router = Router()
ADMIN_ID=519234410

class Registration(StatesGroup):
    waiting_for_full_name = State()
    waiting_for_tg_choice = State()
    waiting_for_phone_choice = State()
    waiting_for_phone_manual = State()
    waiting_for_confirmation = State()
    waiting_for_course_choice = State()

@router.message(Command('start'))
async def cmd_start(message: Message, state: FSMContext):
   await message.answer(
       "Привет, меня зовут Беляш, я добрый дух-помощник энергокоуча и психолога Александра Белякова, а как тебя зовут?\n"
        "\n"
        "<b>Напиши своё имя и фамилию?</b>"
   )
   await state.set_state(Registration.waiting_for_full_name)


@router.message(Registration.waiting_for_full_name)
async def process_tg_choice(message: Message, state: FSMContext):
    full_name = message.text.strip()
    await state.update_data(full_name=full_name)
    await message.answer(
        'Круто, теперь напишу свой тг_аккаунт\n'
        '\n'
        '(<b>например</b> @sumasoshedshiy)'
    )
    await state.set_state(Registration.waiting_for_tg_choice)


@router.message(Registration.waiting_for_tg_choice)
async def process_full_name(message: Message, state: FSMContext):
    tg_acc = message.text.strip()
    await state.update_data(tg_acc=tg_acc)

    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text='Автоматически скинуть свой номер', request_contact=True),
        types.KeyboardButton(text='напишу сам',)
       )

    await message.answer(
        'Отлично! Теперь напиши свой номер телефона или отправь его автоматически:',
        reply_markup=builder.as_markup(resize_keyboard=True)
    )
    await state.set_state(Registration.waiting_for_phone_choice)


@router.message(Registration.waiting_for_phone_choice, F.contact)
async def process_contact(message: Message, state: FSMContext):
    phone = message.contact.phone_number
    await state.update_data(phone=phone)
    await show_user_info_and_ask_subscription(message, state, message.bot)


@router.message(Registration.waiting_for_phone_choice, F.text.lower() == 'напишу сам')
async def process_manual_choice(message: Message, state: FSMContext):
    await message.answer(
        "Хорошо, напиши свой номер телефона вручную:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(Registration.waiting_for_phone_manual)

@router.message(Registration.waiting_for_phone_manual)
async def process_manual_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    await state.update_data(phone=phone)
    await show_user_info_and_ask_subscription(message, state, message.bot)

async def show_user_info_and_ask_subscription(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    full_name = data.get('full_name')
    tg_acc = data.get('tg_acc')
    phone = data.get('phone')

    # Отправляем данные пользователю
    await message.answer(
        f"Спасибо, {full_name}!\n"
        f"Твой Telegram: {tg_acc}\n"
        f"Твой номер: {phone}",
        reply_markup=types.ReplyKeyboardRemove()
    )

    # Отправляем данные админу (вам)
    try:
        await bot.send_message(
            ADMIN_ID,
            f"Новый клиент зарегистрировался 🎉\n"
            f"Имя: {full_name}\n"
            f"Telegram: {tg_acc}\n"
            f"Номер телефона: {phone}"
        )
    except Exception as e:
        print("Ошибка при отправке данных админу:", e)

    # Продолжаем проверку подписки
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text="да",
        callback_data='check_subscription')
    )
    await message.answer(
        "Ты подписан на наш канал: https://t.me/angeliSani?\n"
        "\n"
        "Если нет — скорей подпишись и получишь халяву!",
        reply_markup=builder.as_markup()
    )
    await state.set_state(Registration.waiting_for_confirmation)

@router.callback_query(Registration.waiting_for_confirmation, F.data == 'check_subscription')
async def process_check_subscription(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Проверяю подписку...')
    try:
        chat_member = await callback.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=callback.from_user.id)

        if chat_member.status in ("member", "administrator", "creator"):
            audio = FSInputFile(AUDIO_PATH)
            await callback.message.answer_audio(
                audio,
                caption="Вот твой подарок 🎧\n"
                        "\n"
                        "Если хочешь увидеть услуги Санька нажми на /course"
            )
        else:
            builder = InlineKeyboardBuilder()
            builder.row(types.InlineKeyboardButton(
                text="Подписаться на канал",
                url=f"https://t.me/angeliSani"  # Замени на ссылку на твой канал
            ))
            await callback.message.answer(
                "К сожалению, ты не подписан на канал. Подпишись по кнопке ниже и вернись и нажми на /start",
                reply_markup=builder.as_markup()
            )

    except Exception as e:
        await callback.message.answer("Ошибка при проверке подписки. Попробуй позже.")
        print("Ошибка:", e)

    await callback.answer()

@router.message(Command('course'))
async def cmd_course(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
    text='Энергокоучинг - Личная Энерготерапия с Сашей Беляковым – 7000 рублей',
    url='https://payform.ru/tf83K7G/')
    )
    builder.row(types.InlineKeyboardButton(
        text='Энергокоучинг – Первая/Студенческая Энерготерапия с Сашей Беляковым – 3500 рублей',
        url='https://payform.ru/gd83KgR/')
    )
    builder.row(types.InlineKeyboardButton(
        text='Тариф «Ангел Изобилия» - 3333 рублей',
        url='https://payform.ru/tf83Hgg/')
    )
    builder.row(types.InlineKeyboardButton(
        text='Тариф «Серафим» - 11111 рублей',
        url='https://payform.ru/3b83JDE/')
    )

    await message.answer(
        'Хорошего денёчка от энергичного Cанёчка'
        '/n'
        'Выбери услугу, Ангел Сани)',
        reply_markup=builder.as_markup(),
   )