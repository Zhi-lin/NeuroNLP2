__author__ = 'max'

from collections import OrderedDict
import pickle
import numpy as np
from gensim.models.word2vec import Word2Vec
import gzip
import os

from neuronlp2.io.logger import get_logger
from neuronlp2.io.alphabet import Alphabet
from neuronlp2.io.common import DIGIT_RE
from neuronlp2.io.common import PAD, ROOT, END


def load_embedding_dict(embedding, embedding_path, normalize_digits=True):
    """
    load word embeddings from file
    :param embedding:
    :param embedding_path:
    :return: embedding dict, embedding dimention, caseless
    """
    print("loading embedding: %s from %s" % (embedding, embedding_path))
    if embedding == 'word2vec':
        # loading word2vec
        word2vec = Word2Vec.load_word2vec_format(embedding_path, binary=True)
        embedd_dim = word2vec.vector_size
        return word2vec, embedd_dim
    elif embedding == 'glove':
        # loading GloVe
        embedd_dim = -1
        embedd_dict = OrderedDict()
        with gzip.open(embedding_path, 'rt') as file:
            for line in file:
                line = line.strip()
                if len(line) == 0:
                    continue

                tokens = line.split()
                if embedd_dim < 0:
                    embedd_dim = len(tokens) - 1
                else:
                    assert (embedd_dim + 1 == len(tokens))
                embedd = np.empty([1, embedd_dim], dtype=np.float32)
                embedd[:] = tokens[1:]
                word = DIGIT_RE.sub("0", tokens[0]) if normalize_digits else tokens[0]
                embedd_dict[word] = embedd
        return embedd_dict, embedd_dim
    elif embedding == 'senna':
        # loading Senna
        embedd_dim = -1
        embedd_dict = OrderedDict()
        with gzip.open(embedding_path, 'rt') as file:
            for line in file:
                line = line.strip()
                if len(line) == 0:
                    continue

                tokens = line.split()
                if embedd_dim < 0:
                    embedd_dim = len(tokens) - 1
                else:
                    assert (embedd_dim + 1 == len(tokens))
                embedd = np.empty([1, embedd_dim], dtype=np.float32)
                embedd[:] = tokens[1:]
                word = DIGIT_RE.sub("0", tokens[0]) if normalize_digits else tokens[0]
                embedd_dict[word] = embedd
        return embedd_dict, embedd_dim
    elif embedding == 'sskip':
        embedd_dim = -1
        embedd_dict = OrderedDict()
        with gzip.open(embedding_path, 'rt') as file:
            # skip the first line
            file.readline()
            for line in file:
                line = line.strip()
                try:
                    if len(line) == 0:
                        continue

                    tokens = line.split()
                    if len(tokens) < embedd_dim:
                        continue

                    if embedd_dim < 0:
                        embedd_dim = len(tokens) - 1

                    embedd = np.empty([1, embedd_dim], dtype=np.float32)
                    start = len(tokens) - embedd_dim
                    word = ' '.join(tokens[0:start])
                    embedd[:] = tokens[start:]
                    word = DIGIT_RE.sub("0", word) if normalize_digits else word
                    embedd_dict[word] = embedd
                except UnicodeDecodeError:
                    continue
        return embedd_dict, embedd_dim
    elif embedding == 'polyglot':
        words, embeddings = pickle.load(open(embedding_path, 'rb'), encoding='latin1')
        _, embedd_dim = embeddings.shape
        embedd_dict = OrderedDict()
        for i, word in enumerate(words):
            embedd = np.empty([1, embedd_dim], dtype=np.float32)
            embedd[:] = embeddings[i, :]
            word = DIGIT_RE.sub("0", word) if normalize_digits else word
            embedd_dict[word] = embedd
        return embedd_dict, embedd_dim

    else:
        raise ValueError("embedding should choose from [word2vec, senna, glove, sskip, polyglot]")


def create_alphabet_from_embedding(alphabet_directory, embedd_dict, vocabs, max_vocabulary_size=100000):
    _START_VOCAB = [PAD, ROOT, END]
    logger = get_logger("Create Pretrained Alphabets")
    pretrained_alphabet = Alphabet('pretrained', defualt_value=True)
    file = os.path.join(alphabet_directory, 'pretrained.json')
    if not os.path.exists(file):
        logger.info("Creating Pretrained Alphabets: %s" % alphabet_directory)
        pretrained_alphabet.add(PAD)
        pretrained_alphabet.add(ROOT)
        pretrained_alphabet.add(END)

        pretrained_vocab = list(embedd_dict.keys())
        n_oov = 0
        for word in vocabs:
            if word in pretrained_vocab:
                pretrained_alphabet.add(word)
            elif word.lower() in pretrained_vocab:
                pretrained_alphabet.add(word.lower())
            elif word not in _START_VOCAB:
                n_oov += 1
        #vocab_size = min(len(pretrained_vocab), max_vocabulary_size)
        logger.info("Loaded/Total Pretrained Vocab Size: %d/%d, OOV Words: %d" % (pretrained_alphabet.size(),len(pretrained_vocab),n_oov))
        
        pretrained_alphabet.save(alphabet_directory)
    else:
        pretrained_alphabet.load(alphabet_directory)
        #pretrained_vocab = list(embedd_dict.keys())
        #vocab_size = min(len(pretrained_vocab), max_vocabulary_size)
        #assert pretrained_alphabet.size() == (vocab_size + 4)
        
    pretrained_alphabet.close()

    return pretrained_alphabet