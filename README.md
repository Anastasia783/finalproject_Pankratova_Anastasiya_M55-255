# Final Project - Currency Wallet
Приложение для управления виртуальным валютным кошельком. Это комплексная платформа, которая позволяет пользователям регистрироваться, управлять своим виртуальным портфелем фиатных и криптовалют, совершать сделки по покупке/продаже, а также отслеживать актуальные курсы в реальном времени.

## Установка

poetry install

make install


## Запуск 
make project

poetry run project

## Команды 
register --username <name> --password <pass> - регистрация

login --username <name> --password <pass> - вход

show-portfolio [--base <currency>] - показать портфель

buy --currency <code> --amount <sum> - купить валюту

sell --currency <code> --amount <sum> - продать валюту

get-rate --from <currency> --to <currency> - получить курс


## Демонстрация процесса работы и основных команд: 
https://asciinema.org/a/GmqudmdoK0XKFCAUoY2LlRfbu


## Структура проекта:

finalproject_Pankratova_Anastasiya_M55-255
├── data/
│    ├── users.json          
│    ├── portfolios.json       
│    ├── rates.json               # локальный кэш для Core Service
│    └── exchange_rates.json      # хранилище Parser Service (исторические данные).json            
├── valutatrade_hub/
│    ├── __init__.py
│    ├── logging_config.py         
│    ├── decorators.py            
│    ├── core/
│    │    ├── __init__.py
│    │    ├── currencies.py         
│    │    ├── exceptions.py         
│    │    ├── models.py           
│    │    ├── usecases.py          
│    │    └── utils.py             
│    ├── infra/
│    │    ├─ __init__.py
│    │    ├── settings.py           
│    │    └── database.py          
│    ├── parser_service/
│    │    ├── __init__.py
│    │    ├── config.py             # конфигурация API и параметров обновления
│    │    ├── api_clients.py        # работа с внешними API
│    │    ├── updater.py            # основной модуль обновления курсов
│    │    ├── storage.py            # операции чтения/записи exchange_rates.json
│    │    └── scheduler.py          # планировщик периодического обновления
│    └── cli/
│         ├─ __init__.py
│         └─ interface.py     
│
├── main.py
├── Makefile
├── poetry.lock
├── pyproject.toml
├── README.md
└── .gitignore     


## Запуск линтера

poetry run ruff check .

## Автор 

Анастасия Панкратова группа M25-555
