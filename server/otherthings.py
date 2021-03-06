import nltk
import string
from heapq import nlargest
from csv import reader

# write a function to summarize a body of text
# it should take a string as input and return a string
# summarizing the text


def load_reliability_data():
    rawdawg = reader(open("reliability.tsv"), delimiter='\t')
    m = {}
    for row in rawdawg:
        m[row[1]] = row[3]
    return m

def summarize(text: str) -> dict:
    dick = 10 if text.count(".") > 10 else 5
    length = int(round(text.count(".") / dick))

    # Remove punctuation
    nopunc = [char for char in text if char not in string.punctuation]
    nopunc = ''.join(nopunc)
    # Remove stopwords
    processed_text = [word for word in nopunc.split() if word.lower() not in nltk.corpus.stopwords.words('english')]

    # Create a dictionary to store word frequency
    word_freq = {}  
    # Enter each word and its number of occurrences
    for word in processed_text:
        if word not in word_freq:
            word_freq[word] = 1
        else:
            word_freq[word] = word_freq[word] + 1

    max_freq = max(word_freq.values())
    for word in word_freq.keys():
        word_freq[word] = (word_freq[word]/max_freq)

    # Create a list of the sentences in the text
    sent_list = nltk.sent_tokenize(text)
    # Create an empty dictionary to store sentence scores
    sent_score = {}
    for sent in sent_list:
        for word in nltk.word_tokenize(sent.lower()):
            if word in word_freq.keys():
                if sent not in sent_score.keys():
                    sent_score[sent] = word_freq[word]
                else:
                    sent_score[sent] = sent_score[sent] + word_freq[word]

    summary_sents = nlargest(length, sent_score, key = sent_score.get)
    summary = ' '.join(summary_sents)
    return summary