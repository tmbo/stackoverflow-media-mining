import nltk
from syllablecounter import cmusyllables

_syl_counter = cmusyllables()

class TextStatistics(object):
    def __init__(self, text):
        global _syl_counter

        self.text = text

        self.syl_counter = _syl_counter

        sentences = nltk.sent_tokenize(text)
        words = [token for sent in sentences for token in nltk.word_tokenize(sent) if len(token) >= 2 or token.lower() == "i"]

        self.syllables_per_word = self.count_syllables(words)

        self.num_syllables = sum(self.syllables_per_word)
        self.num_chars = self._count_characters(text)
        self.num_words = len(words)
        self.num_sentences = len(sentences)
        self.num_polysyllables = \
            len(filter(lambda num_word_syllables: num_word_syllables >= 3, self.syllables_per_word))

    def _count_characters(self):
        count = 0
        punctuation = ['.', ',', '!', '?', ';', ':']
        for c in self.text:
            if c.isalnum or c in punctuation:
                count += 1
        return count

    def avg_words(self):
        return self.num_words / self.num_sentences if self.num_sentences > 0 else 0

    def avg_chars(self):
        return self.num_chars / self.num_words if self.num_words > 0 else 0

    def automated_readability_index(self):
        try:
            return 4.71 * (self.num_chars / self.num_words) + 0.5 * (self.num_words / self.num_sentences) - 21.43
        except ZeroDivisionError:
            return 0

    def coleman_liau_index(self):
        try:
            return 0.0588 * \
                   (self.num_chars * 100 / self.num_words) - 0.296 * (self.num_sentences * 100 / self.num_words) - 15.8
        except ZeroDivisionError:
            return 0

    def flesch_reading_ease(self):
        try:
            return 206.835 - \
                   1.015 * (self.num_words / self.num_sentences) - 84.6 * (self.num_syllables / self.num_words)
        except ZeroDivisionError:
            return 0

    def gunning_fog_index(self):
        try:
            return 0.4 * (self.num_words / self.num_sentences + 100 * self.num_polysyllables / self.num_words)

        except ZeroDivisionError:
            return 0

    def count_syllables(self, words):
        return [self.syl_counter.SyllableCount(word) for word in words]
