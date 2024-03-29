# Zetachain-earn-xp
<img src="https://i.postimg.cc/NF5MqDBH/image.png" /> 

# Доступные модули
* 🧠 **Автоматический Маршрут** — _запускает автоматический маршрут выполнения заданий_
* 🧠 **Кастомный маршрут** — _запускает по очереди модули из `CUSTOM_WAY` в `settings.py`_
* 💲  **Вывод с ОКХ** — _выводит сумму указанную в  `AMOUNT_TO_WITHDRAW` из `settings.py`_
* 📝 **Регистрация по рефке** — _регистрирует аккаунт по рефке из `settings.py`_
* 💸 **Перевод самому себе** — _переводит ZETA сам себе(кол-во указывается в `settings.py`)_
* 🔄 **Свап на iZUMi** — _делает свап на iZUMi, пару спрашивает после запуска (кол-во для свапа указывается в `settings.py`)_
* ➕ **Добавить ликвидность** — _добавляет ликвидность, пару спрашивает после запуска (кол-во 10-90% от баланса второго токена)_
* 🔄 **Свап на Eddy Finance** — _делает свап("туда-обратно") на Eddy Finance, пару спрашивает после запуска (кол-во для свапа указывается в `settings.py` !минимум 5$!)_
* 🌹 **Минт $stZETA** — _минтит $stZETA для задания Accumulated Finance (кол-во указывается в `settings.py` | задание регает даже без стейка, только минт)_
* 🥇 **Минт нфт бейджа на Ultiverse** — _минтит нфт бейдж Zeta Badge на Ultiverse(выполнить можно только один раз)_
* 🎁 **Клейм поинтов** — _клеймит все доступные поинты для аккаунта_
* 💰 **Депозит на адрес для вывода** — _выводит баланс на адреса для вывода (кол-во которое оставить указывается в `settings.py`)_
* 📊 **Чекер** — _отображает статистику аккаунтов_
* 💹 **Проверить баланс ОКХ** — _отображает текущий баланс $ZETA на ОКХ_

# Настройка
* В файл `data/accounts.txt` вписываем приватные ключи или фразы с новой строки !**перед запуском убрать пример**!
* В файл `data/deposit_addresses.txt` вписываем адреса для вывода с новой строки !**перед запуском убрать пример**!
* В файл `data/proxies.txt` вписываем прокси в формате `login:pass@ip:port` с новой строки !**перед запуском убрать пример**!
* В файле `settings.py` выставляем настройки(каждый пункт подписан)

# Установка
#### *Чтобы отображались эмодзи и всё отображалось корректно лучше использовать VS Code или Windows Terminal*
Открываем cmd и прописываем:
1. `cd путь/к/проекту`
3. `python -m venv venv`
4. `venv\Scripts\activate`
5. `pip install -r requirements.txt`

# Запуск
```
python main.py
```

# Важно
* Версия python должна быть **минимум 3.10**
* Сейчас для выполнения всех заданий кроме Eddy finance требуется ~0.05 $ZETA
* Для вывода с ОКХ токены $ZETA должны быть на **основном аккаунте**, а не торговом
* Если аккаунты уже имеют баланс, то выставьте для `MIN_WALLET_BALANCE` в `settings.py` значение 0
* Если прокси не используются или его нет для аккаунта, тогда после каждого аккаунта софт будет ждать смены IP(просто жмёте Enter когда поменяли IP). Сделал чтобы можно было раздавать интернет с телефона и менять IP через режим полёта
* Свапалку Eddy Finance лучше не использовать, из-за большого слиппейджа. На двух свапах из 5$ теряется 0.2-0.3$. Чтобы выключить для кастомного маршрута нужно просто закомментировать в `CUSTOM_WAY`. А чтобы выключить из автоматического маршрута нужно закомментировать 40-ую строку в `functions.py`
* Бекенд сайта с заданиями медленно обновляется. Из-за этого задания которые только что выполнились не сразу выполнятся на сайте. Поэтому после того как прогнали аккаунты лучше ещё раз запустить клейм

###### возможно скоро добавляю в софт выполнение ещё квестов
