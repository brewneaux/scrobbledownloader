from sqlalchemy import create_engine
from unittest import TestCase


class SqlTestCase(TestCase):
    def setUpClass(cls) -> None:
        cls.engine = create_engine('sqlite://')

    def tearDownClass(cls) -> None:
        cls.engine.dispose()