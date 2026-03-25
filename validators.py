from datetime import datetime, timedelta
from config import (
    VLK_PERIOD, UMO_PERIOD, EXERCISE_4_PERIOD,
    EXERCISE_7_PERIOD, LEAVE_PERIOD, PARACHUTE_PERIOD,
    WARNING_PERIOD, DATE_FORMAT
)
import re

# =====================================================================
# ВАЖНО: user везде — это dict (словарь), ключи — имена колонок БД
# Пример: user['fio'], user['vlk_date'], user['parachute_jump_date']
# =====================================================================

def parse_date_auto(date_str: str):
    if not date_str:
        return None
    date_str = str(date_str).strip()

    freed_words = [
        'освобожден', 'освобождён', 'осв', 'освобождение',
        'не требуется', 'не нужно', 'нет', '-', ''
    ]
    if date_str.lower() in freed_words:
        return None

    clean_date = re.sub(r'[^\d]', '', date_str)

    if len(clean_date) == 6:
        day = int(clean_date[0:2])
        month = int(clean_date[2:4])
        year_short = int(clean_date[4:6])
        year = 2000 + year_short if year_short < 50 else 1900 + year_short
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

    for fmt in ['%d.%m.%Y', '%d.%m.%y', '%d-%m-%Y', '%d-%m-%y']:
        try:
            parsed = datetime.strptime(date_str, fmt)
            if parsed.year < 100:
                parsed = parsed.replace(year=2000 + parsed.year if parsed.year < 50 else 1900 + parsed.year)
            return parsed
        except ValueError:
            continue

    return None


def parse_date(date_str):
    """Принимает str или datetime, возвращает datetime или None"""
    if not date_str:
        return None
    # Если уже datetime — возвращаем как есть
    if isinstance(date_str, datetime):
        return date_str

    date_str = str(date_str).strip()
    freed_words = [
        'освобожден', 'освобождён', 'осв', 'освобождение',
        'не требуется', 'не нужно', 'нет', '-', ''
    ]
    if date_str.lower() in freed_words:
        return None
    return parse_date_auto(date_str)


def is_valid_date(date_str: str) -> bool:
    return parse_date_auto(date_str) is not None


def format_date(date: datetime) -> str:
    if not date:
        return "Не указано"
    return date.strftime("%d.%m.%Y")


def _safe_str(val) -> str:
    """Безопасно преобразует значение поля в строку для проверки"""
    if val is None:
        return ''
    return str(val).strip()


def get_vlk_status_with_umo(user: dict):
    """
    Специальная логика для ВЛК с учётом УМО.
    user — словарь с ключами vlk_date, umo_date и т.д.
    Возвращает: (emoji, status_text, days_left, needs_umo_warning)
    """
    vlk_date_str = _safe_str(user.get('vlk_date'))
    umo_date_str = _safe_str(user.get('umo_date'))
    now = datetime.now()

    if not vlk_date_str:
        return '⚪', 'Не указана', 0, False

    vlk_date = parse_date(vlk_date_str)
    if not vlk_date:
        return '⚪', 'Не указана', 0, False

    freed_words = ['нет', 'освобожден', 'освобождён', 'осв', 'не требуется']
    umo_date = None
    if umo_date_str and umo_date_str.lower() not in freed_words:
        umo_date = parse_date(umo_date_str)

    vlk_6months = vlk_date + timedelta(days=180)
    vlk_12months = vlk_date + timedelta(days=365)
    days_until_6months = (vlk_6months - now).days
    days_until_12months = (vlk_12months - now).days

    if umo_date:
        umo_deadline = vlk_date + timedelta(days=365)
        if umo_date <= umo_deadline:
            if days_until_12months < 0:
                return '🔴', f'Просрочено на {abs(days_until_12months)} дн.', days_until_12months, False
            elif days_until_12months <= 30:
                return '🟡', f'Действует (осталось {days_until_12months} дн.)', days_until_12months, False
            else:
                return '🟢', f'Действует (осталось {days_until_12months} дн.)', days_until_12months, False

    # УМО не пройдено
    if days_until_6months < 0:
        return '🔴', f'Просрочено на {abs(days_until_6months)} дн.', days_until_6months, True
    elif days_until_6months <= 30:
        return '🟡', f'Действует (осталось {days_until_6months} дн.)', days_until_6months, True
    else:
        needs_umo_warn = days_until_6months <= 60
        return '🟢', f'Действует (осталось {days_until_6months} дн.)', days_until_6months, needs_umo_warn


def get_date_status(date_str, period_days: int, reference_date=None):
    if not date_str:
        return '⚪', 'Не указано', 0
    date = parse_date(date_str)
    if not date:
        return '⚪', 'Не указано', 0

    now = reference_date if reference_date else datetime.now()
    expiry_date = date + timedelta(days=period_days)
    days_until_expiry = (expiry_date - now).days

    if days_until_expiry < 0:
        return '🔴', f'Просрочено на {abs(days_until_expiry)} дн.', -abs(days_until_expiry)
    elif days_until_expiry <= WARNING_PERIOD:
        return '🟡', f'Действует (осталось {days_until_expiry} дн.)', days_until_expiry
    else:
        return '🟢', f'Действует (осталось {days_until_expiry} дн.)', days_until_expiry


def check_date_warnings(user: dict):
    """
    Проверка предупреждений.
    user — dict с ключами колонок БД.
    Возвращает: (warnings_list, bans_list)
    """
    warnings = []
    bans = []
    now = datetime.now()
    freed_words = ['нет', 'освобожден', 'освобождён', 'осв', 'не требуется']

    # Отпуск (конец)
    leave_end = _safe_str(user.get('leave_end_date'))
    if leave_end:
        leave_date = parse_date(leave_end)
        if leave_date:
            expiry = leave_date + timedelta(days=365)
            days_left = (expiry - now).days
            if days_left < 0:
                bans.append("Отпуск истёк")
            elif days_left <= 30:
                warnings.append(f"Отпуск (осталось {days_left} дн.)")

    # ВЛК + УМО
    vlk_emoji, vlk_status, vlk_days, needs_umo = get_vlk_status_with_umo(user)
    if vlk_emoji == '🔴':
        bans.append("ВЛК истекло")
    elif vlk_emoji == '🟡':
        if needs_umo:
            warnings.append(f"ВЛК (осталось {vlk_days} дн.) — необходимо пройти УМО")
        else:
            warnings.append(f"ВЛК (осталось {vlk_days} дн.)")

    # УМО отдельная проверка
    umo_date_str = _safe_str(user.get('umo_date'))
    vlk_date_str = _safe_str(user.get('vlk_date'))
    if umo_date_str and umo_date_str.lower() not in freed_words:
        umo_parsed = parse_date(umo_date_str)
        vlk_date = parse_date(vlk_date_str) if vlk_date_str else None
        if umo_parsed and vlk_date:
            umo_deadline = vlk_date + timedelta(days=365)
            days_until_deadline = (umo_deadline - now).days
            if now > umo_deadline:
                bans.append("УМО не пройдено (срок истёк)")
            elif days_until_deadline <= 30 and vlk_days > 180:
                warnings.append(f"УМО (срок пройти до {format_date(umo_deadline)})")

    # КБП-4 МД-М
    ex4_md_m = _safe_str(user.get('exercise_4_md_m_date'))
    if ex4_md_m:
        ex4_parsed = parse_date(ex4_md_m)
        if ex4_parsed:
            days_left = ((ex4_parsed + timedelta(days=EXERCISE_4_PERIOD)) - now).days
            if days_left < 0:
                bans.append("КБП-4 (МД-М) истекло")
            elif days_left <= 30:
                warnings.append(f"КБП-4 (МД-М) (осталось {days_left} дн.)")

    # КБП-7 МД-М
    ex7_md_m = _safe_str(user.get('exercise_7_md_m_date'))
    if ex7_md_m:
        ex7_parsed = parse_date(ex7_md_m)
        if ex7_parsed:
            days_left = ((ex7_parsed + timedelta(days=EXERCISE_7_PERIOD)) - now).days
            if days_left < 0:
                bans.append("КБП-7 (МД-М) истекло")
            elif days_left <= 30:
                warnings.append(f"КБП-7 (МД-М) (осталось {days_left} дн.)")

    # КБП-4 МД-90А
    ex4_md_90a = _safe_str(user.get('exercise_4_md_90a_date'))
    if ex4_md_90a:
        ex4_parsed = parse_date(ex4_md_90a)
        if ex4_parsed:
            days_left = ((ex4_parsed + timedelta(days=EXERCISE_4_PERIOD)) - now).days
            if days_left < 0:
                bans.append("КБП-4 (МД-90А) истекло")
            elif days_left <= 30:
                warnings.append(f"КБП-4 (МД-90А) (осталось {days_left} дн.)")

    # КБП-7 МД-90А
    ex7_md_90a = _safe_str(user.get('exercise_7_md_90a_date'))
    if ex7_md_90a:
        ex7_parsed = parse_date(ex7_md_90a)
        if ex7_parsed:
            days_left = ((ex7_parsed + timedelta(days=EXERCISE_7_PERIOD)) - now).days
            if days_left < 0:
                bans.append("КБП-7 (МД-90А) истекло")
            elif days_left <= 30:
                warnings.append(f"КБП-7 (МД-90А) (осталось {days_left} дн.)")

    return warnings, bans


def check_flight_ban(user: dict) -> list:
    """Проверка запретов на полёты. Возвращает список причин запрета."""
    _, bans = check_date_warnings(user)
    return bans


def generate_profile_text(user: dict) -> str:
    """Генерация текста профиля. user — dict."""
    fio = user.get('fio') or "Не указано"
    rank = user.get('rank') or "Не указано"
    qualification = user.get('qualification') or "Не указано"
    freed_words = ['нет', 'освобожден', 'освобождён', 'осв', 'не требуется']

    text = f"👤 {fio}\n"
    text += f"🎖 Воинское звание: {rank}\n"
    text += f"🏅 Квалификация: {qualification}\n\n"

    now = datetime.now()

    # Отпуск (конец)
    leave_end = _safe_str(user.get('leave_end_date'))
    if leave_end:
        leave_date = parse_date(leave_end)
        if leave_date:
            expiry = leave_date + timedelta(days=365)
            days_left = (expiry - now).days
            formatted_date = format_date(leave_date)
            if days_left < 0:
                text += f"🔴 Отпуск (конец): {formatted_date} (Просрочено на {abs(days_left)} дн.)\n"
            else:
                text += f"🟢 Отпуск (конец): {formatted_date} (Действует, осталось {days_left} дн.)\n"
        else:
            text += f"⚪ Отпуск (конец): {leave_end}\n"
    else:
        text += f"⚪ Отпуск (конец): Не указан\n"

    # ВЛК
    vlk_emoji, vlk_status, vlk_days, needs_umo = get_vlk_status_with_umo(user)
    vlk_date_str = _safe_str(user.get('vlk_date'))
    if vlk_date_str:
        vlk_parsed = parse_date(vlk_date_str)
        if vlk_parsed:
            formatted_date = format_date(vlk_parsed)
            text += f"{vlk_emoji} ВЛК: {formatted_date} ({vlk_status})"
            if needs_umo and vlk_days > 0:
                text += " ⚠️ <b>необходимо пройти УМО</b>"
            text += "\n"
        else:
            text += f"⚪ ВЛК: {vlk_date_str}\n"
    else:
        text += f"⚪ ВЛК: Не указана\n"

    # УМО
    umo_date_str = _safe_str(user.get('umo_date'))
    if umo_date_str and umo_date_str.lower() not in freed_words:
        umo_parsed = parse_date(umo_date_str)
        vlk_date_parsed = parse_date(vlk_date_str) if vlk_date_str else None
        if umo_parsed and vlk_date_parsed:
            umo_deadline = vlk_date_parsed + timedelta(days=365)
            days_until_deadline = (umo_deadline - now).days
            formatted_date = format_date(umo_parsed)
            if now > umo_deadline:
                text += f"🔴 УМО: {formatted_date} (Срок прошёл {abs(days_until_deadline)} дн. назад)\n"
            elif days_until_deadline <= 30:
                text += f"🟡 УМО: {formatted_date} (Срок пройти до {format_date(umo_deadline)})\n"
            else:
                text += f"🟢 УМО: {formatted_date} (Пройдено, ВЛК продлена до {format_date(umo_deadline)})\n"
        else:
            text += f"⚪ УМО: {umo_date_str}\n"
    else:
        text += f"⚪ УМО: Не указано\n"

    # КБП-4 (Ил-76 МД-М)
    ex4_md_m = _safe_str(user.get('exercise_4_md_m_date'))
    if ex4_md_m:
        ex4_parsed = parse_date(ex4_md_m)
        if ex4_parsed:
            ex4_expiry = ex4_parsed + timedelta(days=EXERCISE_4_PERIOD)
            days_left = (ex4_expiry - now).days
            formatted_date = format_date(ex4_parsed)
            if days_left < 0:
                text += f"🔴 КБП-4 (Ил-76 МД-М): {formatted_date} (Просрочено на {abs(days_left)} дн.)\n"
            elif days_left <= WARNING_PERIOD:
                text += f"🟡 КБП-4 (Ил-76 МД-М): {formatted_date} (Осталось {days_left} дн.)\n"
            else:
                text += f"🟢 КБП-4 (Ил-76 МД-М): {formatted_date} (Действует, осталось {days_left} дн.)\n"

    # КБП-7 (Ил-76 МД-М)
    ex7_md_m = _safe_str(user.get('exercise_7_md_m_date'))
    if ex7_md_m:
        ex7_parsed = parse_date(ex7_md_m)
        if ex7_parsed:
            ex7_expiry = ex7_parsed + timedelta(days=EXERCISE_7_PERIOD)
            days_left = (ex7_expiry - now).days
            formatted_date = format_date(ex7_parsed)
            if days_left < 0:
                text += f"🔴 КБП-7 (Ил-76 МД-М): {formatted_date} (Просрочено на {abs(days_left)} дн.)\n"
            elif days_left <= WARNING_PERIOD:
                text += f"🟡 КБП-7 (Ил-76 МД-М): {formatted_date} (Осталось {days_left} дн.)\n"
            else:
                text += f"🟢 КБП-7 (Ил-76 МД-М): {formatted_date} (Действует, осталось {days_left} дн.)\n"

    # КБП-4 (Ил-76 МД-90А)
    ex4_md_90a = _safe_str(user.get('exercise_4_md_90a_date'))
    if ex4_md_90a:
        ex4_parsed = parse_date(ex4_md_90a)
        if ex4_parsed:
            ex4_expiry = ex4_parsed + timedelta(days=EXERCISE_4_PERIOD)
            days_left = (ex4_expiry - now).days
            formatted_date = format_date(ex4_parsed)
            if days_left < 0:
                text += f"🔴 КБП-4 (Ил-76 МД-90А): {formatted_date} (Просрочено на {abs(days_left)} дн.)\n"
            elif days_left <= WARNING_PERIOD:
                text += f"🟡 КБП-4 (Ил-76 МД-90А): {formatted_date} (Осталось {days_left} дн.)\n"
            else:
                text += f"🟢 КБП-4 (Ил-76 МД-90А): {formatted_date} (Действует, осталось {days_left} дн.)\n"

    # КБП-7 (Ил-76 МД-90А)
    ex7_md_90a = _safe_str(user.get('exercise_7_md_90a_date'))
    if ex7_md_90a:
        ex7_parsed = parse_date(ex7_md_90a)
        if ex7_parsed:
            ex7_expiry = ex7_parsed + timedelta(days=EXERCISE_7_PERIOD)
            days_left = (ex7_expiry - now).days
            formatted_date = format_date(ex7_parsed)
            if days_left < 0:
                text += f"🔴 КБП-7 (Ил-76 МД-90А): {formatted_date} (Просрочено на {abs(days_left)} дн.)\n"
            elif days_left <= WARNING_PERIOD:
                text += f"🟡 КБП-7 (Ил-76 МД-90А): {formatted_date} (Осталось {days_left} дн.)\n"
            else:
                text += f"🟢 КБП-7 (Ил-76 МД-90А): {formatted_date} (Действует, осталось {days_left} дн.)\n"

    # Прыжки с парашютом
    parachute = _safe_str(user.get('parachute_jump_date'))
    if parachute:
        if parachute.lower() in freed_words + ['освобождение']:
            text += f"⚪ Прыжки с парашютом: Освобождён\n"
        else:
            parachute_parsed = parse_date(parachute)
            if parachute_parsed:
                parachute_expiry = parachute_parsed + timedelta(days=PARACHUTE_PERIOD)
                days_left = (parachute_expiry - now).days
                formatted_date = format_date(parachute_parsed)
                if days_left < 0:
                    text += f"🔴 Прыжки с парашютом: {formatted_date} (Просрочено на {abs(days_left)} дн.)\n"
                elif days_left <= WARNING_PERIOD:
                    text += f"🟡 Прыжки с парашютом: {formatted_date} (Осталось {days_left} дн.)\n"
                else:
                    text += f"🟢 Прыжки с парашютом: {formatted_date} (Действует, осталось {days_left} дн.)\n"
            else:
                text += f"⚪ Прыжки с парашютом: {parachute}\n"
    else:
        text += f"⚪ Прыжки с парашютом: Не указаны\n"

    return text
