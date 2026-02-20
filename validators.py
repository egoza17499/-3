from datetime import datetime
from config import DATE_FORMAT, WARNING_PERIOD

def is_valid_date(date_string):
    """Проверка формата даты"""
    if not date_string:
        return False
    # Проверяем на "освобожден"
    if date_string.lower() in ['освобожден', 'освобождён', 'осв']:
        return True
    try:
        datetime.strptime(date_string, DATE_FORMAT)
        return True
    except ValueError:
        return False

def is_exempt(date_string):
    """Проверка на освобождение"""
    if not date_string:
        return False
    return date_string.lower() in ['освобожден', 'освобождён', 'осв']

def calculate_days_remaining(date_string):
    """Расчёт оставшихся дней до истечения"""
    if not date_string:
        return -999
    # Если освобожден - возвращаем большое положительное число
    if is_exempt(date_string):
        return 9999
    try:
        date_obj = datetime.strptime(date_string, DATE_FORMAT)
        today = datetime.now()
        delta = date_obj - today
        return delta.days
    except ValueError:
        return -999

def get_status_color(days_remaining):
    """Определение статуса по количеству дней"""
    if days_remaining == -999:
        return "⚪"  # Нет данных
    elif days_remaining == 9999:
        return "⚪"  # Освобожден
    elif days_remaining > WARNING_PERIOD:
        return "🟢"  # Зелёный - всё OK
    elif days_remaining > 0:
        return "🟡"  # Жёлтый - скоро истечёт
    else:
        return "🔴"  # Красный - истекло

def check_parameter_status(param_name, date_string, is_parachute=False):
    """Проверка статуса параметра"""
    if not date_string:
        return "⚪ Не указано"
    
    # Специальная обработка для прыжков
    if is_parachute and is_exempt(date_string):
        return "⚪ Освобожден"
    
    if not is_valid_date(date_string):
        return "🔴 Некорректная дата"
    
    days = calculate_days_remaining(date_string)
    color = get_status_color(days)
    
    if days == 9999:
        return f"{color} Освобожден"
    elif days == -999:
        return f"{color} Нет данных"
    elif days < 0:
        return f"{color} Истекло {abs(days)} дней назад"
    elif days == 0:
        return f"{color} Истекает сегодня"
    else:
        return f"{color} {days} дней"

def generate_profile_text(user_data):
    """Генерация текста профиля пользователя"""
    if not user_data:
        return "❌ Пользователь не найден"
    
    # Индексы полей в кортеже (согласно структуре БД)
    chat_id = user_data[1]
    username = user_data[2] or "Не указано"
    fio = user_data[3] or "Не указано"
    rank = user_data[4] or "Не указано"
    qualification = user_data[5] or "Не указано"
    vlk_date = user_data[8]
    umo_date = user_data[9]
    ex4_md_m = user_data[10]
    ex7_md_m = user_data[11]
    ex4_md_90a = user_data[12]
    ex7_md_90a = user_data[13]
    parachute = user_data[14]
    leave_end = user_data[7]
    
    text = f"👤 **{fio}**\n"
    text += f"🔹 Звание: {rank}\n"
    text += f"🔹 Квалификация: {qualification}\n\n"
    
    text += f"📋 **Сроки:**\n"
    text += f"{check_parameter_status('ВЛК', vlk_date)}\n"
    text += f"{check_parameter_status('УМО', umo_date)}\n"
    text += f"{check_parameter_status('КБП-4 МД-М', ex4_md_m)}\n"
    text += f"{check_parameter_status('КБП-7 МД-М', ex7_md_m)}\n"
    text += f"{check_parameter_status('КБП-4 МД-90А', ex4_md_90a)}\n"
    text += f"{check_parameter_status('КБП-7 МД-90А', ex7_md_90a)}\n"
    text += f"{check_parameter_status('Прыжки', parachute, is_parachute=True)}\n"
    
    if leave_end:
        days = calculate_days_remaining(leave_end)
        if days > 0 and days != 9999:
            text += f"\n🏖 **Отпуск:** {check_parameter_status('Отпуск', leave_end)}"
    
    # Проверка на запрет полётов
    bans = check_flight_ban(user_data)
    if bans:
        text += "\n\n🚫 **ПОЛЁТЫ ЗАПРЕЩЕНЫ:**\n"
        text += "\n".join(bans)
    
    return text

def check_flight_ban(user_data):
    """Проверка запретов на полёты"""
    bans = []
    
    if not user_data:
        return bans
    
    # Индексы полей
    vlk_date = user_data[8]
    umo_date = user_data[9]
    ex4_md_m = user_data[10]
    ex7_md_m = user_data[11]
    ex4_md_90a = user_data[12]
    ex7_md_90a = user_data[13]
    parachute = user_data[14]
    
    # Проверка ВЛК (6 месяцев = 180 дней)
    days_vlk = calculate_days_remaining(vlk_date)
    if days_vlk < 0:
        bans.append("🔴 ВЛК истекло")
    elif days_vlk < 30 and days_vlk >= 0:
        bans.append("🟡 ВЛК истекает скоро")
    
    # Проверка УМО (12 месяцев = 360 дней)
    days_umo = calculate_days_remaining(umo_date)
    if days_umo < 0:
        bans.append("🔴 УМО истекло")
    
    # Проверка КБП
    if calculate_days_remaining(ex4_md_m) < 0:
        bans.append("🔴 КБП-4 МД-М истекло")
    
    if calculate_days_remaining(ex7_md_m) < 0:
        bans.append("🔴 КБП-7 МД-М истекло")
    
    if calculate_days_remaining(ex4_md_90a) < 0:
        bans.append("🔴 КБП-4 МД-90А истекло")
    
    if calculate_days_remaining(ex7_md_90a) < 0:
        bans.append("🔴 КБП-7 МД-90А истекло")
    
    # Прыжки НЕ влияют если освобожден
    if not is_exempt(parachute):
        days_parachute = calculate_days_remaining(parachute)
        if days_parachute < 0:
            bans.append("🔴 Прыжки истекли")
    
    return bans
