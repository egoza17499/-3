def get_user_status_details(user):
    """
    Возвращает детальную информацию о статусе пользователя
    Returns: (indicator, status_text, details_list)
    """
    try:
        warnings, bans = check_date_warnings(user)
        
        if bans:
            # 🔴 Красный кирпич - что-то истекло
            return "🛑", "Запрещено", bans
        elif warnings:
            # 🟡 Желтый восклицательный - истекает в течение 30 дней
            return "⚠️", "Внимание", warnings
        else:
            # 🟢 Зеленый круг - всё хорошо
            return "🟢", "OK", []
    except Exception as e:
        logger.error(f"Ошибка проверки статуса: {e}")
        return "⚪", "Ошибка", []

def create_user_list_keyboard(user_id, fio):
    """Создаёт клавиатуру с кнопкой для перехода к профилю"""
    fio_short = fio[:40] + "..." if len(fio) > 40 else fio
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"👤 {fio_short}", callback_data=f"admin_user_profile_{user_id}")],
        [InlineKeyboardButton(text="🔙 Назад к списку", callback_data="admin_list")]
    ])

@router.callback_query(F.data == "admin_list")
@admin_required
async def admin_list(callback: types.CallbackQuery, state: FSMContext):
    try:
        users = db.get_all_users()
        
        if not users:
            text = "📋 Список пользователей:\n\nПользователей пока нет"
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_functions_back")]
            ])
            await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
            await callback.answer()
            return
        
        text = "📋 <b>Список пользователей</b>\n\n"
        text += "💡 <i>Введите фамилию для поиска или нажмите на имя</i>\n\n"
        
        # Считаем статистику
        green_count = 0
        yellow_count = 0
        red_count = 0
        
        for i, user in enumerate(users, 1):
            user_id = user[0] if len(user) > 0 else 0
            username = user[1] if len(user) > 1 else "Не указан"
            fio = user[3] if len(user) > 3 else "Не указано"
            rank = user[4] if len(user) > 4 else "Не указано"
            
            # Экранируем HTML
            fio_safe = str(fio).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
            username_safe = str(username).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
            rank_safe = str(rank).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;') if rank else "Не указано"
            
            # Получаем статус
            indicator, status_label, details = get_user_status_details(user)
            
            # Считаем статистику
            if indicator == "🟢":
                green_count += 1
            elif indicator == "⚠️":
                yellow_count += 1
            elif indicator == "🛑":
                red_count += 1
            
            # Формируем строку пользователя
            text += f"{i}. {indicator} <b>{fio_safe}</b>\n"
            text += f"   👤 @{username_safe} | 🎖 {rank_safe}\n"
            
            # Добавляем детали статуса
            if details:
                for detail in details:
                    detail_safe = str(detail).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
                    text += f"   <i>{detail_safe}</i>\n"
            
            text += "\n"
            
            if len(text) > 3500:
                text += f"... и ещё {len(users) - i} пользователей\n"
                break
        
        # Добавляем статистику
        text += f"\n<b>Статус:</b> 🟢 {green_count} | ⚠️ {yellow_count} | 🛑 {red_count}\n"
        text += "\n<i>Введите текст для поиска или нажмите Назад</i>"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_functions_back")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await state.set_state(AdminListState.waiting_for_search)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка в admin_list: {e}", exc_info=True)
        await callback.message.answer("❌ Ошибка при получении списка", parse_mode="HTML")
        await callback.answer()

@router.message(AdminListState.waiting_for_search, F.text)
@admin_required_message
async def admin_list_search_handler(message: types.Message):
    try:
        search_text = message.text.strip()
        if len(search_text) < 2:
            await message.answer("⚠️ Введите минимум 2 символа", parse_mode="HTML")
            return
        
        users = db.search_users(search_text)
        if not users:
            await message.answer(f"❌ Пользователи по запросу \"{search_text}\" не найдены", parse_mode="HTML")
            return
        
        if len(users) == 1:
            # Показываем профиль с кнопками
            user = users[0]
            user_id = user[0]
            fio = user[3] if len(user) > 3 else "Не указано"
            
            profile_text = generate_profile_text(user)
            indicator, status_label, details = get_user_status_details(user)
            
            # Добавляем индикатор в начало
            profile_text = f"{indicator} <b>Статус: {status_label}</b>\n\n" + profile_text
            
            # Добавляем детали
            if details:
                profile_text += f"\n<b>Детали:</b>\n"
                for detail in details:
                    detail_safe = str(detail).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
                    profile_text += f"• {detail_safe}\n"
            
            keyboard = create_user_list_keyboard(user_id, fio)
            await message.answer(profile_text, reply_markup=keyboard, parse_mode="HTML")
        else:
            # Показываем список с кнопками
            text = f"🔍 Найдено: {len(users)}\n\n"
            keyboard_buttons = []
            
            for i, user in enumerate(users, 1):
                user_id = user[0]
                fio = user[3] if len(user) > 3 else "Не указано"
                rank = user[4] if len(user) > 4 else "Не указано"
                username = user[1] if len(user) > 1 else "Не указан"
                
                fio_safe = str(fio).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
                username_safe = str(username).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
                rank_safe = str(rank).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;') if rank else "Не указано"
                
                indicator, status_label, details = get_user_status_details(user)
                
                text += f"{i}. {indicator} <b>{fio_safe}</b>\n"
                text += f"   👤 @{username_safe} | 🎖 {rank_safe}\n"
                
                if details:
                    for detail in details:
                        detail_safe = str(detail).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
                        text += f"   <i>{detail_safe}</i>\n"
                
                text += "\n"
                
                # Кнопка для каждого пользователя
                fio_short = fio[:35] + "..." if len(fio) > 35 else fio
                keyboard_buttons.append([
                    InlineKeyboardButton(text=f"👤 {fio_short}", callback_data=f"admin_user_profile_{user_id}")
                ])
            
            keyboard_buttons.append([InlineKeyboardButton(text="🔙 Назад к списку", callback_data="admin_list")])
            keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
            
            await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
            
    except Exception as e:
        logger.error(f"Ошибка поиска: {e}", exc_info=True)
        await message.answer("❌ Ошибка при поиске", parse_mode="HTML")

@router.callback_query(F.data.startswith("admin_user_profile_"))
@admin_required
async def admin_user_profile(callback: types.CallbackQuery):
    """Показывает полный профиль пользователя внутри бота"""
    try:
        user_id = int(callback.data.split("_")[-1])
        
        # Получаем пользователя из БД
        query = """
            SELECT user_id, username, registered_at, fio, rank, qualification,
                   leave_start_date, leave_end_date, vlk_date, umo_date,
                   exercise_4_md_m_date, exercise_7_md_m_date,
                   exercise_4_md_90a_date, exercise_7_md_90a_date,
                   parachute_jump_date, is_registered
            FROM users WHERE user_id = %s
        """
        user = db.execute_query(query, (user_id,), fetch=True)
        
        if not user:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
        
        user = user[0]
        fio = user[3] if len(user) > 3 else "Не указано"
        
        # Генерируем текст профиля
        profile_text = generate_profile_text(user)
        indicator, status_label, details = get_user_status_details(user)
        
        # Добавляем индикатор
        profile_text = f"{indicator} <b>Статус: {status_label}</b>\n\n" + profile_text
        
        # Добавляем детали
        if details:
            profile_text += f"\n<b>⚠️ Детали статуса:</b>\n"
            for detail in details:
                detail_safe = str(detail).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
                profile_text += f"• {detail_safe}\n"
        
        # Кнопки
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад к списку", callback_data="admin_list")],
            [InlineKeyboardButton(text="🔙 Админ функции", callback_data="admin_functions_back")]
        ])
        
        await callback.message.answer(profile_text, reply_markup=keyboard, parse_mode="HTML")
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка просмотра профиля: {e}", exc_info=True)
        await callback.answer("❌ Ошибка", show_alert=True)
