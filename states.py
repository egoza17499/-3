from aiogram.fsm.state import State, StatesGroup


# ============================================================
# СОСТОЯНИЯ ДЛЯ РЕГИСТРАЦИИ
# ============================================================

class RegistrationState(StatesGroup):
    fio = State()           # ФИО
    rank = State()          # Звание
    qualification = State() # Квалификация
    dates = State()         # Все даты (шаг хранится в data['date_step'])


# ============================================================
# СОСТОЯНИЯ ДЛЯ ПОЛЕЗНОЙ ИНФОРМАЦИИ
# ============================================================

class KnowledgeState(StatesGroup):
    aerodrome_search = State()   # Поиск аэродрома
    safety_block_search = State() # Поиск блока безопасности
    aircraft_search = State()    # Поиск знаний о самолёте


# ============================================================
# СОСТОЯНИЯ ДЛЯ РЕДАКТИРОВАНИЯ АЭРОДРОМА
# ============================================================

class EditAerodromeState(StatesGroup):
    add_phone_name = State()     # Название телефона (АДП, Диспетчер...)
    add_phone_number = State()   # Номер телефона
    change_phone_number = State() # Изменение существующего номера
    change_housing = State()     # Изменение информации о жилье


# ============================================================
# СОСТОЯНИЯ ДЛЯ АДМИНИСТРАТИВНЫХ КОМАНД
# ============================================================

class AdminState(StatesGroup):
    waiting_for_admin_id = State()      # Ввод ID для добавления/удаления админа
    waiting_for_user_search = State()   # Поиск пользователя для редактирования
    editing_user_field = State()        # Редактирование поля пользователя
    waiting_for_field_value = State()   # Ввод нового значения поля
