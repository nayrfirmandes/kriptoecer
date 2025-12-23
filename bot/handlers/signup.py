from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from prisma import Prisma

from bot.formatters.messages import (
    format_terms,
    format_signup_email,
    format_signup_whatsapp,
    format_signup_location,
    format_signup_referral,
    format_signup_success,
    format_main_menu,
    format_error,
)
from bot.keyboards.inline import (
    get_terms_keyboard,
    get_skip_referral_keyboard,
    get_main_menu_keyboard,
    CallbackData,
)
from bot.utils.helpers import (
    validate_email,
    validate_phone,
    normalize_phone,
    generate_referral_code,
)
from bot.db.queries import (
    get_user_by_telegram_id,
    get_user_by_referral_code,
    create_user,
    get_referral_setting,
    process_referral_bonus,
)

router = Router()


class SignupStates(StatesGroup):
    waiting_email = State()
    waiting_whatsapp = State()
    waiting_location = State()
    waiting_referral = State()


@router.callback_query(F.data == CallbackData.AGREE_TERMS)
async def agree_terms(callback: CallbackQuery, state: FSMContext, db: Prisma, **kwargs):
    user = await get_user_by_telegram_id(db, callback.from_user.id)
    
    if user and user.status == "INACTIVE":
        await db.user.delete(where={"id": user.id})
    elif user and user.status == "ACTIVE":
        await callback.answer("Anda sudah terdaftar!", show_alert=True)
        return
    
    await state.set_state(SignupStates.waiting_email)
    
    await callback.message.edit_text(
        format_signup_email(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(SignupStates.waiting_email)
async def process_email(message: Message, state: FSMContext, **kwargs):
    email = message.text.strip().lower()
    
    if not validate_email(email):
        await message.answer(
            format_error("Format email tidak valid. Silakan coba lagi."),
            parse_mode="HTML"
        )
        return
    
    await state.update_data(email=email)
    await state.set_state(SignupStates.waiting_whatsapp)
    
    await message.answer(
        format_signup_whatsapp(),
        parse_mode="HTML"
    )


@router.message(SignupStates.waiting_whatsapp)
async def process_whatsapp(message: Message, state: FSMContext, **kwargs):
    phone = message.text.strip()
    
    if not validate_phone(phone):
        await message.answer(
            format_error("Format nomor tidak valid. Gunakan format 08xxx atau 628xxx."),
            parse_mode="HTML"
        )
        return
    
    normalized = normalize_phone(phone)
    await state.update_data(whatsapp=normalized)
    await state.set_state(SignupStates.waiting_location)
    
    await message.answer(
        format_signup_location(),
        parse_mode="HTML"
    )


@router.message(SignupStates.waiting_location, F.content_type == ContentType.LOCATION)
async def process_location(message: Message, state: FSMContext, **kwargs):
    location = message.location
    
    await state.update_data(
        latitude=location.latitude,
        longitude=location.longitude
    )
    await state.set_state(SignupStates.waiting_referral)
    
    await message.answer(
        format_signup_referral(),
        reply_markup=get_skip_referral_keyboard(),
        parse_mode="HTML"
    )


@router.message(SignupStates.waiting_location)
async def process_location_text(message: Message, **kwargs):
    await message.answer(
        "📍 Silakan bagikan lokasi Anda menggunakan fitur 'Share Location' di Telegram.\n\n"
        "Klik ikon 📎 (attachment) → Location → Share My Location",
        parse_mode="HTML"
    )


@router.message(SignupStates.waiting_referral)
async def process_referral(message: Message, state: FSMContext, db: Prisma, **kwargs):
    referral_code = message.text.strip().upper()
    
    referrer = await get_user_by_referral_code(db, referral_code)
    
    if referrer:
        await state.update_data(referred_by_id=referrer.id)
        await complete_signup(message, state, db)
    else:
        await message.answer(
            format_error("Kode referral tidak ditemukan. Coba lagi atau klik 'Lewati'."),
            reply_markup=get_skip_referral_keyboard(),
            parse_mode="HTML"
        )


@router.callback_query(F.data == CallbackData.SKIP_REFERRAL)
async def skip_referral(callback: CallbackQuery, state: FSMContext, db: Prisma, **kwargs):
    await state.update_data(referred_by_id=None)
    await complete_signup_callback(callback, state, db)


async def complete_signup(message: Message, state: FSMContext, db: Prisma):
    data = await state.get_data()
    
    referral_code = generate_referral_code()
    while await get_user_by_referral_code(db, referral_code):
        referral_code = generate_referral_code()
    
    user = await create_user(
        db=db,
        telegram_id=message.from_user.id,
        referral_code=referral_code,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        email=data.get("email"),
        whatsapp=data.get("whatsapp"),
        latitude=data.get("latitude"),
        longitude=data.get("longitude"),
        referred_by_id=data.get("referred_by_id"),
    )
    
    if data.get("referred_by_id"):
        referral_setting = await get_referral_setting(db)
        if referral_setting:
            await process_referral_bonus(
                db=db,
                referrer_id=data["referred_by_id"],
                referee_id=user.id,
                referrer_bonus=referral_setting.referrerBonus,
                referee_bonus=referral_setting.refereeBonus,
            )
    
    await state.clear()
    
    await message.answer(
        format_signup_success(referral_code),
        parse_mode="HTML"
    )
    
    balance = user.balance.amount if user.balance else 0
    name = user.firstName or user.username or "User"
    
    await message.answer(
        format_main_menu(balance, name),
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )


async def complete_signup_callback(callback: CallbackQuery, state: FSMContext, db: Prisma):
    data = await state.get_data()
    
    referral_code = generate_referral_code()
    while await get_user_by_referral_code(db, referral_code):
        referral_code = generate_referral_code()
    
    user = await create_user(
        db=db,
        telegram_id=callback.from_user.id,
        referral_code=referral_code,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name,
        email=data.get("email"),
        whatsapp=data.get("whatsapp"),
        latitude=data.get("latitude"),
        longitude=data.get("longitude"),
        referred_by_id=data.get("referred_by_id"),
    )
    
    if data.get("referred_by_id"):
        referral_setting = await get_referral_setting(db)
        if referral_setting:
            await process_referral_bonus(
                db=db,
                referrer_id=data["referred_by_id"],
                referee_id=user.id,
                referrer_bonus=referral_setting.referrerBonus,
                referee_bonus=referral_setting.refereeBonus,
            )
    
    await state.clear()
    
    await callback.message.edit_text(
        format_signup_success(referral_code),
        parse_mode="HTML"
    )
    
    balance = user.balance.amount if user.balance else 0
    name = user.firstName or user.username or "User"
    
    await callback.message.answer(
        format_main_menu(balance, name),
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()
