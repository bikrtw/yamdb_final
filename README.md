# yamdb_final
![Test, build & deploy](https://github.com/bikrtw/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

Api сервис для сбора отзывов на книги, фильмы (теперь и в контейнерном исполнении!)
Финальный проект спринта "Инфраструктура". Яндекс Практикум, 29 когорта

Проект автоматически разворачивается в облаке.

Проверить работоспособность можно перейдя по адресу: http://84.252.136.64/admin/

### Как запустить проект у себя в контейнере:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/bikrtw/yamdb_final.git
cd yamdb_final
```

Перейти в директорию, содержащую файл docker-compose.yaml:

```
cd infra
```

Запустить docker-compose

```
docker-compose up -d
```

Выполнить миграции и собрать статику:

```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --no-input
```

Восстановить базу из бекапа:

```
docker-compose exec web python manage.py loaddata dump.json
```

Профит!

## Содержимое файла .env:
```
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=password # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД 
```
