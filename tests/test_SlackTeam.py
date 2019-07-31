# unittest for SlackTeam class
# requires a postgres DB with an existing table

import unittest
import psycopg2
import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from app import SlackTeam

# database connection
DATABASE_URL = os.environ['DATABASE_URL']

class TestSlackTeam(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls._connection = psycopg2.connect(DATABASE_URL)

    @classmethod
    def tearDownClass(cls):
        # remove test objects from DB
        cursor = cls._connection.cursor()               
        sql_query = """DELETE FROM slack_teams 
            WHERE id IN ('T0TEST01', 'T0TEST02')"""        
        cursor.execute(sql_query)
        cls._connection.commit()
        cursor.close()
        # close DB connection
        cls._connection.close()

    def test_getters(self):
        x = SlackTeam("T0TEST01", "name1", "token1")
        self.assertIsInstance(x, SlackTeam)
        self.assertEqual(x.id, "T0TEST01")
        self.assertEqual(x.name, "name1")
        self.assertEqual(x.token, "token1")


    def test_store(self):
        x = SlackTeam("T0TEST01", "name1", "token1")
        self.assertIsInstance(x, SlackTeam)
        
        x.store(self._connection)
        # store again to verify overwriting existing works
        x.store(self._connection)

        y = SlackTeam("T0TEST02", "name2", "token2")
        self.assertIsInstance(y, SlackTeam)
        y.store(self._connection)

    def test_fetch_normal(self):
        x = SlackTeam("T0TEST01", "name1", "token1")
        self.assertIsInstance(x, SlackTeam)        
        x.store(self._connection)
        
        y = SlackTeam.fetchFromDb(self._connection, "T0TEST01")
        self.assertEqual(x.id, y.id)
        self.assertEqual(x.name, y.name)
        self.assertEqual(x.token, y.token)
    

    def test_fetch_unknown(self):
        y = SlackTeam.fetchFromDb(self._connection, "does_not_exist")
        self.assertIsNone(y)

if __name__ == '__main__':
    unittest.main()