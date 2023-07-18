### Описание проекта:

Проект Foodgram - "Продуктовый помощник". 
На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

### Стэк технологий:

- Python
- Django
- DRF
- React
- Nginx
- PostgreSQL

### Как запустить проект:

Клонировать репозиторий:
```
git clone https://github.com/ponomarev-iv1986/foodgram-project-react.git
```

Подготовить сервер:
```
scp docker-compose.yml <username>@<host>:/home/<username>/
scp nginx.conf <username>@<host>:/home/<username>/
scp .env <username>@<host>:/home/<username>/
```

Установить docker и docker-compose:
```
sudo apt install docker.io 
sudo apt install docker-compose
```

Собрать контейнер и выполнить миграции:
```
sudo docker-compose up -d --build
sudo docker-compose exec backend python manage.py migrate
```

Создать суперюзера и собрать статику:
```
sudo docker-compose exec backend python manage.py createsuperuser
sudo docker-compose exec backend python manage.py collectstatic --no-input
```

Для того, чтобы наполнить БД ингредиентами, выполнить команду:
```
sudo docker-compose exec backend python manage.py load_ingredients --path 'data/ingredients.json'
```

![yamdb_workflow](https://github.com/ponomarev-iv1986/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)