#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📋 states.py — Состояния FSM для бота
✅ Все необходимые состояния для регистрации, поиска, админ-функций
"""

from aiogram.fsm.state import State, StatesGroup

# ============================================================
# СОСТОЯНИЯ ДЛЯ РЕГИСТРАЦИИ ПОЛЬЗОВАТЕЛЯ
# ============================================================

class RegistrationState(StatesGroup):
    """Состояния пошаговой регистрации пользователя"""
    fio = State()                    # ФИО
    rank = State()                   # Звание
    qualification = State()          # Квалификация
    leave_start_date = State()       # Дата начала отпуска
    leave_end_date = State()         # Дата конца отпуска
    vlk_date = State()               # Дата ВЛК
    umo_date = State()               # Дата УМО
    exercise_4_md_m_date = State()   # КБП-4 МД-М
    exercise_7_md_m_date = State()   # КБП-7 МД-М
    exercise_4_md_90a_date = State() # КБП-4 МД-90А
    exercise_7_md_90a_date = State() # КБП-7 МД-90А
    parachute_jump_date = State()    # Дата парашютного прыжка


# ============================================================
# СОСТОЯНИЯ ДЛЯ ПОЛЕЗНОЙ ИНФОРМАЦИИ (ПОЛЬЗОВАТЕЛЬ)
# ============================================================

class KnowledgeState(StatesGroup):
    """Состояния для поиска полезной информации"""
    # Аэродромы
    aerodrome_search = State()
    
    # Блоки безопасности
    safety_block_search = State()
    
    # Знания по самолётам
    aircraft_search = State()


# ============================================================
# СОСТОЯНИЯ ДЛЯ РЕДАКТИРОВАНИЯ АЭРОДРОМА (АДМИН)
# ============================================================

class EditAerodromeState(StatesGroup):
    """Состояния для редактирования данных аэродрома"""
    add_phone_name = State()        # Название телефона (АДП, Диспетчер...)
    add_phone_number = State()      # Номер телефона
    change_phone_number = State()   # Изменение существующего номера
    change_housing = State()        # Изменение информации о жилье
    add_doc_name = State()          # Название документа
    add_doc_file = State()          # Файл документа


# ============================================================
# СОСТОЯНИЯ ДЛЯ АДМИНИСТРАТИВНЫХ КОМАНД
# ============================================================

class AdminState(StatesGroup):
    """Состояния для административных функций"""
    waiting_for_admin_id = State()      # Ввод ID для добавления/удаления админа
    waiting_for_user_search = State()   # Поиск пользователя для редактирования
    editing_user_field = State()        # Редактирование поля пользователя
    waiting_for_field_value = State()   # Ввод нового значения поля


# ============================================================
# ✅ НОВЫЙ КЛАСС: АДМИН — УПРАВЛЕНИЕ БАЗОЙ ЗНАНИЙ
# ============================================================

class AdminKnowledgeState(StatesGroup):
    """
    Состояния для управления базой знаний (админ)
    ✅ Добавление/редактирование аэродромов, блоков, знаний о самолётах
    """
    
    # === АЭРОДРОМЫ ===
    aero_add_name = State()           # Название города/аэродрома
    aero_add_city = State()           # Город
    aero_add_airport = State()        # Название аэропорта
    aero_add_housing = State()        # Информация о жилье
    aero_add_phone_name = State()     # Название телефона
    aero_add_phone_number = State()   # Номер телефона
    aero_add_doc_name = State()       # Название документа
    aero_add_doc_file = State()       # Файл документа
    
    # === БЛОКИ БЕЗОПАСНОСТИ ===
    safety_add_number = State()       # Номер блока
    safety_add_text = State()         # Текст блока
    
    # === ЗНАНИЯ ПО САМОЛЁТАМ ===
    aircraft_add_type = State()       # Тип самолёта (Ил-76МД, МД-М, МД-90А)
    aircraft_add_name = State()       # Название материала
    aircraft_add_text = State()       # Текст материала
    aircraft_add_file = State()       # Файл материала
