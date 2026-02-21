from datetime import datetime, timedelta
from config import (
    VLK_PERIOD, UMO_PERIOD, EXERCISE_4_PERIOD, 
    EXERCISE_7_PERIOD, LEAVE_PERIOD, PARACHUTE_PERIOD,
    WARNING_PERIOD, DATE_FORMAT
)
import re

def parse_date_auto(date_str: str):
    if not date_str:
        return None
    
    date_str = str(date_str).strip()
    
    освобожден_words = [
        'освобожден', 'освобождён', 'осв', 'освобождение',
        'не требуется', 'не нужно', 'нет', '-', ''
    ]
    
    if date_str.lower() in освобожден_words:
        return None
    
    clean_date = re.sub(r'[^\d]', '', date_str)
    
    if len(clean_date) == 6:
        day = int(clean_date[0:2])
        month = int(clean_date[2:4])
        year_short = int(clean_date[4:6])
        
        if year_short < 50:
            year = 2000 + year_short
        else:
            year = 1900 + year_short
        
        try:
            return datetime(year, month, day)
        except ValueError:
            return None
    
    elif len(clean_date) == 8:
        day = int(clean_date[0:2])
        month = int(clean_date[2:4])
        year = int(clean_date[4:8])
        
        try:
            return datetime(year, month, day)
        except ValueError:
            return None
    
    formats = [
        '%d.%m.%Y',
        '%d.%m.%y',
        '%d-%m-%Y',
        '%d-%m-%y',
    ]
    
    for fmt in formats:
        try:
            parsed = datetime.strptime(date_str, fmt)
            if parsed.year < 100:
                if parsed.year < 50:
                    parsed = parsed.replace(year=2000 + parsed.year)
                else:
                    parsed = parsed.replace(year=1900 + parsed.year)
            return parsed
        except ValueError:
            continue
    
    return None

def is_valid_date(date_str: str) -> bool:
    return parse_date_auto(date_str) is not None

def parse_date(date_str: str):
    if not date_str:
        return None
    
    date_str = str(date_str).strip()
    
    освобожден_words = [
        'освобожден', 'освобождён', 'осв', 'освобождение',
        'не требуется', 'не нужно', 'нет', '-', ''
    ]
    
    if date_str.lower() in освобожден_words:
        return None
    
    return parse_date_auto(date_str)

def format_date(date: datetime) -> str:
    if not date:
        return "Не указано"
    return date.strftime("%d.%m.%Y")

def get_date_status(date_str: str, period_days: int, reference_date=None):
    if not date_str:
        return '⚪', 'Не указано', 0
    
    date = parse_date(date_str)
    if not date:
        return '⚪', 'Не указано', 0
    
    now = reference_date if reference_date else datetime.now()
    expiry_date = date + timedelta(days=period_days)
    days_until_expiry = (expiry_date - now).days
    
    if days_until_expiry < 0:
        days_overdue = abs(days_until_expiry)
        return '🔴', f'Просрочено на {days_overdue} дн.', -days_overdue
    elif days_until_expiry <= WARNING_PERIOD:
        return '🟡', f'Действует (осталось {days_until_expiry} дн.)', days_until_expiry
    else:
        return '🟢', f'Действует (осталось {days_until_expiry} дн.)', days_until_expiry

def check_date_warnings(user: tuple):
    """
    Проверка предупреждений (30 дней)
    Возвращает: (warning_list, ban_list)
    """
    warnings = []  # Желтые предупреждения (30 дней)
    bans = []      # Красные запреты (истекло)
    
    now = datetime.now()
    
    # Отпуск (конец) - 365 дней
    leave_end = user[7]
    if leave_end:
        leave_date = parse_date(leave_end)
        if leave_date:
            expiry = leave_date + timedelta(days=365)
            days_left = (expiry - now).days
            if days_left < 0:
                bans.append(f"Отпуск истёк")
            elif days_left <= 30:
                warnings.append(f"Отпуск (осталось {days_left} дн.)")
    
    # ВЛК - 180 дней
    vlk_date = user[8]
    if vlk_date:
        vlk_parsed = parse_date(vlk_date)
        if vlk_parsed:
            vlk_expiry = vlk_parsed + timedelta(days=180)
            days_left = (vlk_expiry - now).days
            if days_left < 0:
                bans.append(f"ВЛК истекло")
            elif days_left <= 30:
                warnings.append(f"ВЛК (осталось {days_left} дн.)")
    
    # УМО - 365 дней от ВЛК
    umo_date = user[9]
    if umo_date and umo_date.lower() not in ['нет', 'освобожден', 'осв', 'не требуется']:
        umo_parsed = parse_date(umo_date)
        if umo_parsed and user[8]:
            vlk_parsed = parse_date(user[8])
            if vlk_parsed:
                umo_expiry = vlk_parsed + timedelta(days=365)
                days_left = (umo_expiry - now).days
                if days_left < 0:
                    bans.append(f"УМО истекло")
                elif days_left <= 30:
                    warnings.append(f"УМО (осталось {days_left} дн.)")
    
    # КБП-4 МД-М - 180 дней
    ex4_md_m = user[10]
    if ex4_md_m:
        ex4_parsed = parse_date(ex4_md_m)
        if ex4_parsed:
            ex4_expiry = ex4_parsed + timedelta(days=EXERCISE_4_PERIOD)
            days_left = (ex4_expiry - now).days
            if days_left < 0:
                bans.append(f"КБП-4 (МД-М) истекло")
            elif days_left <= 30:
                warnings.append(f"КБП-4 (МД-М) (осталось {days_left} дн.)")
    
    # КБП-7 МД-М - 360 дней
    ex7_md_m = user[11]
    if ex7_md_m:
        ex7_parsed = parse_date(ex7_md_m)
        if ex7_parsed:
            ex7_expiry = ex7_parsed + timedelta(days=EXERCISE_7_PERIOD)
            days_left = (ex7_expiry - now).days
            if days_left < 0:
                bans.append(f"КБП-7 (МД-М) истекло")
            elif days_left <= 30:
                warnings.append(f"КБП-7 (МД-М) (осталось {days_left} дн.)")
    
    # КБП-4 МД-90А - 180 дней
    ex4_md_90a = user[12]
    if ex4_md_90a:
        ex4_parsed = parse_date(ex4_md_90a)
        if ex4_parsed:
            ex4_expiry = ex4_parsed + timedelta(days=EXERCISE_4_PERIOD)
            days_left = (ex4_expiry - now).days
            if days_left < 0:
                bans.append(f"КБП-4 (МД-90А) истекло")
            elif days_left <= 30:
                warnings.append(f"КБП-4 (МД-90А) (осталось {days_left} дн.)")
    
    # КБП-7 МД-90А - 360 дней
    ex7_md_90a = user[13]
    if ex7_md_90a:
        ex7_parsed = parse_date(ex7_md_90a)
        if ex7_parsed:
            ex7_expiry = ex7_parsed + timedelta(days=EXERCISE_7_PERIOD)
            days_left = (ex7_expiry - now).days
            if days_left < 0:
                bans.append(f"КБП-7 (МД-90А) истекло")
            elif days_left <= 30:
                warnings.append(f"КБП-7 (МД-90А) (осталось {days_left} дн.)")
    
    return warnings, bans

def check_flight_ban(user: tuple) -> list:
    """Проверка запретов на полёты"""
    _, bans = check_date_warnings(user)
    return bans

def generate_profile_text(user: tuple) -> str:
    fio = user[3] or "Не указано"
    rank = user[4] or "Не указано"
    qualification = user[5] or "Не указано"
    
    text = f"👤 {fio}\n"
    text += f"🎖 Воинское звание: {rank}\n"
    text += f"🏅 Квалификация: {qualification}\n\n"
    
    now = datetime.now()
    
    leave_end = user[7]
    if leave_end:
        leave_date = parse_date(leave_end)
        if leave_date:
            expiry = leave_date + timedelta(days=365)
            days_left = (expiry - now).days
            formatted_date = format_date(leave_date)
            if days_left < 0:
                text += f"🔴 Отпуск (конец):: {formatted_date} (Просрочено на {abs(days_left)} дн.)\n"
            else:
                text += f"🟢 Отпуск (конец):: {formatted_date} (Действует (осталось {days_left} дн.))\n"
        else:
            text += f"⚪ Отпуск (конец):: {leave_end}\n"
    else:
        text += f"⚪ Отпуск (конец):: Не указан\n"
    
    vlk_date = user[8]
    if vlk_date:
        vlk_parsed = parse_date(vlk_date)
        if vlk_parsed:
            vlk_expiry = vlk_parsed + timedelta(days=180)
            days_left = (vlk_expiry - now).days
            formatted_date = format_date(vlk_parsed)
            if days_left < 0:
                text += f"🔴 ВЛК: {formatted_date} (Просрочено на {abs(days_left)} дн.)\n"
            else:
                text += f"🟢 ВЛК: {formatted_date} (Действует, осталось {days_left} дн.)\n"
        else:
            text += f"⚪ ВЛК: {vlk_date}\n"
    else:
        text += f"⚪ ВЛК: Не указана\n"
    
    umo_date = user[9]
    if umo_date and umo_date.lower() not in ['нет', 'освобожден', 'осв', 'не требуется']:
        umo_parsed = parse_date(umo_date)
        if umo_parsed and user[8]:
            vlk_parsed = parse_date(user[8])
            if vlk_parsed:
                umo_expiry = vlk_parsed + timedelta(days=365)
                days_left = (umo_expiry - now).days
                formatted_date = format_date(umo_parsed)
                if days_left < 0:
                    text += f"🔴 УМО:: {formatted_date} (Просрочено на {abs(days_left)} дн.)\n"
                else:
                    text += f"🟢 УМО:: {formatted_date} (Действует, осталось {days_left} дн.)\n"
        else:
            text += f"⚪ УМО:: {umo_date}\n"
    else:
        text += f"⚪ УМО:: Не указано\n"
    
    ex4_md_m = user[10]
    if ex4_md_m:
        ex4_parsed = parse_date(ex4_md_m)
        if ex4_parsed:
            ex4_expiry = ex4_parsed + timedelta(days=EXERCISE_4_PERIOD)
            days_left = (ex4_expiry - now).days
            formatted_date = format_date(ex4_parsed)
            if days_left < 0:
                text += f"🔴 КБП-4 (Ил-76 МД-М):: {formatted_date} (Просрочено на {abs(days_left)} дн.)\n"
            else:
                text += f"🟢 КБП-4 (Ил-76 МД-М):: {formatted_date} (Действует (осталось {days_left} дн.))\n"
    
    ex7_md_m = user[11]
    if ex7_md_m:
        ex7_parsed = parse_date(ex7_md_m)
        if ex7_parsed:
            ex7_expiry = ex7_parsed + timedelta(days=EXERCISE_7_PERIOD)
            days_left = (ex7_expiry - now).days
            formatted_date = format_date(ex7_parsed)
            if days_left < 0:
                text += f"🔴 КБП-7 (Ил-76 МД-М):: {formatted_date} (Просрочено на {abs(days_left)} дн.)\n"
            else:
                text += f"🟢 КБП-7 (Ил-76 МД-М):: {formatted_date} (Действует (осталось {days_left} дн.))\n"
    
    ex4_md_90a = user[12]
    if ex4_md_90a:
        ex4_parsed = parse_date(ex4_md_90a)
        if ex4_parsed:
            ex4_expiry = ex4_parsed + timedelta(days=EXERCISE_4_PERIOD)
            days_left = (ex4_expiry - now).days
            formatted_date = format_date(ex4_parsed)
            if days_left < 0:
                text += f"🔴 КБП-4 (Ил-76 МД-90А):: {formatted_date} (Просрочено на {abs(days_left)} дн.)\n"
            else:
                text += f"🟢 КБП-4 (Ил-76 МД-90А):: {formatted_date} (Действует (осталось {days_left} дн.))\n"
    
    ex7_md_90a = user[13]
    if ex7_md_90a:
        ex7_parsed = parse_date(ex7_md_90a)
        if ex7_parsed:
            ex7_expiry = ex7_parsed + timedelta(days=EXERCISE_7_PERIOD)
            days_left = (ex7_expiry - now).days
            formatted_date = format_date(ex7_parsed)
            if days_left < 0:
                text += f"🔴 КБП-7 (Ил-76 МД-90А):: {formatted_date} (Просрочено на {abs(days_left)} дн.)\n"
            else:
                text += f"🟢 КБП-7 (Ил-76 МД-90А):: {formatted_date} (Действует (осталось {days_left} дн.))\n"
    
    parachute = user[14]
    if parachute:
        parachute_lower = parachute.lower().strip()
        if parachute_lower in ['освобожден', 'освобождён', 'осв', 'освобождение', 'не требуется', 'нет', '-']:
            text += f"⚪ Прыжки с парашютом: Освобожден\n"
        else:
            parachute_parsed = parse_date(parachute)
            if parachute_parsed:
                parachute_expiry = parachute_parsed + timedelta(days=PARACHUTE_PERIOD)
                days_left = (parachute_expiry - now).days
                formatted_date = format_date(parachute_parsed)
                if days_left < 0:
                    text += f"🔴 Прыжки с парашютом:: {formatted_date} (Просрочено на {abs(days_left)} дн.)\n"
                else:
                    text += f"🟢 Прыжки с парашютом:: {formatted_date} (Действует (осталось {days_left} дн.))\n"
            else:
                text += f"⚪ Прыжки с парашютом: {parachute}\n"
    else:
        text += f"⚪ Прыжки с парашютом: Не указаны\n"
    
    return text
