import unittest
from robot.practice import VocabularyPractice


class PracticeTests(unittest.TestCase):
    def test_natural_invitations_and_transcribed_name_start_without_a_gesture(self):
        for text in ('Acole, vamos praticar?', 'Acolhe, vamos praticar?',
                     'Vamos aprender uma palavra.', 'Quero aprender uma palavra!',
                     'Pode me ensinar uma palavra?', 'Vamos praticar português?'):
            with self.subTest(text=text):
                result=VocabularyPractice().respond(text)
                self.assertIsNotNone(result)
                self.assertIn('hola',result['answer'])
                self.assertIsNone(result['correct'])

    def test_negated_and_unclear_invitations_do_not_start_an_activity(self):
        for text in ('Não vamos praticar', 'Não quero aprender uma palavra',
                     'Você disse vamos praticar?', 'Vamos MinSini!'):
            with self.subTest(text=text):
                self.assertIsNone(VocabularyPractice().respond(text))

    def test_three_words_and_retry(self):
        practice=VocabularyPractice()
        first=practice.respond('Acolhe, vamos praticar!')
        self.assertIn('hola',first['answer'])
        self.assertIsNone(first['correct'])
        wrong=practice.respond('livro')
        self.assertFalse(wrong['correct']);self.assertIn('olá',wrong['answer'])
        self.assertTrue(practice.respond('Olá')['correct'])
        self.assertTrue(practice.respond('cadeira')['correct'])
        end=practice.respond('garrafa')
        self.assertTrue(end['correct']);self.assertTrue(end['finished'])
        self.assertIsNone(practice.respond('oi'))

    def test_questions_and_negation_do_not_count_as_answers(self):
        practice=VocabularyPractice();practice.respond('Vamos praticar')
        for text in ('Qual é a temperatura?','Qual é seu nome','Não mova a cabeça','Como atravessar a rua?','Não.','Obrigado','Sim'):
            self.assertIsNone(practice.respond(text),text)
        self.assertTrue(practice.respond('oi')['correct'])

    def test_hint_repeat_cancel_and_reset(self):
        practice=VocabularyPractice();practice.respond('Vamos praticar')
        for text in ('Não sei','Repita a pergunta'):
            result=practice.respond(text);self.assertIsNone(result['correct']);self.assertIn('hola',result['answer'])
        self.assertTrue(practice.respond('Encerrar atividade')['finished'])
        self.assertIsNone(practice.respond('olá'))
        practice.respond('Vamos praticar');practice.reset()
        self.assertIsNone(practice.respond('olá'))
