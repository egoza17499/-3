from datetime import datetime, timedelta
from config import (
    VLK_PERIOD, UMO_PERIOD, EXERCISE_4_PERIOD, 
    EXERCISE_7_PERIOD, LEAVE_PERIOD, PARACHUTE_PERIOD,
    WARNING_PERIOD, DATE_FORMAT
)
import re

def parse_date_auto(date_str: str):
    """
    Авто-распознавание дат в разных форматах:
    - 08.06.2025 или 08.06.25
    - 08-06-2025 или 08-06-25
    - 080625 или 08062025
    """
    if not date_str:
        return None
    
    date_str = str(date_str).strip()
    
    # Проверяем на "освобожден" и синонимы
    if date_str.lower() in ['освобожден', 'освобождён', 'осв', 'не требуется', '-', '']:
        return None
    
    # Список форматов для проверки
    formats = [
        '%d.%m.%Y',    # 08.06.2025
        '%d.%m.%y',    # 08.06.25
        '%d-%m-%Y',    # 08-06-2025
        '%d-%m-%y',    # 08-06-25
        '%d%m%y',      # 080625
        '%d%m%Y',      # 08062025
    ]
    
    # Очищаем строку от лишних символов для короткого формата
    clean_date = re.sub(r'[^\d]', '', date_str)
    
    for fmt in formats:
        try:
            # Для форматов без разделителей используем очищенную строку
            if fmt in ['%d%m%y', '%d%m%Y']:
                return datetime.strptime(clean_date, fmt)
            else:
                return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None

def is_valid_date(date_str: str) -> bool:
    """Проверка формата даты"""
    return parse_date_auto(date_str) is not None

def parse_date(date_str: str):
    """Парсинг даты"""
    if not date_str:
        return None
    
    date_str = str(date_str).strip()
    
    # Проверяем на освобожден и синонимы
    освобожден_words = [
        'освобожден', 'освобождён', 'осв', 'освобождение',
        'не требуется', 'не нужно', 'нет', '-', ''
    ]
    
    if date_str.lower() in освобожден_words:
        return None
    
    return parse_date_auto(date_str)

def get_date_status(date_str: str, period_days: int, reference_date=None):
    """
    Получение статуса даты
    reference_date - дата отсчёта (если None, то сегодня)
    Возвращает: (emoji, status_text, days_left_or_overdue)
    """
    if not date_str:
        return '⚪', 'Не указано', 0
    
    date = parse_date(date_str)
    if not date:
        return '⚪', 'Не указано', 0
    
    now = reference_date if reference_date else datetime.now()
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
    now = datetime.now()
    
    # Отпуск (конец) - проверяем от даты конца + 12 месяцев
    leave_end = user[6]
    if leave_end:
        leave_date = parse_date(leave_end)
        if leave_date:
            # 12 месяцев от даты конца отпуска
            expiry = leave_date + timedelta(days=365)
            if now > expiry:
                bans.append('Отпуск истёк')
    
    # ВЛК - 6 месяцев
    vlk_date = user[7]
    vlk_expired = False
    if vlk_date:
        vlk_parsed = parse_date(vlk_date)
        if vlk_parsed:
            # 6 месяцев от ВЛК
            vlk_expiry = vlk_parsed + timedelta(days=180)
            if now > vlk_expiry:
                vlk_expired = True
                bans.append('ВЛК истекло')
    
    # УМО - если не прошёл, то после 6 месяцев ВЛК полёты запрещены
    umo_date = user[8]
    if umo_date and umo_date.lower() not in ['нет', 'освобожден', 'осв', 'не требуется']:
        umo_parsed = parse_date(umo_date)
        if umo_parsed and vlk_date:
            # УМО пройден - 12 месяцев от даты ВЛК
            vlk_parsed = parse_date(vlk_date)
            if vlk_parsed:
                umo_expiry = vlk_parsed + timedelta(days=365)
                if now > umo_expiry:
                    if 'УМО истекло' not in bans:
                        bans.append('УМО истекло')
        elif not umo_parsed:
            # УМО не прошёл и ВЛК истекло - запрет
            if vlk_expired and 'УМО не пройдено' not in bans:
                bans.append('УМО не пройдено')
    elif umo_date and umo_date.lower() in ['нет', 'освобожден', 'осв', 'не требуется']:
        # УМО не требуется - проверяем только ВЛК (6 месяцев)
        if vlk_expired and 'УМО не пройдено' not in bans:
            bans.append('УМО не пройдено')
    
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
    """Генерация текста профиля"""
    
    fio = user[3] or "Не указано"
    rank = user[4] or "Не указано"
    qualification = user[5] or "Не указано"
    
    # Основные данные
    text = f"👤 {fio}\n"
    text += f"🎖 Воинское звание: {rank}\n"
    text += f"🏅 Квалификация: {qualification}\n\n"
    
    now = datetime.now()
    
    # Отпуск (конец) - 12 месяцев от даты конца
    leave_end = user[6]
    if leave_end:
        leave_date = parse_date(leave_end)
        if leave_date:
            # 12 месяцев от даты конца
            status, status_text, _ = get_date_status(leave_end, 365, leave_date)
            # Пересчитываем относительно сегодня
            expiry = leave_date + timedelta(days=365)
            days_left = (expiry - now).days
            if days_left < 0:
                text += f"🔴 Отпуск (конец):: {leave_end} (Просрочено на {abs(days_left)} дн.)\n"
            else:
                text += f"🟢 Отпуск (конец):: {leave_end} (Действует (осталось {days_left} дн.))\n"
        else:
            text += f"⚪ Отпуск (конец):: {leave_end}\n"
    else:
        text += f"⚪ Отпуск (конец):: Не указан\n"
    
    # ВЛК - 6 месяцев
    vlk_date = user[7]
    if vlk_date:
        vlk_parsed = parse_date(vlk_date)
        if vlk_parsed:
            vlk_expiry = vlk_parsed + timedelta(days=180)
            days_left = (vlk_expiry - now).days
            if days_left < 0:
                text += f"🔴 ВЛК: {vlk_date} (Просрочено на {abs(days_left)} дн.)\n"
            else:
                text += f"🟢 ВЛК: {vlk_date} (Действует, осталось {days_left} дн.)\n"
        else:
            text += f"⚪ ВЛК: {vlk_date}\n"
    else:
        text += f"⚪ ВЛК: Не указана\n"
    
    # УМО
    umo_date = user[8]
    if umo_date and umo_date.lower() not in ['нет', 'освобожден', 'осв', 'не требуется']:
        umo_parsed = parse_date(umo_date)
        if umo_parsed and user[7]:
            # УМО пройден - 12 месяцев от даты ВЛК
            vlk_parsed = parse_date(user[7])
            if vlk_parsed:
                umo_expiry = vlk_parsed + timedelta(days=365)
                days_left = (umo_expiry - now).days
                if days_left < 0:
                    text += f"🔴 УМО:: {umo_date} (Просрочено на {abs(days_left)} дн.)\n"
                else:
                    text += f"🟢 УМО:: {umo_date} (Действует, осталось {days_left} дн.)\n"
        else:
            text += f"⚪ УМО:: {umo_date}\n"
    else:
        text += f"⚪ УМО:: Не указано\n"
    
    # КБП-4 (Ил-76 МД-М)
    ex4_md_m = user[9]
    if ex4_md_m:
        ex4_parsed = parse_date(ex4_md_m)
        if ex4_parsed:
            ex4_expiry = ex4_parsed + timedelta(days=EXERCISE_4_PERIOD)
            days_left = (ex4_expiry - now).days
            if days_left < 0:
                text += f"🔴 КБП-4 (Ил-76 МД-М):: {ex4_md_m} (Просрочено на {abs(days_left)} дн.)\n"
            else:
                text += f"🟢 КБП-4 (Ил-76 МД-М):: {ex4_md_m} (Действует (осталось {days_left} дн.))\n"
    
    # КБП-7 (Ил-76 МД-М)
    ex7_md_m = user[10]
    if ex7_md_m:
        ex7_parsed = parse_date(ex7_md_m)
        if ex7_parsed:
            ex7_expiry = ex7_parsed + timedelta(days=EXERCISE_7_PERIOD)
            days_left = (ex7_expiry - now).days
            if days_left < 0:
                text += f"🔴 КБП-7 (Ил-76 МД-М):: {ex7_md_m} (Просрочено на {abs(days_left)} дн.)\n"
            else:
                text += f"🟢 КБП-7 (Ил-76 МД-М):: {ex7_md_m} (Действует (осталось {days_left} дн.))\n"
    
    # КБП-4 (Ил-76 МД-90А)
    ex4_md_90a = user[11]
    if ex4_md_90a:
        ex4_parsed = parse_date(ex4_md_90a)
        if ex4_parsed:
            ex4_expiry = ex4_parsed + timedelta(days=EXERCISE_4_PERIOD)
            days_left = (ex4_expiry - now).days
            if days_left < 0:
                text += f"🔴 КБП-4 (Ил-76 МД-90А):: {ex4_md_90a} (Просрочено на {abs(days_left)} дн.)\n"
            else:
                text += f"🟢 КБП-4 (Ил-76 МД-90А):: {ex4_md_90a} (Действует (осталось {days_left} дн.))\n"
    
    # КБП-7 (Ил-76 МД-90А)
    ex7_md_90a = user[12]
    if ex7_md_90a:
        ex7_parsed = parse_date(ex7_md_90a)
        if ex7_parsed:
            ex7_expiry = ex7_parsed + timedelta(days=EXERCISE_7_PERIOD)
            days_left = (ex7_expiry - now).days
            if days_left < 0:
                text += f"🔴 КБП-7 (Ил-76 МД-90А):: {ex7_md_90a} (Просрочено на {abs(days_left)} дн.)\n"
            else:
                text += f"🟢 КБП-7 (Ил-76 МД-90А):: {ex7_md_90a} (Действует (осталось {days_left} дн.))\n"
    
    # Прыжки с парашютом
    parachute = user[13]
    if parachute:
        parachute_lower = parachute.lower().strip()
        # Проверяем на освобожден и синонимы
        if parachute_lower in ['освобожден', 'освобождён', 'осв', 'освобождение', 'не требуется', 'нет', '-']:
            text += f"⚪ Прыжки с парашютом: Освобожден\n"
        else:
            parachute_parsed = parse_date(parachute)
            if parachute_parsed:
                parachute_expiry = parachute_parsed + timedelta(days=PARACHUTE_PERIOD)
                days_left = (parachute_expiry - now).days
                if days_left < 0:
                    text += f"🔴 Прыжки с парашютом:: {parachute} (Просрочено на {abs(days_left)} дн.)\n"
                else:
                    text += f"🟢 Прыжки с парашютом:: {parachute} (Действует (осталось {days_left} дн.))\n"
            else:
                text += f"⚪ Прыжки с парашютом: {parachute}\n"
    else:
        text += f"⚪ Прыжки с парашютом: Не указаны\n"
    
    return text
