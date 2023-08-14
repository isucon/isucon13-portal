# isucon13-portal

ISUCON13 Portal

## Requirements

* Python3.11
* pipenv

## Getting Started

ローカル環境では、SQLite3を利用して開発をすることができます。

```bash
git clone git@github.com:chibiegg/isucon13-portal.git
cd isucon13-portal
pipenv install
pipenv run python manage.py migrate
pipenv run python manage.py runserver
```
