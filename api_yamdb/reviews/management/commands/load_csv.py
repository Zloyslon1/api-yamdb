import csv
import os

from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime

from reviews.models import Category, Comment, Genre, Review, Title, User


class Command(BaseCommand):
    help = 'Загружает данные из CSV-файлов в базу данных'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            default='static/data',
            help='Путь к папке с CSV-файлами',
        )

    def handle(self, *args, **options):
        path = options['path']

        self.stdout.write('Загрузка данных...')

        self._load_users(path)
        self._load_simple(path, 'category', Category, ['id', 'name', 'slug'])
        self._load_simple(path, 'genre', Genre, ['id', 'name', 'slug'])
        self._load_titles(path)
        self._load_genre_title(path)
        self._load_reviews(path)
        self._load_comments(path)

        self.stdout.write(self.style.SUCCESS('Все данные загружены'))

    def _load_users(self, path):
        filepath = os.path.join(path, 'users.csv')
        with open(filepath, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            instances = [
                User(
                    id=int(row['id']),
                    username=row['username'],
                    email=row['email'],
                    role=row['role'],
                    bio=row.get('bio', ''),
                    first_name=row.get('first_name', ''),
                    last_name=row.get('last_name', ''),
                )
                for row in reader
            ]
        User.objects.bulk_create(instances, ignore_conflicts=True)
        self.stdout.write(f'  users: {len(instances)} записей')

    def _load_simple(self, path, name, model, fields):
        filepath = os.path.join(path, f'{name}.csv')
        with open(filepath, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            instances = [
                model(**{k: row[k] for k in fields})
                for row in reader
            ]
        model.objects.bulk_create(instances, ignore_conflicts=True)
        self.stdout.write(f'  {name}: {len(instances)} записей')

    def _load_titles(self, path):
        filepath = os.path.join(path, 'titles.csv')
        with open(filepath, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            instances = [
                Title(
                    id=int(row['id']),
                    name=row['name'],
                    year=int(row['year']),
                    category_id=int(row['category']),
                    description='',
                )
                for row in reader
            ]
        Title.objects.bulk_create(instances, ignore_conflicts=True)
        self.stdout.write(f'  titles: {len(instances)} записей')

    def _load_genre_title(self, path):
        filepath = os.path.join(path, 'genre_title.csv')
        with open(filepath, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            through = Title.genre.through
            instances = [
                through(
                    title_id=int(row['title_id']),
                    genre_id=int(row['genre_id']),
                )
                for row in reader
            ]
        through.objects.bulk_create(instances, ignore_conflicts=True)
        self.stdout.write(f'  genre_title: {len(instances)} связей')

    def _load_reviews(self, path):
        filepath = os.path.join(path, 'review.csv')
        with open(filepath, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            instances = [
                Review(
                    id=int(row['id']),
                    title_id=int(row['title_id']),
                    text=row['text'],
                    author_id=int(row['author']),
                    score=int(row['score']),
                    pub_date=parse_datetime(row['pub_date']),
                )
                for row in reader
            ]
        Review.objects.bulk_create(instances, ignore_conflicts=True)
        self.stdout.write(f'  review: {len(instances)} записей')

    def _load_comments(self, path):
        filepath = os.path.join(path, 'comments.csv')
        with open(filepath, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            instances = [
                Comment(
                    id=int(row['id']),
                    review_id=int(row['review_id']),
                    text=row['text'],
                    author_id=int(row['author']),
                    pub_date=parse_datetime(row['pub_date']),
                )
                for row in reader
            ]
        Comment.objects.bulk_create(instances, ignore_conflicts=True)
        self.stdout.write(f'  comments: {len(instances)} записей')
