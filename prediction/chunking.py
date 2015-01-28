from nltk.chunk import tree2conlltags
from nltk.corpus import conll2000
from nltk import sent_tokenize, word_tokenize, pos_tag, UnigramTagger, ChunkParserI
from nltk.chunk.util import conlltags2tree
from nltk.stem.snowball import EnglishStemmer
import multiprocessing
import datetime
import nltk
from nltk.corpus import conll2000
from sklearn.svm import  LinearSVC, SVC
from nltk.classify.scikitlearn import SklearnClassifier

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
        self.chunker = NPChunker(train_sents)
        print "Finished training chunker..."

    def chunk_text(self, rawtext):
        if self.chunker is None:
            raise Exception("Text chunker needs to be trained before it can be used.")
        sentences = sent_tokenize(rawtext)  # NLTK default sentence segmenter
        tokenized = [word_tokenize(sent) for sent in sentences]  # NLTK word tokenizer
        postagged = [pos_tag(tokens) for tokens in tokenized]  # NLTK POS tagger
        for tagged in postagged:
            for chunk in self._extract_chunks(self.chunker.parse(tagged), exclude=["NP", ".", ":", "(", ")"]):
                if len(chunk) >= 2:
                    yield chunk

    def _extract_chunks(self, tree, exclude):
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
        self.tagger = UnigramTagger(train_data)

    def parse(self, sentence):
        pos_tags = [pos for (word, pos) in sentence]
        tagged_pos_tags = self.tagger.tag(pos_tags)
        chunk_tags = [chunk_tag for (pos, chunk_tag) in tagged_pos_tags]
        conll_tags = [(word, pos, chunk_tag) for ((word, pos), chunk_tag) in zip(sentence, chunk_tags)]
        return conlltags2tree(conll_tags)

class NPChunker(nltk.ChunkParserI):
    """Chunk text into shallow NP trees using IOB parser."""
    def __init__(self, train_sents):
        start_time = datetime.datetime.now()
        print('Training started: {0}'.format(start_time))
        tagged_sents = [[((w,t),c) for (w,t,c) in
                         nltk.chunk.tree2conlltags(sent)]
                        for sent in train_sents]
        self.tagger = LinearSVCIOBChunkTagger(tagged_sents)
        end_time = datetime.datetime.now()
        print('Training complete: {0}'.format(end_time))
        print('Time spent training: {0}'.format(end_time - start_time))

    def parse(self, sentence):
        tagged_sents = self.tagger.tag(sentence)
        conlltags = [(w,t,c) for ((w,t),c) in tagged_sents]
        return nltk.chunk.conlltags2tree(conlltags)


class BaseIOBChunkTagger(nltk.TaggerI):
    """Base class for IOB taggers. Defines tag method."""
    def tag(self, sentence):
        history = []
        for i, word in enumerate(sentence):
            featureset = npchunk_features(sentence, i, history)
            tag = self.classifier.classify(featureset)
            history.append(tag)
        return zip(sentence, history)

def extract_features(train_sents):
    """"Extract features from training data."""
    train_set = []
    for tagged_sent in train_sents:
        untagged_sent = nltk.tag.untag(tagged_sent)
        history = []
        for i, (word, tag) in enumerate(tagged_sent):
            featureset = npchunk_features(untagged_sent, i, history)
            train_set.append( (featureset, tag) )
            history.append(tag)
    return train_set

def tags_since_dt(sentence, i):
    """Get all tags after a determiner as a
       classification feature."""
    tags = set()
    for word, pos in sentence[:i]:
        if pos == 'DT':
            tags = set()
        else:
            tags.add(pos)
    return '+'.join(sorted(tags))

def npchunk_features(sentence, i, history):
    """Extract features for classification."""
    word, pos = sentence[i]
    if i == 0:
        prevword, prevpos = "<START>", "<START>"
        previob = "<START>"
    else:
        prevword, prevpos = sentence[i - 1]
        previob = history[i - 1]
    if i == len(sentence) - 1:
        nextword, nextpos = "<END>", "<END>"
    else:
        nextword, nextpos = sentence[i+1]
    return {"word": word,
            "prevword": prevword,
            "nextword": nextword,
            "pos": pos,
            "prevpos": prevpos,
            "nextpos": nextpos,
            "previob": previob,
            "prevpos+pos": "%s+%s" % (prevpos, pos),
            "pos+nextpos": "%s+%s" % (pos, nextpos),
            "tags-since-dt": tags_since_dt(sentence, i)}

class LinearSVCIOBChunkTagger(BaseIOBChunkTagger):
    """IOB tagger using the scikit-learn LinearSVC classifier."""
    def __init__(self, train_sents):
        train_set = extract_features(train_sents)
        print train_set[0]
        self.classifier = SklearnClassifier(LinearSVC()).train(train_set)