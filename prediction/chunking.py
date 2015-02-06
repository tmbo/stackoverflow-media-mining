import nltk
from nltk.chunk import tree2conlltags
from nltk import sent_tokenize, word_tokenize, pos_tag, BigramTagger, ChunkParserI
from nltk.chunk.util import conlltags2tree
from nltk.stem.snowball import EnglishStemmer
import multiprocessing
from nltk.corpus import conll2000

class TextChunker:
    contractionReplacements = {"'s": "is", "n't": "not", "'ll": "will", "'m": "am", "'re": "are", "'ve": "have",
                               "'d": "had"}

    def __init__(self, stem_chunks):
        self.stem_chunks = stem_chunks
        self.chunker = None
        if stem_chunks:
            self.stemmer = EnglishStemmer()

    def train(self):
        train_sents = conll2000.chunked_sents('train.txt', chunk_types=['VP', 'NP'])
        print "Training chunker..."
        self.chunker = BigramChunker(train_sents)
        print "Finished training chunker..."

    def chunk_text(self, rawtext):
        if self.chunker is None:
            raise Exception("Text chunker needs to be trained before it can be used.")
        sentences = sent_tokenize(rawtext.lower())  # NLTK default sentence segmenter
        tokenized = [word_tokenize(sent) for sent in sentences]  # NLTK word tokenizer
        postagged = [pos_tag(tokens) for tokens in tokenized]  # NLTK POS tagger
        for tagged in postagged:
            for chunk in self._extract_chunks(self.chunker.parse(tagged), exclude=["NP", ".", ":", "(", ")"]):
                if len(chunk) >= 2:
                    yield chunk

    def _extract_chunks(self, tree, exclude):
        def traverse(tree):
            try:
                if nltk.__version__ == "2.0.4":
                    tree.node
                else:
                    tree.label()
            except AttributeError:
                if tree[1] in exclude or tree[0] in exclude or (tree[0] != "to" and tree[0] == tree[1]):
                    return []
                else:
                    # we don't want to have "'s" or "n't" in the chunks
                    if tree[0] in self.contractionReplacements:
                        return [self.contractionReplacements[tree[0]]]
                    else:
                        return [tree[0]]
            else:
                if nltk.__version__ == "2.0.4":
                    node = tree.node
                else:
                    node = tree.label()
                if node in exclude:
                    return []
                else:
                    return [word for child in tree for word in traverse(child)]

        for child in tree:
            traversed = traverse(child)
            if len(traversed) > 0:
                if self.stem_chunks:
                    yield " ".join(map(lambda token: self.stemmer.stem(token.decode('utf-8')), traversed))
                else:
                    yield " ".join(traversed)


class MultithreadedTextChunker(TextChunker):
    def __init__(self, stem_chunks):
        super(MultithreadedTextChunker, self).__init__(stem_chunks)

    def chunk_texts(self, texts):
        pool = multiprocessing.Pool()
        result = list(pool.map(self.chunk_text, texts))
        pool.terminate()
        return result


class BigramChunker(ChunkParserI):
    def __init__(self, train_sentences):
        train_data = [[(t, c) for w, t, c in tree2conlltags(sent)]
                      for sent in train_sentences]
        self.tagger = BigramTagger(train_data)

    def parse(self, sentence):
        pos_tags = [pos for (word, pos) in sentence]
        tagged_pos_tags = self.tagger.tag(pos_tags)
        chunk_tags = [chunk_tag for (pos, chunk_tag) in tagged_pos_tags]
        conll_tags = [(word, pos, chunk_tag) for ((word, pos), chunk_tag) in zip(sentence, chunk_tags)]
        return conlltags2tree(conll_tags)