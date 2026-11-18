import unittest
from robot.polite import polite_documents

class PoliteTests(unittest.TestCase):
    def test_polite_words_bilingual(self):
        self.assertEqual(polite_documents('gracias obrigado')[0]['id'], 'thanks')
        self.assertEqual(polite_documents('por favor pedir educadamente')[0]['id'], 'please')

    def test_unrelated_text_has_no_polite_document(self):
        self.assertEqual(polite_documents('como atravessar a rua'), [])
