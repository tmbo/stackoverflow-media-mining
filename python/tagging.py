from nltk.corpus import conll2000
import nltk
from nltk.chunk.util import conlltags2tree
from nltk.stem.snowball import EnglishStemmer


class TextChunker:
    contractionReplacements = {"'s" : "is", "n't" : "not", "'ll" : "will", "'m": "am", "'re": "are", "'ve": "have", "'d" : "had"}

    def __init__(self, stemChunks):
        train_sents = conll2000.chunked_sents('train.txt', chunk_types=['VP', 'NP'])
        print "Training chunker..."
        self.chunker = BigramChunker(train_sents)
        print "Finished training chunker..."
        self.stemChunks = stemChunks
        if stemChunks:
            self.stemmer = EnglishStemmer()


    def chunkText(self, rawtext):
        sentences = nltk.sent_tokenize(rawtext) # NLTK default sentence segmenter
        tokenized = [nltk.word_tokenize(sent) for sent in sentences] # NLTK word tokenizer
        postagged = [nltk.pos_tag(tokens) for tokens in tokenized] # NLTK POS tagger
        for tagged in postagged:
            for chunk in self.extractChunks(self.chunker.parse(tagged), exclude=["NP", ".", ":", "(", ")"]):
                if len(chunk) >= 2:
                    yield chunk


    def extractChunks(self, tree, exclude):
        def traverse(tree):
            try:
                tree.node
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
                if tree.node in exclude:
                    return []
                else:
                    return [word for child in tree for word in traverse(child)]
        for child in tree:
            traversed = traverse(child)
            if len(traversed) > 0:
                if self.stemChunks:
                    yield " ".join(map(lambda token: self.stemmer.stem(token.decode('utf-8')), traversed))
                else:
                    yield " ".join(traversed)


class BigramChunker(nltk.ChunkParserI):
    def __init__(self, train_sents):
        train_data = [[(t, c) for w, t, c in nltk.chunk.tree2conlltags(sent)]
                      for sent in train_sents]
        self.tagger = nltk.BigramTagger(train_data)

    def parse(self, sentence):
        pos_tags = [pos for (word, pos) in sentence]
        tagged_pos_tags = self.tagger.tag(pos_tags)
        chunktags = [chunktag for (pos, chunktag) in tagged_pos_tags]
        conlltags = [(word, pos, chunktag) for ((word, pos), chunktag)
                     in zip(sentence, chunktags)]
        return conlltags2tree(conlltags)