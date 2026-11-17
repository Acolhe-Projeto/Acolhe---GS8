"""Small curated vocabulary activity; grading never comes from generated text."""
import re
import unicodedata


def normalize(text):
    folded = ''.join(c for c in unicodedata.normalize('NFKD', text.casefold()) if not unicodedata.combining(c))
    return ' '.join(re.sub(r'[,!.:]', ' ', folded).split())


class VocabularyPractice:
    words = (('hola', ('ola', 'oi'), 'olá'), ('silla', ('cadeira',), 'cadeira'),
             ('botella', ('garrafa',), 'garrafa'))

    def __init__(self):
        self.reset()

    def reset(self):
        self.index = None

    def respond(self, text):
        value = normalize(text)
        value = re.sub(r'^(?:acolhe|acole) ', '', value)
        # Question punctuation is accepted for invitations, not for motor commands or grading.
        invitation = value.rstrip(' ?')
        if re.fullmatch(r'(?:(?:vamos|quero) (?:praticar(?: portugues)?|aprender(?: uma palavra)?)|pode me ensinar uma palavra)(?: por favor)?', invitation):
            self.index = 0
            return self._result('Vamos praticar! ' + self._question())
        if self.index is None: return None
        if value in ('encerrar atividade', 'pare a atividade', 'pare', 'parar', 'cancelar'):
            self.reset()
            return self._result('Atividade encerrada. Podemos conversar quando quiser.', finished=True)
        spanish, accepted, portuguese = self.words[self.index]
        if value in ('nao sei', 'repita a pergunta'):
            return self._result(f'Dica: a palavra é {portuguese}. ' + self._question())
        if value in ('nao', 'sim', 'obrigado', 'obrigada', 'tchau', 'qual', 'quem', 'como', 'onde', 'porque'): return None
        # Only a single word is an answer; questions and unrelated conversation keep the activity pending.
        if not re.fullmatch(r'[a-z]+', value): return None
        if value not in accepted:
            return self._result(f'Vamos tentar novamente: {spanish} em português é {portuguese}. Responda só a palavra.', False)
        self.index += 1
        if self.index == len(self.words):
            self.reset()
            return self._result('Muito bem! Você completou as palavras. Para repetir, diga: vamos praticar.', True, True)
        return self._result('Isso mesmo! ' + self._question(), True)

    def _question(self):
        return f'Como se diz {self.words[self.index][0]} em português? Responda só a palavra.'

    @staticmethod
    def _result(answer, correct=None, finished=False):
        return {'answer': answer, 'correct': correct, 'finished': finished}
