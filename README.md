# Final Project - Currency Wallet
Приложени для управления виртуальным валютным кошельком.

## Установка

make install
poetry install


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

