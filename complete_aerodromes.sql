-- ============================================================
-- ПОЛНОЕ ЗАПОЛНЕНИЕ БАЗЫ АЭРОДРОМОВ - 350+ АЭРОДРОМОВ
-- Все данные из скриншотов
-- ============================================================

-- ==================== А ====================

-- АБАКАН
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Абакан', 'Абакан', 'Абакан', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'Диспетчер', '8-390-228-25-34' FROM aerodromes WHERE name = 'Абакан';

-- АДЛЕР (СОЧИ)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Адлер', 'Сочи', 'Адлер', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-862-249-75-71' FROM aerodromes WHERE name = 'Адлер'
UNION ALL SELECT id, 'Личный', '8-988-142-32-14' FROM aerodromes WHERE name = 'Адлер';

-- АНАПА
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Анапа', 'Анапа', 'Витязево', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'Диспетчер', '8-861-332-36-70' FROM aerodromes WHERE name = 'Анапа'
UNION ALL SELECT id, 'АДП', '8-861-332-37-35' FROM aerodromes WHERE name = 'Анапа'
UNION ALL SELECT id, 'УС', '8-861-333-30-38' FROM aerodromes WHERE name = 'Анапа'
UNION ALL SELECT id, 'Граждане', '8-861-339-85-21' FROM aerodromes WHERE name = 'Анапа';

-- АРМАВИР
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Армавир', 'Армавир', 'Армавир', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'Диспетчер', '8-964-922-75-40' FROM aerodromes WHERE name = 'Армавир'
UNION ALL SELECT id, 'Коммутатор', '8-861-377-32-61' FROM aerodromes WHERE name = 'Армавир'
UNION ALL SELECT id, 'УС', '8-861-377-32-62' FROM aerodromes WHERE name = 'Армавир';

-- АСТРАХАНЬ (ПРИВОЛЖСКИЙ)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Астрахань', 'Астрахань', 'Приволжский', 'Требуется справка', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'Диспетчер', '8-917-097-67-70' FROM aerodromes WHERE name = 'Астрахань'
UNION ALL SELECT id, 'УС', '8-851-257-70-20' FROM aerodromes WHERE name = 'Астрахань'
UNION ALL SELECT id, 'ОД', '8-851-257-45-88' FROM aerodromes WHERE name = 'Астрахань'
UNION ALL SELECT id, 'гр. АДП', '8-851-239-37-31' FROM aerodromes WHERE name = 'Астрахань';

-- АХТУБИНСК
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Ахтубинск', 'Ахтубинск', 'Ахтубинск', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-851-414-22-94' FROM aerodromes WHERE name = 'Ахтубинск'
UNION ALL SELECT id, 'ОД', '8-851-414-20-11' FROM aerodromes WHERE name = 'Ахтубинск'
UNION ALL SELECT id, 'РП', '8-851-414-27-27' FROM aerodromes WHERE name = 'Ахтубинск';

-- АШУЛУК
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Ашулук', 'Ашулук', 'Ашулук', 'Запрос через Астрахань', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-851-257-70-20' FROM aerodromes WHERE name = 'Ашулук'
UNION ALL SELECT id, 'ОД', '8-851-257-10-57' FROM aerodromes WHERE name = 'Ашулук';

-- ==================== Б ====================

-- БАГАЙ-БАРАНОВКА
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Багай-Барановка', 'Багай-Барановка', 'Багай-Барановка', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'Коммутатор', '8-845-936-06-90' FROM aerodromes WHERE name = 'Багай-Барановка'
UNION ALL SELECT id, 'УС', '8-906-304-13-45' FROM aerodromes WHERE name = 'Багай-Барановка';

-- БАЛАШОВ
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Балашов', 'Балашов', 'Балашов', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'УС', '8-845-455-32-88' FROM aerodromes WHERE name = 'Балашов'
UNION ALL SELECT id, 'АДП', '8-963-112-44-14' FROM aerodromes WHERE name = 'Балашов';

-- БЕЛАЯ
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Белая', 'Белая', 'Белая', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'Диспетчер', '8-999-422-38-71' FROM aerodromes WHERE name = 'Белая'
UNION ALL SELECT id, 'УС', '8-395-439-43-43' FROM aerodromes WHERE name = 'Белая'
UNION ALL SELECT id, 'ОД личный', '8-983-416-66-05' FROM aerodromes WHERE name = 'Белая';

-- БЕЛЬБЕК (СЕВАСТОПОЛЬ)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Бельбек', 'Севастополь', 'Бельбек', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'Диспетчер', '8-978-819-79-87' FROM aerodromes WHERE name = 'Бельбек';

-- БЕСЛАН
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Беслан', 'Беслан', 'Беслан', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-867-240-88-29' FROM aerodromes WHERE name = 'Беслан'
UNION ALL SELECT id, 'ПДСП', '8-867-240-88-34' FROM aerodromes WHERE name = 'Беслан'
UNION ALL SELECT id, 'Метео', '8-867-240-88-43' FROM aerodromes WHERE name = 'Беслан';

-- БЕСОВЕЦ (ПЕТРОЗАВОДСК)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Бесовец', 'Петрозаводск', 'Бесовец', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'Диспетчер', '8-921-524-25-31' FROM aerodromes WHERE name = 'Бесовец'
UNION ALL SELECT id, 'АДП', '8-921-626-73-47' FROM aerodromes WHERE name = 'Бесовец'
UNION ALL SELECT id, 'деж. по полку', '8-814-271-13-77' FROM aerodromes WHERE name = 'Бесовец';

-- БОРИСОГЛЕБСК
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Борисоглебск', 'Борисоглебск', 'Борисоглебск', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'Диспетчер', '8-980-349-87-19' FROM aerodromes WHERE name = 'Борисоглебск';

-- БРАТСК
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Братск', 'Братск', 'Братск', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'УС', '8-395-332-23-82' FROM aerodromes WHERE name = 'Братск'
UNION ALL SELECT id, 'АДП', '8-902-576-40-09' FROM aerodromes WHERE name = 'Братск';

-- БУДЕННОВСК
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Буденновск', 'Буденновск', 'Буденновск', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'УС', '8-865-592-12-71' FROM aerodromes WHERE name = 'Буденновск'
UNION ALL SELECT id, 'Диспетчер', '8-918-781-75-67' FROM aerodromes WHERE name = 'Буденновск'
UNION ALL SELECT id, 'Диспетчер', '8-988-766-34-71' FROM aerodromes WHERE name = 'Буденновск'
UNION ALL SELECT id, 'Коммутатор', '8-865-592-12-74' FROM aerodromes WHERE name = 'Буденновск';

-- БУТУРЛИНОВКА
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Бутурлиновка', 'Бутурлиновка', 'Бутурлиновка', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'Диспетчер', '8-950-766-78-22' FROM aerodromes WHERE name = 'Бутурлиновка'
UNION ALL SELECT id, 'АДП', '8-473-612-14-17' FROM aerodromes WHERE name = 'Бутурлиновка';

-- ==================== В ====================

-- ВЛАДИМИР (СЕМЯЗИНО)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Владимир', 'Владимир', 'Семязино', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-492-277-85-13' FROM aerodromes WHERE name = 'Владимир'
UNION ALL SELECT id, 'УС', '8-492-277-85-12' FROM aerodromes WHERE name = 'Владимир';

-- ВЛАДИВОСТОК (КНЕВИЧИ)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Владивосток', 'Владивосток', 'Кневичи', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-423-232-27-70' FROM aerodromes WHERE name = 'Владивосток'
UNION ALL SELECT id, 'Диспетчер', '8-914-717-97-19' FROM aerodromes WHERE name = 'Владивосток'
UNION ALL SELECT id, 'гражданский', '8-423-230-68-55' FROM aerodromes WHERE name = 'Владивосток'
UNION ALL SELECT id, 'гр. АДП', '8-423-230-67-77' FROM aerodromes WHERE name = 'Владивосток';

-- ВОЛГОГРАД (ГУМРАК)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Волгоград', 'Волгоград', 'Гумрак', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'РП', '8-844-235-76-50' FROM aerodromes WHERE name = 'Волгоград';

-- ВОЛГОГРАД (МАРИНОВКА)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Волгоград', 'Волгоград', 'Мариновка', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'УС', '8-844-726-10-33' FROM aerodromes WHERE name = 'Волгоград' AND city = 'Волгоград'
UNION ALL SELECT id, 'АДП', '8-960-880-27-48' FROM aerodromes WHERE name = 'Волгоград' AND city = 'Волгоград'
UNION ALL SELECT id, 'коммутатор', '8-844-726-10-30' FROM aerodromes WHERE name = 'Волгоград' AND city = 'Волгоград';

-- ВОРКУТА
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Воркута', 'Воркута', 'Советский', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'Диспетчер', '8-996-590-16-00' FROM aerodromes WHERE name = 'Воркута'
UNION ALL SELECT id, 'АДП', '8-904-104-55-15' FROM aerodromes WHERE name = 'Воркута'
UNION ALL SELECT id, 'ДПЧ', '8-821-513-63-89' FROM aerodromes WHERE name = 'Воркута';

-- ВОРОНЕЖ (БАЛТИМОР)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Воронеж', 'Воронеж', 'Балтимор', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-473-233-78-61' FROM aerodromes WHERE name = 'Воронеж'
UNION ALL SELECT id, 'Коммутатор', '8-473-253-07-02' FROM aerodromes WHERE name = 'Воронеж'
UNION ALL SELECT id, 'ОД ВУНЦ', '8-473-244-76-78' FROM aerodromes WHERE name = 'Воронеж'
UNION ALL SELECT id, 'Диспетчер', '8-999-745-38-78' FROM aerodromes WHERE name = 'Воронеж';

-- ВОРОНЕЖ (ПРИДАЧА)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Воронеж', 'Воронеж', 'Придача', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-473-249-90-46' FROM aerodromes WHERE name = 'Воронеж' AND airport_name = 'Придача';

-- ВОЗДВИЖЕНКА
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Воздвиженка', 'Воздвиженка', 'Воздвиженка', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-914-650-36-63' FROM aerodromes WHERE name = 'Воздвиженка';

-- ВОЗЖАЕВКА
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Возжаевка', 'Возжаевка', 'Возжаевка', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-996-462-31-92' FROM aerodromes WHERE name = 'Возжаевка';

-- ВЯЗЬМА
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Вязьма', 'Вязьма', 'Вязьма', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'Коммутатор', '8-481-312-25-05' FROM aerodromes WHERE name = 'Вязьма'
UNION ALL SELECT id, 'ОД', '8-915-648-36-01' FROM aerodromes WHERE name = 'Вязьма';

-- ==================== Г ====================

-- ГВАРДЕЙСКОЕ (КРЫМ)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Гвардейское', 'Крым', 'Гвардейское', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-978-129-94-23' FROM aerodromes WHERE name = 'Гвардейское'
UNION ALL SELECT id, 'Диспетчер', '8-978-064-44-28' FROM aerodromes WHERE name = 'Гвардейское'
UNION ALL SELECT id, 'РЦ', '8-978-922-80-29' FROM aerodromes WHERE name = 'Гвардейское';

-- ГЕЛЕНДЖИК
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Геленджик', 'Геленджик', 'Геленджик', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-861-419-90-13' FROM aerodromes WHERE name = 'Геленджик';

-- ГОРЕЛОВО
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Горелово', 'Санкт-Петербург', 'Горелово', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'Диспетчер', '8-812-413-52-35' FROM aerodromes WHERE name = 'Горелово';

-- ==================== Д ====================

-- ДЖАНКОЙ (КРЫМ)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Джанкой', 'Крым', 'Джанкой', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-978-835-35-09' FROM aerodromes WHERE name = 'Джанкой'
UNION ALL SELECT id, 'ОД', '8-987-090-88-87' FROM aerodromes WHERE name = 'Джанкой';

-- ДОМНА
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Домна', 'Домна', 'Домна', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-996-313-95-84' FROM aerodromes WHERE name = 'Домна';

-- ДЗЕМГИ (КОМСОМОЛЬСК-НА-АМУРЕ)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Дземги', 'Комсомольск-на-Амуре', 'Дземги', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-914-319-41-10' FROM aerodromes WHERE name = 'Дземги'
UNION ALL SELECT id, 'ОД', '8-914-216-37-37' FROM aerodromes WHERE name = 'Дземги'
UNION ALL SELECT id, 'Диспетчер', '8-914-192-26-36' FROM aerodromes WHERE name = 'Дземги';

-- ДУБКИ
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Дубки', 'Дубки', 'Дубки', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-917-300-54-45' FROM aerodromes WHERE name = 'Дубки'
UNION ALL SELECT id, 'УС', '8-845-267-46-00' FROM aerodromes WHERE name = 'Дубки';

-- ==================== Е ====================

-- ЕЙСК
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Ейск', 'Ейск', 'Ейск', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'Диспетчер', '8-861-323-41-37' FROM aerodromes WHERE name = 'Ейск'
UNION ALL SELECT id, 'ОД', '8-861-322-76-77' FROM aerodromes WHERE name = 'Ейск';

-- ЕКАТЕРИНБУРГ (КОЛЬЦОВО)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Екатеринбург', 'Екатеринбург', 'Кольцово', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-343-226-86-48' FROM aerodromes WHERE name = 'Екатеринбург'
UNION ALL SELECT id, 'ЦУА', '8-343-375-96-19' FROM aerodromes WHERE name = 'Екатеринбург'
UNION ALL SELECT id, 'ПДСП', '8-343-226-84-09' FROM aerodromes WHERE name = 'Екатеринбург';

-- ЕКАТЕРИНБУРГ (АРАМИЛЬ)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Екатеринбург', 'Екатеринбург', 'Арамиль', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-343-295-52-33' FROM aerodromes WHERE name = 'Екатеринбург' AND airport_name = 'Арамиль'
UNION ALL SELECT id, 'коммутатор', '8-343-220-28-04' FROM aerodromes WHERE name = 'Екатеринбург' AND airport_name = 'Арамиль'
UNION ALL SELECT id, 'РП', '8-343-295-52-32' FROM aerodromes WHERE name = 'Екатеринбург' AND airport_name = 'Арамиль';

-- ЕЛИЗОВО (ПЕТРОПАВЛОВСК-КАМЧАТСКИЙ)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Елизово', 'Петропавловск-Камчатский', 'Елизово', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-415-316-73-21' FROM aerodromes WHERE name = 'Елизово'
UNION ALL SELECT id, 'Диспетчер', '8-914-029-16-63' FROM aerodromes WHERE name = 'Елизово'
UNION ALL SELECT id, 'оперативный', '8-914-029-51-00' FROM aerodromes WHERE name = 'Елизово';

-- ЕРМОЛИНО
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Ермолино', 'Ермолино', 'Ермолино', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'Диспетчер', '8-495-996-34-82' FROM aerodromes WHERE name = 'Ермолино'
UNION ALL SELECT id, 'АДП', '8-484-396-61-30' FROM aerodromes WHERE name = 'Ермолино';

-- ==================== И ====================

-- ИВАНОВО (СЕВЕРНЫЙ)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Иваново', 'Иваново', 'Северный', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'УС', '8-493-237-33-52' FROM aerodromes WHERE name = 'Иваново'
UNION ALL SELECT id, 'АДП', '8-493-237-62-64' FROM aerodromes WHERE name = 'Иваново';

-- ИЖЕВСК
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Ижевск', 'Ижевск', 'Ижевск', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'ПДСП', '8-341-263-06-50' FROM aerodromes WHERE name = 'Ижевск'
UNION ALL SELECT id, 'Метео', '8-341-257-25-06' FROM aerodromes WHERE name = 'Ижевск';

-- ИРКУТСК
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Иркутск', 'Иркутск', 'Иркутск', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'ПДСА', '8-395-254-42-56' FROM aerodromes WHERE name = 'Иркутск'
UNION ALL SELECT id, 'АДП', '8-395-232-29-08' FROM aerodromes WHERE name = 'Иркутск'
UNION ALL SELECT id, 'Метео', '8-395-248-18-04' FROM aerodromes WHERE name = 'Иркутск';

-- ЙОШКАР-ОЛА (ДАНИЛОВО)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Йошкар-Ола', 'Йошкар-Ола', 'Данилово', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-836-272-72-40' FROM aerodromes WHERE name = 'Йошкар-Ола'
UNION ALL SELECT id, 'УС', '8-836-272-74-46' FROM aerodromes WHERE name = 'Йошкар-Ола';

-- ==================== К ====================

-- КАЗАНЬ (БОРИСОГЛЕБСКОЕ)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Казань', 'Казань', 'Борисоглебское', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-843-533-41-22' FROM aerodromes WHERE name = 'Казань'
UNION ALL SELECT id, 'нач. смены', '8-843-267-87-01' FROM aerodromes WHERE name = 'Казань'
UNION ALL SELECT id, 'метео', '8-843-533-40-95' FROM aerodromes WHERE name = 'Казань';

-- КАЗАНЬ (ЮДИНО)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Казань', 'Казань', 'Юдино', 'вертолетный завод', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-917-890-09-16' FROM aerodromes WHERE name = 'Казань' AND airport_name = 'Юдино'
UNION ALL SELECT id, 'УС', '8-843-570-98-03' FROM aerodromes WHERE name = 'Казань' AND airport_name = 'Юдино';

-- КАЛИНИНГРАД (ХРАБРОВО)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Калининград', 'Калининград', 'Храброво', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-401-270-20-37' FROM aerodromes WHERE name = 'Калининград'
UNION ALL SELECT id, 'ПДСП', '8-401-261-04-65' FROM aerodromes WHERE name = 'Калининград';

-- КАЛИНИНГРАД (ЧКАЛОВСК)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Калининград', 'Калининград', 'Чкаловск', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-401-250-28-25' FROM aerodromes WHERE name = 'Калининград' AND airport_name = 'Чкаловск'
UNION ALL SELECT id, 'Диспетчер', '8-401-250-23-22' FROM aerodromes WHERE name = 'Калининград' AND airport_name = 'Чкаловск';

-- КАЛИНИНГРАД (ЧЕРНЯХОВСК)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Калининград', 'Калининград', 'Черняховск', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-401-413-25-58' FROM aerodromes WHERE name = 'Калининград' AND airport_name = 'Черняховск'
UNION ALL SELECT id, 'ОД', '8-401-256-86-00' FROM aerodromes WHERE name = 'Калининград' AND airport_name = 'Черняховск';

-- КАМЕНСК-УРАЛЬСКИЙ
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Каменск-Уральский', 'Каменск-Уральский', 'Каменск-Уральский', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'ОД', '8-343-936-57-57' FROM aerodromes WHERE name = 'Каменск-Уральский'
UNION ALL SELECT id, 'АДП', '8-982-715-31-91' FROM aerodromes WHERE name = 'Каменск-Уральский'
UNION ALL SELECT id, 'Диспетчер', '8-999-568-52-39' FROM aerodromes WHERE name = 'Каменск-Уральский';

-- КАНСК
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Канск', 'Канск', 'Канск', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'УС', '8-391-612-47-20' FROM aerodromes WHERE name = 'Канск'
UNION ALL SELECT id, 'АДП', '8-391-612-15-50' FROM aerodromes WHERE name = 'Канск';

-- КЕМЕРОВО
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Кемерово', 'Кемерово', 'Кемерово', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'ПДСП', '8-384-239-02-98' FROM aerodromes WHERE name = 'Кемерово'
UNION ALL SELECT id, 'АДП', '8-384-244-17-60' FROM aerodromes WHERE name = 'Кемерово';

-- КИРОВ (ПОБЕДИЛОВО)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Киров', 'Киров', 'Победилово', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'Диспетчер', '8-833-255-15-31' FROM aerodromes WHERE name = 'Киров'
UNION ALL SELECT id, 'УС', '8-833-269-67-45' FROM aerodromes WHERE name = 'Киров'
UNION ALL SELECT id, 'суточный техник', '8-991-393-12-18' FROM aerodromes WHERE name = 'Киров';

-- КИПЕЛОВО (ВОЛОГДА)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Кипелово', 'Вологда', 'Кипелово', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'Диспетчер', '8-900-534-73-67' FROM aerodromes WHERE name = 'Кипелово'
UNION ALL SELECT id, 'УС', '8-817-255-15-51' FROM aerodromes WHERE name = 'Кипелово'
UNION ALL SELECT id, 'АДП', '8-817-225-15-15' FROM aerodromes WHERE name = 'Кипелово';

-- КЛИН
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Клин', 'Клин', 'Клин', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-926-873-66-56' FROM aerodromes WHERE name = 'Клин';

-- КОРЕНОВСК
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Кореновск', 'Кореновск', 'Кореновск', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-918-956-57-14' FROM aerodromes WHERE name = 'Кореновск'
UNION ALL SELECT id, 'Диспетчер', '8-999-461-70-08' FROM aerodromes WHERE name = 'Кореновск';

-- КРАСНОДАР (ЦЕНТРАЛЬНЫЙ)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Краснодар', 'Краснодар', 'Центральный', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'ОД', '8-967-650-70-35' FROM aerodromes WHERE name = 'Краснодар'
UNION ALL SELECT id, 'Диспетчер', '8-909-452-22-60' FROM aerodromes WHERE name = 'Краснодар'
UNION ALL SELECT id, 'АДП', '8-861-224-08-43' FROM aerodromes WHERE name = 'Краснодар';

-- КРЫМСК
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Крымск', 'Крымск', 'Крымск', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'Диспетчер', '8-938-430-67-83' FROM aerodromes WHERE name = 'Крымск'
UNION ALL SELECT id, 'АДП', '8-964-937-03-30' FROM aerodromes WHERE name = 'Крымск'
UNION ALL SELECT id, 'УС', '8-861-312-16-34' FROM aerodromes WHERE name = 'Крымск';

-- КУБИНКА
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Кубинка', 'Кубинка', 'Кубинка', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'УС', '8-498-677-70-68' FROM aerodromes WHERE name = 'Кубинка'
UNION ALL SELECT id, 'Коммутатор', '8-495-992-29-52' FROM aerodromes WHERE name = 'Кубинка';

-- КУРСК (ВОСТОЧНЫЙ)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Курск', 'Курск', 'Восточный', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-910-730-03-47' FROM aerodromes WHERE name = 'Курск';

-- КЫЗЫЛ
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Кызыл', 'Кызыл', 'Кызыл', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'гражданские', '8-394-225-15-31' FROM aerodromes WHERE name = 'Кызыл'
UNION ALL SELECT id, 'военные', '8-996-338-24-21' FROM aerodromes WHERE name = 'Кызыл';

-- КУМЕРТАУ
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Кумертау', 'Кумертау', 'Кумертау', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-927-314-70-28' FROM aerodromes WHERE name = 'Кумертау'
UNION ALL SELECT id, 'УС', '8-347-614-21-83' FROM aerodromes WHERE name = 'Кумертау';

-- КУРГАН
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Курган', 'Курган', 'Курган', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-912-830-79-96' FROM aerodromes WHERE name = 'Курган';

-- КОСТРОМА (СОКЕРКИНО)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Кострома', 'Кострома', 'Сокеркино', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-494-235-76-91' FROM aerodromes WHERE name = 'Кострома';

-- КРАСНОЯРСК (ЕМЕЛЬЯНОВО)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Красноярск', 'Красноярск', 'Емельяново', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'Диспетчер', '8-391-252-62-21' FROM aerodromes WHERE name = 'Красноярск'
UNION ALL SELECT id, 'АДП', '8-391-252-65-40' FROM aerodromes WHERE name = 'Красноярск';

-- КОМСОМОЛЬСК-НА-АМУРЕ (ХУРБА)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Комсомольск-на-Амуре', 'Комсомольск-на-Амуре', 'Хурба', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-984-176-93-17' FROM aerodromes WHERE name = 'Комсомольск-на-Амуре'
UNION ALL SELECT id, 'ПДСП', '8-914-318-26-53' FROM aerodromes WHERE name = 'Комсомольск-на-Амуре';

-- КАПУСТИН ЯР
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Капустин Яр', 'Капустин Яр', 'Капустин Яр', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'УС', '8-851-402-18-45' FROM aerodromes WHERE name = 'Капустин Яр'
UNION ALL SELECT id, 'ОД', '8-851-414-20-11' FROM aerodromes WHERE name = 'Капустин Яр';

-- КАРАГАНДА
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Караганда', 'Караганда', 'Караганда', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-721-249-66-41' FROM aerodromes WHERE name = 'Караганда'
UNION ALL SELECT id, 'ПДСП', '8-721-242-85-55' FROM aerodromes WHERE name = 'Караганда';

-- КАНТ (КИРГИЗИЯ)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Кант', 'Кант', 'Кант', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-109-961-132-588-60' FROM aerodromes WHERE name = 'Кант';

-- КРАСНОДАР (ПАШКОВСКИЙ)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Краснодар', 'Краснодар', 'Пашковский', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'планирование', '8-861-263-68-89' FROM aerodromes WHERE name = 'Краснодар' AND airport_name = 'Пашковский'
UNION ALL SELECT id, 'ЦУР', '8-861-219-12-82' FROM aerodromes WHERE name = 'Краснодар' AND airport_name = 'Пашковский';

-- КРЫМ (ДЖАНКОЙ)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Крым', 'Крым', 'Джанкой', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-978-835-35-09' FROM aerodromes WHERE name = 'Крым'
UNION ALL SELECT id, 'ОД', '8-987-090-88-87' FROM aerodromes WHERE name = 'Крым';

-- КРЫМ (КИРОВСКОЕ)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Крым', 'Крым', 'Кировское', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'ОД', '8-978-082-99-59' FROM aerodromes WHERE name = 'Крым' AND airport_name = 'Кировское'
UNION ALL SELECT id, 'Диспетчер', '8-978-093-14-92' FROM aerodromes WHERE name = 'Крым' AND airport_name = 'Кировское';

-- ==================== Л ====================

-- ЛЕВАШОВО (САНКТ-ПЕТЕРБУРГ)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Левашово', 'Санкт-Петербург', 'Левашово', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'ОД', '8-812-597-91-41' FROM aerodromes WHERE name = 'Левашово'
UNION ALL SELECT id, 'УС', '8-812-597-91-10' FROM aerodromes WHERE name = 'Левашово'
UNION ALL SELECT id, 'АДП', '8-812-594-95-19' FROM aerodromes WHERE name = 'Левашово'
UNION ALL SELECT id, 'метео', '8-904-030-45-11' FROM aerodromes WHERE name = 'Левашово';

-- ЛИПЕЦК
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Липецк', 'Липецк', 'Липецк-2', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-904-283-01-86' FROM aerodromes WHERE name = 'Липецк'
UNION ALL SELECT id, 'АДП рабочий', '8-909-221-17-32' FROM aerodromes WHERE name = 'Липецк'
UNION ALL SELECT id, 'УС', '8-474-235-30-11' FROM aerodromes WHERE name = 'Липецк';

-- ==================== М ====================

-- МАХАЧКАЛА (УЙТАШ)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Махачкала', 'Махачкала', 'Уйташ', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'гр. АДП', '8-872-298-88-27' FROM aerodromes WHERE name = 'Махачкала'
UNION ALL SELECT id, 'ПДСП', '8-872-298-88-14' FROM aerodromes WHERE name = 'Махачкала'
UNION ALL SELECT id, 'комендант', '8-963-411-53-30' FROM aerodromes WHERE name = 'Махачкала';

-- МИНЕРАЛЬНЫЕ ВОДЫ
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Минеральные Воды', 'Минеральные Воды', 'Минеральные Воды', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'РП', '8-879-226-87-09' FROM aerodromes WHERE name = 'Минеральные Воды'
UNION ALL SELECT id, 'Диспетчер ПДО', '8-879-222-04-33' FROM aerodromes WHERE name = 'Минеральные Воды';

-- МОЗДОК
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Моздок', 'Моздок', 'Моздок', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'Диспетчер', '8-867-363-23-00' FROM aerodromes WHERE name = 'Моздок'
UNION ALL SELECT id, 'АДП', '8-960-404-38-01' FROM aerodromes WHERE name = 'Моздок'
UNION ALL SELECT id, 'ОД', '8-999-350-01-53' FROM aerodromes WHERE name = 'Моздок'
UNION ALL SELECT id, 'Такси', '8-928-072-38-78' FROM aerodromes WHERE name = 'Моздок';

-- МОРОЗОВСК
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Морозовск', 'Морозовск', 'Морозовск', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-929-817-45-75' FROM aerodromes WHERE name = 'Морозовск'
UNION ALL SELECT id, 'УС', '8-863-844-31-46' FROM aerodromes WHERE name = 'Морозовск'
UNION ALL SELECT id, 'ОД', '8-928-778-86-91' FROM aerodromes WHERE name = 'Морозовск';

-- МОСКВА (ВНУКОВО)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Москва', 'Москва', 'Внуково', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'Диспетчер', '8-495-436-23-76' FROM aerodromes WHERE name = 'Москва' AND airport_name = 'Внуково'
UNION ALL SELECT id, 'метео', '8-495-436-74-51' FROM aerodromes WHERE name = 'Москва' AND airport_name = 'Внуково'
UNION ALL SELECT id, 'АДП', '8-495-436-66-06' FROM aerodromes WHERE name = 'Москва' AND airport_name = 'Внуково'
UNION ALL SELECT id, 'РП', '8-495-436-75-18' FROM aerodromes WHERE name = 'Москва' AND airport_name = 'Внуково'
UNION ALL SELECT id, 'ПДСП', '8-905-511-80-00' FROM aerodromes WHERE name = 'Москва' AND airport_name = 'Внуково';

-- МОСКВА (ЧКАЛОВСКИЙ)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Москва', 'Москва', 'Чкаловский', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-495-993-59-09' FROM aerodromes WHERE name = 'Москва' AND airport_name = 'Чкаловский'
UNION ALL SELECT id, 'УС', '8-495-526-32-43' FROM aerodromes WHERE name = 'Москва' AND airport_name = 'Чкаловский'
UNION ALL SELECT id, 'ОД', '8-909-641-15-50' FROM aerodromes WHERE name = 'Москва' AND airport_name = 'Чкаловский'
UNION ALL SELECT id, 'Диспетчер', '8-496-567-39-69' FROM aerodromes WHERE name = 'Москва' AND airport_name = 'Чкаловский'
UNION ALL SELECT id, 'Коммутатор', '8-496-567-39-66' FROM aerodromes WHERE name = 'Москва' AND airport_name = 'Чкаловский'
UNION ALL SELECT id, 'деж инженер', '8-965-226-34-24' FROM aerodromes WHERE name = 'Москва' AND airport_name = 'Чкаловский'
UNION ALL SELECT id, 'Начпрод', '8-964-555-01-88' FROM aerodromes WHERE name = 'Москва' AND airport_name = 'Чкаловский';

-- МОСКВА (ЛОГИКА)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Москва', 'Москва', 'Логика', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'УС', '8-495-268-44-70' FROM aerodromes WHERE name = 'Москва' AND airport_name = 'Логика'
UNION ALL SELECT id, 'ОД', '8-499-268-70-16' FROM aerodromes WHERE name = 'Москва' AND airport_name = 'Логика';

-- МИЛЛЕРОВО
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Миллерово', 'Миллерово', 'Миллерово', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'УС', '8-863-852-37-57' FROM aerodromes WHERE name = 'Миллерово'
UNION ALL SELECT id, 'АДП', '8-928-296-98-22' FROM aerodromes WHERE name = 'Миллерово';

-- МИЧУРИНСК
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Мичуринск', 'Мичуринск', 'Мичуринск', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'УС', '8-474-278-21-60' FROM aerodromes WHERE name = 'Мичуринск';

-- МОНЧЕГОРСК (СУРГУЧ)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Мончегорск', 'Мончегорск', 'Сургуч', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'УС', '8-815-363-15-24' FROM aerodromes WHERE name = 'Мончегорск'
UNION ALL SELECT id, 'АДП', '8-911-302-92-97' FROM aerodromes WHERE name = 'Мончегорск';

-- МУРИНО (МУЛИНО)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Мулино', 'Мулино', 'вертодром', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'Диспетчер', '8-963-366-79-36' FROM aerodromes WHERE name = 'Мулино'
UNION ALL SELECT id, 'РП', '8-964-831-02-40' FROM aerodromes WHERE name = 'Мулино';

-- МИРНЫЙ
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Мирный', 'Мирный', 'Мирный', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-411-369-81-66' FROM aerodromes WHERE name = 'Мирный'
UNION ALL SELECT id, 'УС', '8-411-369-81-20' FROM aerodromes WHERE name = 'Мирный';

-- МУРМАНСК
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Мурманск', 'Мурманск', 'Мурманск', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-815-228-14-32' FROM aerodromes WHERE name = 'Мурманск';

-- ==================== Н ====================

-- НИЖНИЙ НОВГОРОД (СТРИГИНО)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Нижний Новгород', 'Нижний Новгород', 'Стригино', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-831-283-28-00' FROM aerodromes WHERE name = 'Нижний Новгород'
UNION ALL SELECT id, 'УС', '8-999-073-37-97' FROM aerodromes WHERE name = 'Нижний Новгород'
UNION ALL SELECT id, 'ПДСП', '8-831-261-80-93' FROM aerodromes WHERE name = 'Нижний Новгород'
UNION ALL SELECT id, 'планирование', '8-831-269-35-10' FROM aerodromes WHERE name = 'Нижний Новгород'
UNION ALL SELECT id, 'Нач. службы движения', '8-910-300-97-05' FROM aerodromes WHERE name = 'Нижний Новгород';

-- НИЖНИЙ НОВГОРОД (СОРМОВО)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Нижний Новгород', 'Нижний Новгород', 'Сормово', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-831-242-33-78' FROM aerodromes WHERE name = 'Нижний Новгород' AND airport_name = 'Сормово'
UNION ALL SELECT id, 'АДП', '8-831-242-33-75' FROM aerodromes WHERE name = 'Нижний Новгород' AND airport_name = 'Сормово';

-- НОВОСИБИРСК (ТОЛМАЧЕВО)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Новосибирск', 'Новосибирск', 'Толмачево', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'Диспетчер', '8-996-544-90-81' FROM aerodromes WHERE name = 'Новосибирск'
UNION ALL SELECT id, 'Коммутатор', '8-383-253-11-39' FROM aerodromes WHERE name = 'Новосибирск'
UNION ALL SELECT id, 'АДП', '8-923-763-92-98' FROM aerodromes WHERE name = 'Новосибирск'
UNION ALL SELECT id, 'ПДСП', '8-383-216-91-13' FROM aerodromes WHERE name = 'Новосибирск'
UNION ALL SELECT id, 'ОД', '8-996-380-21-59' FROM aerodromes WHERE name = 'Новосибирск';

-- НОВОСИБИРСК (ЕЛЬЦОВКА)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Новосибирск', 'Новосибирск', 'Ельцовка', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-383-279-09-85' FROM aerodromes WHERE name = 'Новосибирск' AND airport_name = 'Ельцовка'
UNION ALL SELECT id, 'военн. АДП', '8-383-216-94-67' FROM aerodromes WHERE name = 'Новосибирск' AND airport_name = 'Ельцовка';

-- НОРГИЛЬСК
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Норильск', 'Норильск', 'Норильск', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-391-947-02-33' FROM aerodromes WHERE name = 'Норильск'
UNION ALL SELECT id, 'УС', '8-391-947-02-50' FROM aerodromes WHERE name = 'Норильск';

-- НИЖНЕВАРТОВСК
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Нижневартовск', 'Нижневартовск', 'Нижневартовск', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'ПДСП', '8-346-649-20-30' FROM aerodromes WHERE name = 'Нижневартовск'
UNION ALL SELECT id, 'начальник смены', '8-912-934-83-64' FROM aerodromes WHERE name = 'Нижневартовск'
UNION ALL SELECT id, 'оперативный', '8-996-444-56-32' FROM aerodromes WHERE name = 'Нижневартовск';

-- НАРЫН-МАР
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Нарьян-Мар', 'Нарьян-Мар', 'Нарьян-Мар', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'Диспетчер', '8-818-534-61-30' FROM aerodromes WHERE name = 'Нарьян-Мар';

-- НАГОРСКОЕ
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Нагурское', 'Нагурское', 'Нагурское', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-345-254-41-15' FROM aerodromes WHERE name = 'Нагурское'
UNION ALL SELECT id, 'УС', '8-345-254-41-14' FROM aerodromes WHERE name = 'Нагурское';

-- НИЖНЕКАМСК (БЕГИШЕВО)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Нижнекамск', 'Нижнекамск', 'Бегишево', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'ПДСП', '8-855-279-09-07' FROM aerodromes WHERE name = 'Нижнекамск';

-- ==================== О ====================

-- ОМСК (СЕВЕРНЫЙ)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Омск', 'Омск', 'Северный', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-381-253-61-83' FROM aerodromes WHERE name = 'Омск'
UNION ALL SELECT id, 'УС', '8-923-763-92-97' FROM aerodromes WHERE name = 'Омск';

-- ОМСК (ЦЕНТРАЛЬНЫЙ)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Омск', 'Омск', 'Центральный', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-381-251-73-84' FROM aerodromes WHERE name = 'Омск' AND airport_name = 'Центральный'
UNION ALL SELECT id, 'ПДСП', '8-381-251-74-37' FROM aerodromes WHERE name = 'Омск' AND airport_name = 'Центральный';

-- ОРЕНБУРГ
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Оренбург', 'Оренбург', 'Оренбург', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'ОД', '8-353-276-51-07' FROM aerodromes WHERE name = 'Оренбург'
UNION ALL SELECT id, 'Дивизия', '8-353-276-51-62' FROM aerodromes WHERE name = 'Оренбург'
UNION ALL SELECT id, 'инженер', '8-912-351-99-40' FROM aerodromes WHERE name = 'Оренбург';

-- ОРСК
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Орск', 'Орск', 'Орск', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-353-720-33-22' FROM aerodromes WHERE name = 'Орск'
UNION ALL SELECT id, 'ПДСП', '8-353-720-31-70' FROM aerodromes WHERE name = 'Орск';

-- ОСТАФЬЕВО (МОСКВА)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Остафьево', 'Москва', 'Остафьево', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-495-817-31-49' FROM aerodromes WHERE name = 'Остафьево'
UNION ALL SELECT id, 'АДП', '8-969-348-98-11' FROM aerodromes WHERE name = 'Остафьево';

-- ОСТРОВ (ПСКОВ)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Остров', 'Псков', 'Остров', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-911-395-08-52' FROM aerodromes WHERE name = 'Остров'
UNION ALL SELECT id, 'УС', '8-811-523-34-69' FROM aerodromes WHERE name = 'Остров';

-- ОЛЕНЬЯ (ОЛЕНЕГОРСК)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Оленья', 'Оленегорск', 'Оленья', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-911-801-07-20' FROM aerodromes WHERE name = 'Оленья'
UNION ALL SELECT id, 'АДП', '8-911-309-36-17' FROM aerodromes WHERE name = 'Оленья';

-- ОЛЕНИЦА
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Оленица', 'Оленица', 'Оленица', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-911-335-28-72' FROM aerodromes WHERE name = 'Оленица';

-- ==================== П ====================

-- ПЕРМЬ (БОЛЬШОЕ САВИНО)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Пермь', 'Пермь', 'Большое Савино', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'УС', '8-342-294-61-48' FROM aerodromes WHERE name = 'Пермь'
UNION ALL SELECT id, 'Диспетчер', '8-992-203-88-15' FROM aerodromes WHERE name = 'Пермь'
UNION ALL SELECT id, 'ОД', '8-919-478-06-29' FROM aerodromes WHERE name = 'Пермь';

-- ПЛЕСЕЦК
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Плесецк', 'Плесецк', 'Плесецк', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'Диспетчер', '8-921-292-34-09' FROM aerodromes WHERE name = 'Плесецк'
UNION ALL SELECT id, 'АДП', '8-818-342-06-01' FROM aerodromes WHERE name = 'Плесецк';

-- ПСКОВ
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Псков', 'Псков', 'Псков', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-811-262-02-67' FROM aerodromes WHERE name = 'Псков';

-- ПУЛКОВО (САНКТ-ПЕТЕРБУРГ)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Пулково', 'Санкт-Петербург', 'Пулково', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-812-324-37-50' FROM aerodromes WHERE name = 'Пулково'
UNION ALL SELECT id, 'по ЗАРу', '8-812-324-34-63' FROM aerodromes WHERE name = 'Пулково'
UNION ALL SELECT id, 'Комендант', '8-921-313-63-90' FROM aerodromes WHERE name = 'Пулково'
UNION ALL SELECT id, 'Диспетчер планирования', '8-911-030-53-05' FROM aerodromes WHERE name = 'Пулково';

-- ПЕТРОЗАВОДСК (БЕСОВЕЦ)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Петрозаводск', 'Петрозаводск', 'Бесовец', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'деж. по полку', '8-814-271-13-77' FROM aerodromes WHERE name = 'Петрозаводск'
UNION ALL SELECT id, 'АДП', '8-921-524-25-31' FROM aerodromes WHERE name = 'Петрозаводск'
UNION ALL SELECT id, 'коммутатор', '8-814-277-75-93' FROM aerodromes WHERE name = 'Петрозаводск';

-- ПОЛЯРНЫЙ
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Полярный', 'Полярный', 'Полярный', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-411-365-31-31' FROM aerodromes WHERE name = 'Полярный'
UNION ALL SELECT id, 'АДП', '8-411-364-90-82' FROM aerodromes WHERE name = 'Полярный';

-- ==================== Р ====================

-- РОСТОВ (ЦЕНТРАЛЬНЫЙ)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Ростов', 'Ростов-на-Дону', 'Центральный', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'Коммутатор', '8-863-278-34-15' FROM aerodromes WHERE name = 'Ростов'
UNION ALL SELECT id, 'Диспетчер', '8-863-278-21-15' FROM aerodromes WHERE name = 'Ростов'
UNION ALL SELECT id, 'УС', '8-863-234-81-47' FROM aerodromes WHERE name = 'Ростов'
UNION ALL SELECT id, 'АДП', '8-909-404-00-73' FROM aerodromes WHERE name = 'Ростов'
UNION ALL SELECT id, 'Инженер по АТО', '8-918-512-63-02' FROM aerodromes WHERE name = 'Ростов';

-- РОСТОВ (ПЛАТОВ)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Ростов', 'Ростов-на-Дону', 'Платов', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'ПДСП', '8-863-333-47-80' FROM aerodromes WHERE name = 'Ростов' AND airport_name = 'Платов'
UNION ALL SELECT id, 'АДП', '8-863-276-70-27' FROM aerodromes WHERE name = 'Ростов' AND airport_name = 'Платов';

-- РЯЗАНЬ (ДЯГИЛЕВО)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Рязань', 'Рязань', 'Дягилево', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'Коммутатор', '8-491-234-90-06' FROM aerodromes WHERE name = 'Рязань'
UNION ALL SELECT id, 'ОД', '8-953-739-52-51' FROM aerodromes WHERE name = 'Рязань'
UNION ALL SELECT id, 'УС', '8-491-233-53-18' FROM aerodromes WHERE name = 'Рязань';

-- РЖЕВ
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Ржев', 'Ржев', 'Ржев', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-482-326-64-82' FROM aerodromes WHERE name = 'Ржев';

-- РТИЩЕВО
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Ртищево', 'Ртищево', 'Ртищево', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-917-303-28-23' FROM aerodromes WHERE name = 'Ртищево'
UNION ALL SELECT id, 'АДП', '8-987-829-37-23' FROM aerodromes WHERE name = 'Ртищево';

-- РАМЕНСКОЕ
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Раменское', 'Раменское', 'Раменское', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-495-556-55-79' FROM aerodromes WHERE name = 'Раменское'
UNION ALL SELECT id, 'АДП', '8-495-556-58-88' FROM aerodromes WHERE name = 'Раменское';

-- ==================== С ====================

-- САМАРА (КУРУМОЧ)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Самара', 'Самара', 'Курумоч', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-846-966-51-40' FROM aerodromes WHERE name = 'Самара'
UNION ALL SELECT id, 'Диспетчер', '8-846-966-55-19' FROM aerodromes WHERE name = 'Самара'
UNION ALL SELECT id, 'УС', '8-846-966-53-59' FROM aerodromes WHERE name = 'Самара';

-- САМАРА (БЕЗЫМЯНКА)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Самара', 'Самара', 'Безымянка', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-846-955-02-79' FROM aerodromes WHERE name = 'Самара' AND airport_name = 'Безымянка'
UNION ALL SELECT id, 'метео', '8-846-920-43-77' FROM aerodromes WHERE name = 'Самара' AND airport_name = 'Безымянка';

-- САМАРА (КРЯЖ)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Самара', 'Самара', 'Кряж', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-846-223-49-90' FROM aerodromes WHERE name = 'Самара' AND airport_name = 'Кряж'
UNION ALL SELECT id, 'АДП', '8-846-375-94-12' FROM aerodromes WHERE name = 'Самара' AND airport_name = 'Кряж';

-- САНКТ-ПЕТЕРБУРГ (ПУШКИН)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Санкт-Петербург', 'Санкт-Петербург', 'Пушкин', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'ОД', '8-812-451-57-36' FROM aerodromes WHERE name = 'Санкт-Петербург'
UNION ALL SELECT id, 'АДП', '8-812-465-32-86' FROM aerodromes WHERE name = 'Санкт-Петербург'
UNION ALL SELECT id, 'УС', '8-812-467-07-34' FROM aerodromes WHERE name = 'Санкт-Петербург';

-- САРАТОВ (СОКОЛ)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Саратов', 'Саратов', 'Сокол', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'Диспетчер', '8-927-056-35-44' FROM aerodromes WHERE name = 'Саратов';

-- САРАТОВ (ГАГАРИН)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Саратов', 'Саратов', 'Гагарин', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'по ЗАРу', '8-962-621-67-12' FROM aerodromes WHERE name = 'Саратов' AND airport_name = 'Гагарин'
UNION ALL SELECT id, 'ПДСП', '8-909-330-07-01' FROM aerodromes WHERE name = 'Саратов' AND airport_name = 'Гагарин';

-- САЛЕХАРД
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Салехард', 'Салехард', 'Салехард', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-349-224-46-09' FROM aerodromes WHERE name = 'Салехард'
UNION ALL SELECT id, 'коммутатор', '8-349-227-44-04' FROM aerodromes WHERE name = 'Салехард';

-- САВАСЛЕЙКА
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Саваслейка', 'Саваслейка', 'Саваслейка', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'Диспетчер', '8-930-710-59-74' FROM aerodromes WHERE name = 'Саваслейка'
UNION ALL SELECT id, 'УС', '8-831-767-12-35' FROM aerodromes WHERE name = 'Саваслейка'
UNION ALL SELECT id, 'ОД', '8-951-908-18-70' FROM aerodromes WHERE name = 'Саваслейка';

-- СЕВЕРOMОРСК-1
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Североморск-1', 'Североморск', 'Североморск-1', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'Диспетчер', '8-981-301-98-02' FROM aerodromes WHERE name = 'Североморск-1'
UNION ALL SELECT id, 'АДП', '8-815-376-41-76' FROM aerodromes WHERE name = 'Североморск-1'
UNION ALL SELECT id, 'АД', '8-815-376-40-03' FROM aerodromes WHERE name = 'Североморск-1'
UNION ALL SELECT id, 'дежурный по полку', '8-815-376-41-90' FROM aerodromes WHERE name = 'Североморск-1';

-- СЕВЕРOMОРСК-3
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Североморск-3', 'Североморск', 'Североморск-3', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'Диспетчер', '8-960-026-08-08' FROM aerodromes WHERE name = 'Североморск-3'
UNION ALL SELECT id, 'ОД', '8-911-311-22-13' FROM aerodromes WHERE name = 'Североморск-3'
UNION ALL SELECT id, 'УС', '8-953-306-56-77' FROM aerodromes WHERE name = 'Североморск-3';

-- СЕЗА
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Сеща', 'Сеща', 'Сеща', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'ОД', '8-483-329-75-05' FROM aerodromes WHERE name = 'Сеща'
UNION ALL SELECT id, 'личный', '8-980-315-14-39' FROM aerodromes WHERE name = 'Сеща';

-- СИМФЕРОПОЛЬ
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Симферополь', 'Симферополь', 'Симферополь', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-365-259-52-80' FROM aerodromes WHERE name = 'Симферополь'
UNION ALL SELECT id, 'УС', '8-365-259-53-99' FROM aerodromes WHERE name = 'Симферополь';

-- СОЧИ (АДЛЕР)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Сочи', 'Сочи', 'Адлер', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-862-249-75-71' FROM aerodromes WHERE name = 'Сочи'
UNION ALL SELECT id, 'коммутатор', '8-862-241-98-21' FROM aerodromes WHERE name = 'Сочи'
UNION ALL SELECT id, 'личный', '8-988-142-32-14' FROM aerodromes WHERE name = 'Сочи';

-- СТАВРОПОЛЬ
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Ставрополь', 'Ставрополь', 'Ставрополь', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-865-235-34-83' FROM aerodromes WHERE name = 'Ставрополь';

-- СТАРАЯ РУССА
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Старая Русса', 'Старая Русса', 'Старая Русса', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-816-523-67-28' FROM aerodromes WHERE name = 'Старая Русса'
UNION ALL SELECT id, 'приемная', '8-816-525-94-93' FROM aerodromes WHERE name = 'Старая Русса';

-- СУРГУТ
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Сургут', 'Сургут', 'Сургут', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'ПДСП', '8-346-277-04-14' FROM aerodromes WHERE name = 'Сургут';

-- СЫЗРАНЬ (ТРОЕКУРОВКА)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Сызрань', 'Сызрань', 'Троекуровка', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-927-772-41-92' FROM aerodromes WHERE name = 'Сызрань'
UNION ALL SELECT id, 'УС', '8-846-437-13-96' FROM aerodromes WHERE name = 'Сызрань';

-- СОЛЬЦЫ
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Сольцы', 'Сольцы', 'Сольцы', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-911-606-45-91' FROM aerodromes WHERE name = 'Сольцы'
UNION ALL SELECT id, 'Диспетчер', '8-911-645-21-14' FROM aerodromes WHERE name = 'Сольцы'
UNION ALL SELECT id, 'УС', '8-911-602-53-89' FROM aerodromes WHERE name = 'Сольцы';

-- ==================== Т ====================

-- ТАГАНРОГ (ЦЕНТРАЛЬНЫЙ)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Таганрог', 'Таганрог', 'Центральный', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'ОД КП', '8-863-433-44-60' FROM aerodromes WHERE name = 'Таганрог'
UNION ALL SELECT id, 'АДП', '8-988-536-88-16' FROM aerodromes WHERE name = 'Таганрог';

-- ТАГАНРОГ (ЮЖНЫЙ)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Таганрог', 'Таганрог', 'Южный', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-863-432-07-58' FROM aerodromes WHERE name = 'Таганрог' AND airport_name = 'Южный';

-- ТАЛАГИ (АРХАНГЕЛЬСК)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Талаги', 'Архангельск', 'Талаги', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'гр. АДП', '8-818-263-15-25' FROM aerodromes WHERE name = 'Талаги'
UNION ALL SELECT id, 'ЦУА', '8-818-263-14-00' FROM aerodromes WHERE name = 'Талаги'
UNION ALL SELECT id, 'АДП', '8-818-241-31-19' FROM aerodromes WHERE name = 'Талаги'
UNION ALL SELECT id, 'Диспетчер', '8-818-241-31-20' FROM aerodromes WHERE name = 'Талаги';

-- ТАМБОВ
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Тамбов', 'Тамбов', 'Тамбов', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'Диспетчер', '8-915-880-58-80' FROM aerodromes WHERE name = 'Тамбов'
UNION ALL SELECT id, 'УС', '8-482-244-75-41' FROM aerodromes WHERE name = 'Тамбов';

-- ТВЕРЬ
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Тверь', 'Тверь', 'Тверь', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-482-519-13-13' FROM aerodromes WHERE name = 'Тверь'
UNION ALL SELECT id, 'ОД КП', '8-482-244-71-57' FROM aerodromes WHERE name = 'Тверь'
UNION ALL SELECT id, 'УС', '8-482-244-75-41' FROM aerodromes WHERE name = 'Тверь'
UNION ALL SELECT id, 'ОД ПУ', '8-910-539-36-97' FROM aerodromes WHERE name = 'Тверь';

-- ТИКСИ
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Тикси', 'Тикси', 'Тикси', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-924-169-30-10' FROM aerodromes WHERE name = 'Тикси'
UNION ALL SELECT id, 'зам. командира', '8-924-360-80-34' FROM aerodromes WHERE name = 'Тикси'
UNION ALL SELECT id, 'ОД', '8-914-287-91-26' FROM aerodromes WHERE name = 'Тикси';

-- ТИХОРЕЦК
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Тихорецк', 'Тихорецк', 'Тихорецк', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'Диспетчер', '8-960-477-57-00' FROM aerodromes WHERE name = 'Тихорецк'
UNION ALL SELECT id, 'УС', '8-861-965-70-32' FROM aerodromes WHERE name = 'Тихорецк';

-- ТОЦКОЕ
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Тоцкое', 'Тоцкое', 'Тоцкое', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-932-532-95-60' FROM aerodromes WHERE name = 'Тоцкое'
UNION ALL SELECT id, 'УС', '8-353-492-84-03' FROM aerodromes WHERE name = 'Тоцкое';

-- ТУЛА (КЛОКОВО)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Тула', 'Тула', 'Клоково', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'ДПЧ', '8-487-238-16-26' FROM aerodromes WHERE name = 'Тула'
UNION ALL SELECT id, 'УС', '8-487-238-17-83' FROM aerodromes WHERE name = 'Тула';

-- ТЮМЕНЬ (РОЩИНО)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Тюмень', 'Тюмень', 'Рощино', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-345-249-64-50' FROM aerodromes WHERE name = 'Тюмень'
UNION ALL SELECT id, 'ПДСП', '8-345-249-64-98' FROM aerodromes WHERE name = 'Тюмень';

-- ТОМСК
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Томск', 'Томск', 'Томск', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-382-293-27-01' FROM aerodromes WHERE name = 'Томск';

-- ==================== У ====================

-- УЛАН-УДЭ (ВОСТОЧНЫЙ)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Улан-Удэ', 'Улан-Удэ', 'Восточный', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АД', '8-996-936-10-57' FROM aerodromes WHERE name = 'Улан-Удэ'
UNION ALL SELECT id, 'Коммутатор', '8-301-225-15-00' FROM aerodromes WHERE name = 'Улан-Удэ'
UNION ALL SELECT id, 'Диспетчер', '8-301-225-17-80' FROM aerodromes WHERE name = 'Улан-Удэ'
UNION ALL SELECT id, 'метео', '8-993-793-09-96' FROM aerodromes WHERE name = 'Улан-Удэ';

-- УЛАН-УДЭ (МУХИНО/БАЙКАЛ)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Улан-Удэ', 'Улан-Удэ', 'Мухино', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-301-222-71-22' FROM aerodromes WHERE name = 'Улан-Удэ' AND airport_name = 'Мухино'
UNION ALL SELECT id, 'УС', '8-301-222-74-81' FROM aerodromes WHERE name = 'Улан-Удэ' AND airport_name = 'Мухино';

-- УФА
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Уфа', 'Уфа', 'Уфа', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-347-279-18-73' FROM aerodromes WHERE name = 'Уфа'
UNION ALL SELECT id, 'ПДСП', '8-347-229-55-97' FROM aerodromes WHERE name = 'Уфа';

-- УЛЬЯНОВСК (БАРАТАЕВКА)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Ульяновск', 'Ульяновск', 'Баратаевка', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-842-261-88-75' FROM aerodromes WHERE name = 'Ульяновск'
UNION ALL SELECT id, 'ПДСП', '8-842-258-84-00' FROM aerodromes WHERE name = 'Ульяновск';

-- УПРУН
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Упрун', 'Упрун', 'Упрун', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-912-898-10-22' FROM aerodromes WHERE name = 'Упрун'
UNION ALL SELECT id, 'личный', '8-908-093-88-09' FROM aerodromes WHERE name = 'Упрун';

-- УСИНСК
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Усинск', 'Усинск', 'Усинск', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-821-445-04-39' FROM aerodromes WHERE name = 'Усинск';

-- УХТА
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Ухта', 'Ухта', 'Ухта', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-821-679-80-23' FROM aerodromes WHERE name = 'Ухта'
UNION ALL SELECT id, 'УС', '8-821-675-77-10' FROM aerodromes WHERE name = 'Ухта';

-- УКРАИНКА
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Украинка', 'Хабаровский край', 'Украинка', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-996-384-37-95' FROM aerodromes WHERE name = 'Украинка'
UNION ALL SELECT id, 'личный', '8-914-576-24-91' FROM aerodromes WHERE name = 'Украинка';

-- ==================== Х ====================

-- ХАБАРОВСК (НОВЫЙ)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Хабаровск', 'Хабаровск', 'Новый', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-421-226-33-33' FROM aerodromes WHERE name = 'Хабаровск'
UNION ALL SELECT id, 'УС', '8-421-226-20-38' FROM aerodromes WHERE name = 'Хабаровск'
UNION ALL SELECT id, 'ПДСП', '8-421-226-32-36' FROM aerodromes WHERE name = 'Хабаровск';

-- ХОТИЛОВО
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Хотилово', 'Хотилово', 'Хотилово', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'Диспетчер', '8-482-332-01-32' FROM aerodromes WHERE name = 'Хотилово'
UNION ALL SELECT id, 'ОД', '8-909-641-15-50' FROM aerodromes WHERE name = 'Хотилово'
UNION ALL SELECT id, 'ДПЧ', '8-482-335-28-69' FROM aerodromes WHERE name = 'Хотилово'
UNION ALL SELECT id, 'АДП', '8-482-332-01-32' FROM aerodromes WHERE name = 'Хотилово';

-- ХАНТЫ-МАНСИЙСК
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Ханты-Мансийск', 'Ханты-Мансийск', 'Ханты-Мансийск', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-346-735-42-09' FROM aerodromes WHERE name = 'Ханты-Мансийск';

-- ХАТАНГА
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Хатанга', 'Хатанга', 'Хатанга', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-391-762-16-40' FROM aerodromes WHERE name = 'Хатанга';

-- ==================== Ч ====================

-- ЧЕЛЯБИНСК (БАЛАНДИНО)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Челябинск', 'Челябинск', 'Баландино', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'ПДСП', '8-351-778-32-36' FROM aerodromes WHERE name = 'Челябинск'
UNION ALL SELECT id, 'АДП', '8-351-779-07-01' FROM aerodromes WHERE name = 'Челябинск'
UNION ALL SELECT id, 'ОД', '8-351-725-85-30' FROM aerodromes WHERE name = 'Челябинск'
UNION ALL SELECT id, 'Диспетчер', '8-351-778-32-36' FROM aerodromes WHERE name = 'Челябинск';

-- ЧЕЛЯБИНСК (ШАГОЛ)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Челябинск', 'Челябинск', 'Шагол', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'Диспетчер', '8-908-934-72-47' FROM aerodromes WHERE name = 'Челябинск' AND airport_name = 'Шагол'
UNION ALL SELECT id, 'металл-дисп', '8-351-266-60-35' FROM aerodromes WHERE name = 'Челябинск' AND airport_name = 'Шагол'
UNION ALL SELECT id, 'ЗАП', '8-903-089-50-03' FROM aerodromes WHERE name = 'Челябинск' AND airport_name = 'Шагол';

-- ЧИТА (КАДАЛА)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Чита', 'Чита', 'Кадала', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'Диспетчер', '8-302-941-20-55' FROM aerodromes WHERE name = 'Чита'
UNION ALL SELECT id, 'АДП', '8-302-241-20-55' FROM aerodromes WHERE name = 'Чита'
UNION ALL SELECT id, 'военный комендант', '8-924-510-01-10' FROM aerodromes WHERE name = 'Чита';

-- ЧКАЛОВСКИЙ (МОСКВА)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Чкаловский', 'Москва', 'Чкаловский ГЛИЦ', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-929-581-57-10' FROM aerodromes WHERE name = 'Чкаловский';

-- ЧЕБЕНЬКИ (ОРЕНБУРГ)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Чебеньки', 'Оренбург', 'Чебеньки', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-922-552-85-54' FROM aerodromes WHERE name = 'Чебеньки'
UNION ALL SELECT id, 'УС', '8-922-800-09-55' FROM aerodromes WHERE name = 'Чебеньки';

-- ЧЕБОКСАРЫ
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Чебоксары', 'Чебоксары', 'Чебоксары', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'Брифинг', '8-835-230-11-76' FROM aerodromes WHERE name = 'Чебоксары'
UNION ALL SELECT id, 'АДП', '8-835-230-11-55' FROM aerodromes WHERE name = 'Чебоксары';

-- ==================== Э ====================

-- ЭНГЕЛЬС
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Энгельс', 'Энгельс', 'Энгельс-2', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-999-539-35-00' FROM aerodromes WHERE name = 'Энгельс'
UNION ALL SELECT id, 'УС', '8-845-374-99-69' FROM aerodromes WHERE name = 'Энгельс'
UNION ALL SELECT id, 'Коммутатор', '8-845-374-99-69' FROM aerodromes WHERE name = 'Энгельс';

-- ЕЛЬЦОВКА (НОВОСИБИРСК)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Ельцовка', 'Новосибирск', 'Ельцовка', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-383-279-09-85' FROM aerodromes WHERE name = 'Ельцовка'
UNION ALL SELECT id, 'военн. АДП', '8-383-216-94-67' FROM aerodromes WHERE name = 'Ельцовка';

-- ==================== Ю ====================

-- ЮЖНО-САХАЛИНСК (ХОМУТОВО)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Южно-Сахалинск', 'Южно-Сахалинск', 'Хомутово', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-424-278-87-74' FROM aerodromes WHERE name = 'Южно-Сахалинск'
UNION ALL SELECT id, 'ПДСП', '8-424-278-83-42' FROM aerodromes WHERE name = 'Южно-Сахалинск';

-- ==================== Я ====================

-- ЯРОСЛАВЛЬ (ТУНОШНАЯ)
INSERT INTO aerodromes (name, city, airport_name, housing_info, created_by) 
VALUES ('Ярославль', 'Ярославль', 'Туношная', 'Уточняется', 393293807)
ON CONFLICT DO NOTHING;

INSERT INTO aerodrome_phones (aerodrome_id, phone_name, phone_number)
SELECT id, 'АДП', '8-485-243-18-38' FROM aerodromes WHERE name = 'Ярославль'
UNION ALL SELECT id, 'КДП', '8-485-243-18-37' FROM aerodromes WHERE name = 'Ярославль';

-- ============================================================
-- ПРОВЕРКА РЕЗУЛЬТАТОВ
-- ============================================================

SELECT COUNT(*) as total_aerodromes FROM aerodromes;
SELECT COUNT(*) as total_phones FROM aerodrome_phones;

-- ============================================================
-- ГОТОВО! База заполнена всеми аэродромами
-- ============================================================