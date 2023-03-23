from typing import Any, Optional, Dict, List
import csv
from pathlib import Path
import logging

from django.core.management.base import BaseCommand, CommandParser
from django.conf import settings

from reviews.models import (User, Category, Genre, Title,
                            GenreTitle, Review, Comment)


logger = logging.getLogger(__name__)


class CsvToDb:
    """
    To add a new model, write the csv_to_model_name method.
    The order of the methods is important,
    tables will be added in this order.
    """

    @classmethod
    def parse_tables(cls, tables: List[str], path: str) -> None:
        for table in tables:
            file_path = Path(path, f'{table}.csv')
            with open(file_path, encoding='utf-8-sig') as fp:
                reader = csv.reader(fp, delimiter=",", quotechar='"')
                headers = next(reader, None)
                data = [
                    {header: row[i] for i, header in enumerate(headers)}
                    for row in reader]
                getattr(cls, f'csv_to_{table}')(data)

    @classmethod
    def get_avaiable_tables(cls) -> List[str]:
        """Returns avaiables tables."""
        result = []
        for key in cls.__dict__.keys():
            if key.startswith('csv_to_'):
                result.append(key.replace('csv_to_', ''))
        return result

    @classmethod
    def sort_tables(cls, tables: List[str]) -> List[str]:
        avaiable_tables = cls.get_avaiable_tables()
        order = {table: i for i, table in enumerate(avaiable_tables)}
        return sorted(tables, key=lambda x: order.get(x, float('inf')))

    @classmethod
    def csv_to_users(cls, data: List[Dict[str, str]]) -> None:
        for instance in data:
            user, status = User.objects.get_or_create(
                id=instance['id'],
                username=instance['username'],
                email=instance['email'],
                role=instance['role'],
                bio=instance['bio'],
                first_name=instance['first_name'],
                last_name=instance['last_name']
            )
            created = 'created' if status else 'not created'
            logger.info(f'User {user} is {created}')

    @classmethod
    def csv_to_category(cls, data: List[Dict[str, str]]) -> None:
        for instance in data:
            category, status = Category.objects.get_or_create(
                id=instance['id'],
                name=instance['name'],
                slug=instance['slug']
            )
            created = 'created' if status else 'not created'
            logger.info(f'Category {category} is {created}')

    @classmethod
    def csv_to_genre(cls, data: List[Dict[str, str]]) -> None:
        for instance in data:
            genre, status = Genre.objects.get_or_create(
                id=instance['id'],
                name=instance['name'],
                slug=instance['slug']
            )
            created = 'created' if status else 'not created'
            logger.info(f'Genre {genre} is {created}')

    @classmethod
    def csv_to_titles(cls, data: List[Dict[str, str]]) -> None:
        for instance in data:
            category = Category.objects.get(pk=instance['category'])
            title, status = Title.objects.get_or_create(
                id=instance['id'],
                name=instance['name'],
                year=instance['year'],
                category=category
            )
            created = 'created' if status else 'not created'
            logger.info(f'Title {title} is {created}')

    @classmethod
    def csv_to_genre_title(cls, data: Dict[str, str]) -> bool:
        for instance in data:
            genre = Genre.objects.get(pk=instance['genre_id'])
            title = Title.objects.get(pk=instance['title_id'])
            genre_title, status = GenreTitle.objects.get_or_create(
                id=instance['id'],
                genre=genre,
                title=title
            )
            created = 'created' if status else 'not created'
            logger.info(f'GenreTitle {genre_title} is {created}')

    @classmethod
    def csv_to_review(cls, data: Dict[str, str]) -> bool:
        for instance in data:
            title = Title.objects.get(pk=instance['title_id'])
            author = User.objects.get(pk=instance['author'])
            review, status = Review.objects.get_or_create(
                id=instance['id'],
                title=title,
                text=instance['text'],
                author=author,
                score=instance['score'],
                pub_date=instance['pub_date']
            )
            created = 'created' if status else 'not created'
            logger.info(f'Review {review} is {created}')

    @classmethod
    def csv_to_comments(cls, data: Dict[str, str]) -> bool:
        for instance in data:
            review = Review.objects.get(pk=instance['review_id'])
            author = User.objects.get(pk=instance['author'])
            comment, status = Comment.objects.get_or_create(
                id=instance['id'],
                review=review,
                text=instance['text'],
                author=author,
                pub_date=instance['pub_date']
            )
            created = 'created' if status else 'not created'
            logger.info(f'Comment {comment} is {created}')


class Command(BaseCommand):
    help = '''
    Fills db from csv.
    Add csv files in STATIC/data.
    Names must be similar to model names.
    '''

    def add_arguments(self, parser: CommandParser) -> None:
        choices = CsvToDb.get_avaiable_tables().append('all')
        parser.add_argument('tables', nargs='+', type=str,
                            choices=choices, default='all')

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        path = (settings.BASE_DIR / 'static/data')
        if 'all' in options['tables']:
            tables = CsvToDb.get_avaiable_tables()
        else:
            tables = CsvToDb.sort_tables(options['tables'])
        CsvToDb.parse_tables(tables, path)
