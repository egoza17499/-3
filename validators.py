def is_valid_date(date_string):
    """
    Validate the date format YYYY-MM-DD.
    """
    from datetime import datetime
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def check_flight_permission(user_permissions):
    """
    Check if the user has permission to book flights.
    """
    required_permission = 'book_flights'
    return required_permission in user_permissions
