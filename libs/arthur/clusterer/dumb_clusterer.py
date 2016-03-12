"""
Module containing DumbClusterer class.

This class is not very smart, as the name suggests. It basically cluster the words inside
a document using classical algorithm.
"""
import os, sys, inspect
# This needs to be included here to ensure path loaded from arthur library directory.
base_path = os.path.realpath(
    os.path.abspath(
        os.path.join(
            os.path.split(
                inspect.getfile(
                    inspect.currentframe()
                )
            )[0],
            '..'
        )
    )
)
sys.path.append(base_path)

import nltk
import string
import numpy as np
from nltk.corpus.reader.plaintext import PlaintextCorpusReader
from nltk.collocations import BigramAssocMeasures, TrigramAssocMeasures, BigramCollocationFinder, TrigramCollocationFinder
from nltk import word_tokenize
from nltk.tokenize import MWETokenizer
from document import ArthurDocument

# Todo: Change to more robust algorithm
class DumbClusterer():
    """A rather dumb clusterer. 
    """
    def __init__(self, corpus_dir=None, mwes=[], setup_mwes=True, **kwargs):
        self.mwes = mwes
        if corpus_dir is not None:
            self.setup_corpus(corpus_dir, '.*')
            if setup_mwes:
                self.setup_mwes(**kwargs)

    def setup_corpus(self, corpus_dir, paths='.*'):
        """Setting up a corpus.

        Args:
            corpus_dir(str): Path to corpus directory.
        """
        self.corpus = PlaintextCorpusReader(corpus_dir, paths)
        return self.corpus

    def extract_expressions(self, document, features=None):
        """Returns expressions from given features and multi-word expressions.
        
        In addition to passing a document into this method, MWEs or Multi-Word Expressions
        can be given to treat some multi words as one expression.

        >>> from document import ArthurDocument
        >>> pdf_path = base_path + '/test/test.pdf'
        >>> with open(pdf_path, 'rb') as f:
        ...     document = ArthurDocument(f.read())
        >>> features = document.get_features()[730:816,:]
        >>> print(document.get_text(features)) # doctest:+ELLIPSIS
        VICTORIA'S CROWN JEWEL OF WATERFRONT ESTATES. Nestled on a quiet cove in the exclusive

        Multi-word expression should be detected:
        >>> clusterer = DumbClusterer(mwes=['crown jewel', 'waterfront estates'])
        >>> expressions = clusterer.extract_expressions(document, features)
        >>> print(expressions[2]['text'])
        CROWN JEWEL

        x position should equal x of "C" from "CROWN JEWEL" :
        >>> expressions[2]['x'] == features[11, ArthurDocument.get_feature_id('x')]
        True

        and width should equal to width of "CROWN JEWEL":
        >>> expr_width = expressions[2]['x1']-expressions[2]['x']
        >>> ftr_width = features[21, ArthurDocument.get_feature_id('x1')] - features[11, ArthurDocument.get_feature_id('x')]
        >>> expr_width == ftr_width
        True

        Args:
            document(ArthurDocument): Document to extract data fields from.
            features(list): List of features containing data fields to extract. If not given, use
                            all document features.
            mwes(list): List of Multi-Word Expressions. Example value:
                        `['property type', 'single family)]`. With that list, both "property type"
                        and "single family" will each be treated as single expressions.        
        Returns:
            np.array: An array of data_fields.
        """
        mwes = self.mwes
        if features is None:
            features = document.get_features()
        text = document.get_text(features)
        for idx, mwe in enumerate(mwes):
            if isinstance(mwe, str):
                mwes[idx] = word_tokenize(mwe.lower())
            elif hasattr(mwe, '__iter__'):
                mwes[idx] = [x.lower() for x in mwe]
        tokenizer = MWETokenizer(mwes, separator=' ')
        tokenized = tokenizer.tokenize(word_tokenize(text.lower()))

        expressions = []
        pos = 0
        for token in tokenized:
            # token could be "deez nutz" but text contains multiple spaces e.g. "deez  nutz",
            # so we need to split the token and find position of first and last characters.
            words = token.split()
            start_pos = text.lower().index(words[0], pos)
            for word in words:
                ipos = text.lower().index(word, pos)
                end_pos = ipos + len(word)
            pos = end_pos
            min_x = 0
            max_x = 0
            min_y = 0
            max_y = 0
            page = 0
            if len(features[start_pos:end_pos,:] > 0):
                min_x =  np.amin(features[start_pos:end_pos,:], axis=0)[ArthurDocument.get_feature_id('x')]
                max_x =  np.amax(features[start_pos:end_pos,:], axis=0)[ArthurDocument.get_feature_id('x1')]
                min_y =  np.amin(features[start_pos:end_pos,:], axis=0)[ArthurDocument.get_feature_id('y')]
                max_y =  np.amax(features[start_pos:end_pos,:], axis=0)[ArthurDocument.get_feature_id('y1')]
                page = features[start_pos, ArthurDocument.get_feature_id('page')]

            expressions.append({
                'text': text[start_pos:end_pos],
                'x': min_x,
                'x1': max_x,
                'y': min_y,
                'y1': max_y,
                'page': page
            })
        return expressions

    def setup_mwes(self, trigram_nbest=100, bigram_nbest=2000):
        """Create multi-word expressions by learning a corpus located in a corpus directory.

        Testing setting up mwes with custom path and setting it up twice (correct when no exception):
        >>> corpus_dir = os.path.join(base_path, 'test', 'corpus')
        >>> clusterer = DumbClusterer(corpus_dir=corpus_dir, mwes=['custom mwe'])
        >>> mwes = clusterer.setup_mwes(trigram_nbest=1000, bigram_nbest=15000)
        >>> 'custom mwe' not in mwes
        True

        >>> 'custom mwe' in clusterer.mwes
        True

        Args:
            trigram_nbest(int): Number of highest ranked trigrams to acquire.
            bigram_nbest(int): Number of highest ranked trigrams to acquire.
        Returns:
            list: List of multi-word expressions.
        """
        if self.corpus is None:
            raise Exception("Corpus not found. Run method `setup_corpus` with given corpus directory first.")

        bigram_measures = BigramAssocMeasures()
        trigram_measures = TrigramAssocMeasures()

        # Following are not used since ne chunk takes too much time.
        # Text processing before bigrams and trigrams calculated
        # words = []
        # for sent in self.corpus.sents():
        #     for chunk in nltk.ne_chunk(nltk.pos_tag(sent)):
        #         if not isinstance(chunk, nltk.Tree):
        #             w = chunk[0]
        #             # - Removal of words containing numbers or punctuations
        #             if not any((ch.isdigit() or ch in string.punctuation) for ch in w):
        #                 # - Lowercasing all words
        #                 words.append(w.lower())
        #                 print(w.lower().encode("utf-8")),

        # Text processing before bigrams and trigrams calculated
        words = []
        for w in self.corpus.words():
            # - Removal of words containing numbers or punctuations
            if not any((ch.isdigit() or ch in string.punctuation) for ch in w):
                # - Lowercasing all words
                words.append(w.lower())

        bigram_finder = BigramCollocationFinder.from_words(words)
        trigram_finder = TrigramCollocationFinder.from_words(words)
        mwes = trigram_finder.nbest(trigram_measures.pmi, trigram_nbest) + bigram_finder.nbest(bigram_measures.pmi, bigram_nbest)
        # Basically combining two list by turning them into sets to make sure union returned 
        # i.e. `set1 | set2` where set1 could be list of string or list, and if the latter, they
        # need to be converted into sets.
        set1 = {(tuple(mwe) if isinstance(mwe,list) else mwe) for mwe in self.mwes}
        set2 = set(mwes)
        self.mwes = list(set1 | set2)
        return mwes

if __name__ == '__main__':
    import doctest
    doctest.testmod()