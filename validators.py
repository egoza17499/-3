from datetime import datetime
from config import DATE_FORMAT, WARNING_PERIOD

def is_valid_date(date_string):
    try:
        datetime.strptime(date_string, DATE_FORMAT)
        return True
    except ValueError:
        return False

def calculate_days_remaining(date_string):
    try:
        date_obj = datetime.strptime(date_string, DATE_FORMAT)
        today = datetime.now()
        delta = date_obj - today
        return delta.days
    except ValueError:
        return -1

def get_status_color(days_remaining):
    if days_remaining > WARNING_PERIOD:
        return "🟢"
    elif days_remaining > 0:
        return "🟡"
    else:
        return "🔴"

def check_parameter_status(param_name, date_string):
    if not date_string:
        return "🔴 Не указано"
    if not is_valid_date(date_string):
        return "🔴 Некорректная дата"
    days = calculate_days_remaining(date_string)
    color = get_status_color(days)
    if days < 0:
        return f"{color} Истекло {abs(days)} дней назад"
    elif days == 0:
        return f"{color} Истекает сегодня"
    else:
        return f"{color} {days} дней"