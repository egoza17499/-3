from aiogram.fsm.state import State, StatesGroup

class KnowledgeState(StatesGroup):
    aerodrome_search = State()
    safety_block_search = State()
    aircraft_search = State()

class RegistrationState(StatesGroup):
    fio = State()
    rank = State()
    qualification = State()
