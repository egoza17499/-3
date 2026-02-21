from datetime import datetime, timedelta
from config import (
    VLK_PERIOD, UMO_PERIOD, EXERCISE_4_PERIOD, 
    EXERCISE_7_PERIOD, LEAVE_PERIOD, PARACHUTE_PERIOD,
    WARNING_PERIOD, DATE_FORMAT
)

def is_valid_date(date_str: str) -> bool:
    """Проверка формата даты"""
    try:
        datetime.strptime(date_str, DATE_FORMAT)
        return True
    except ValueError:
        return False

def parse_date(date_str: str):
    """Парсинг даты"""
    if not date_str or date_str.lower() in ['нет', 'освобожден', 'освобождён', 'осв']:
        return None
    try:
        return datetime.strptime(date_str, DATE_FORMAT)
    except ValueError:
        return None

def get_date_status(date_str: str, period_days: int):
    """
    Получение статуса даты
    Возвращает: (emoji, status_text, days_left_or_overdue)
    """
    if not date_str or date_str.lower() in ['нет', 'освобожден', 'освобождён', 'осв']:
        return '⚪', 'Не указано', 0
    
    date = parse_date(date_str)
    if not date:
        return '⚪', 'Не указано', 0
    
    now = datetime.now()
    expiry_date = date + timedelta(days=period_days)
    days_until_expiry = (expiry_date - now).days
    
    if days_until_expiry < 0:
        # Просрочено
        days_overdue = abs(days_until_expiry)
        return '🔴', f'Просрочено на {days_overdue} дн.', -days_overdue
    elif days_until_expiry <= WARNING_PERIOD:
        # Скоро истечёт
        return '🟡', f'Действует (осталось {days_until_expiry} дн.)', days_until_expiry
    else:
        # Действует
        return '🟢', f'Действует (осталось {days_until_expiry} дн.)', days_until_expiry

def check_flight_ban(user: tuple) -> list:
    """Проверка запретов на полёты"""
    bans = []
    
    # ВЛК
    vlk_date = user[7]
    vlk_status, _, _ = get_date_status(vlk_date, VLK_PERIOD)
    if vlk_status == '🔴':
        bans.append('ВЛК истекло')
    
    # УМО
    umo_date = user[8]
    if umo_date and umo_date.lower() not in ['нет', 'освобожден', 'осв']:
        umo_status, _, _ = get_date_status(umo_date, UMO_PERIOD)
        if umo_status == '🔴':
            bans.append('УМО истекло')
    
    # КБП-4 МД-М
    ex4_md_m = user[9]
    if ex4_md_m:
        status, _, _ = get_date_status(ex4_md_m, EXERCISE_4_PERIOD)
        if status == '🔴':
            bans.append(f'Упражнение 4 (Ил-76 МД-М) истекло')
    
    # КБП-7 МД-М
    ex7_md_m = user[10]
    if ex7_md_m:
        status, _, _ = get_date_status(ex7_md_m, EXERCISE_7_PERIOD)
        if status == '🔴':
            bans.append(f'Упражнение 7 (Ил-76 МД-М) истекло')
    
    # КБП-4 МД-90А
    ex4_md_90a = user[11]
    if ex4_md_90a:
        status, _, _ = get_date_status(ex4_md_90a, EXERCISE_4_PERIOD)
        if status == '🔴':
            bans.append(f'Упражнение 4 (Ил-76 МД-90А) истекло')
    
    # КБП-7 МД-90А
    ex7_md_90a = user[12]
    if ex7_md_90a:
        status, _, _ = get_date_status(ex7_md_90a, EXERCISE_7_PERIOD)
        if status == '🔴':
            bans.append(f'Упражнение 7 (Ил-76 МД-90А) истекло')
    
    return bans

def generate_profile_text(user: tuple) -> str:
    """Генерация текста профиля КАК НА СКРИНШОТЕ"""
    
    fio = user[3] or "Не указано"
    rank = user[4] or "Не указано"
    qualification = user[5] or "Не указано"
    
    # Основные данные
    text = f"👤 {fio}\n"
    text += f"🎖 Звание: {rank}\n"
    text += f"🏅 Квалификация: {qualification}\n\n"
    
    # Отпуск
    leave_end = user[6]
    emoji, status, _ = get_date_status(leave_end, LEAVE_PERIOD)
    text += f"{emoji} Отпуск (конец):: {leave_end or 'Не указан'} ({status})\n"
    
    # ВЛК
    vlk_date = user[7]
    emoji, status, _ = get_date_status(vlk_date, VLK_PERIOD)
    text += f"{emoji} ВЛК: {vlk_date or 'Не указана'} ({status})\n"
    
    # УМО
    umo_date = user[8]
    if umo_date and umo_date.lower() not in ['нет', 'освобожден', 'осв']:
        emoji, status, _ = get_date_status(umo_date, UMO_PERIOD)
        text += f"{emoji} УМО:: {umo_date} ({status})\n"
    else:
        text += f"⚪ УМО:: Не указано\n"
    
    # КБП-4 (Ил-76 МД-М)
    ex4_md_m = user[9]
    if ex4_md_m:
        emoji, status, _ = get_date_status(ex4_md_m, EXERCISE_4_PERIOD)
        text += f"{emoji} КБП-4 (Ил-76 МД-М):: {ex4_md_m} ({status})\n"
    
    # КБП-7 (Ил-76 МД-М)
    ex7_md_m = user[10]
    if ex7_md_m:
        emoji, status, _ = get_date_status(ex7_md_m, EXERCISE_7_PERIOD)
        text += f"{emoji} КБП-7 (Ил-76 МД-М):: {ex7_md_m} ({status})\n"
    
    # КБП-4 (Ил-76 МД-90А)
    ex4_md_90a = user[11]
    if ex4_md_90a:
        emoji, status, _ = get_date_status(ex4_md_90a, EXERCISE_4_PERIOD)
        text += f"{emoji} КБП-4 (Ил-76 МД-90А):: {ex4_md_90a} ({status})\n"
    
    # КБП-7 (Ил-76 МД-90А)
    ex7_md_90a = user[12]
    if ex7_md_90a:
        emoji, status, _ = get_date_status(ex7_md_90a, EXERCISE_7_PERIOD)
        text += f"{emoji} КБП-7 (Ил-76 МД-90А):: {ex7_md_90a} ({status})\n"
    
    # Прыжки с парашютом
    parachute = user[13]
    if parachute and parachute.lower() not in ['освобожден', 'освобождён', 'осв']:
        emoji, status, _ = get_date_status(parachute, PARACHUTE_PERIOD)
        text += f"{emoji} Прыжки с ПДС:: {parachute} ({status})\n"
    else:
        text += f"⚪ Прыжки с парашютом: Освобожден\n"
    
    return text
