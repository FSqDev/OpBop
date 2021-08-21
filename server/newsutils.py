# Keywords - nltk
import nltk
nltk.download('stopwords')
nltk.download('punkt')
from nltk import tokenize
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
# Keywords - other
from operator import itemgetter
import math
# Maintext
from newspaper import Article

class NewsUtils:
    """ Class that handles fetching, parsing and searching of news articles for OpBop """
    KEYWORDS = 3

    def __init__(self, debug = False):
        self.debug = debug

    def parse_maintext_title(self, url: str) -> str:
        """ Gets the main body of text from an article, given url """
        article = Article(url)
        article.download()
        article.parse()
        return {
            "maintext": article.text.replace("\n", ""),
            "title": article.title
        }

    def parse_keywords(self, text: str) -> list:
        """ Extracts keywords from a passage of text """
        # Input cleaning
        text = text.replace(",", "")
        text = text.lower()

        # Stopwords and vars
        stop_words = set(stopwords.words('english'))
        total_words = text.split()
        total_sentences = tokenize.sent_tokenize(text)
        
        # TF score calculation
        tf_score = {}
        for word in total_words:
            word = word.replace(".", "")
            if word not in stop_words:
                if word in tf_score:
                    tf_score[word] += 1
                else:
                    tf_score[word] = 1
        tf_score.update((x, y/int(len(total_words))) for x, y in tf_score.items())

        # IDF calculation
        idf_score = {}
        for word in total_words:
            word = word.replace('.','')
            if word not in stop_words:
                if word in idf_score:
                    idf_score[word] = self._check_sent(word, total_sentences)
                else:
                    idf_score[word] = 1
        idf_score.update((x, math.log(int(len(total_sentences))/y)) for x, y in idf_score.items())

        # Calculate scores and return top weighted
        tf_idf_score = {key: tf_score[key] * idf_score.get(key, 0) for key in tf_score.keys()}
        return list(dict(sorted(tf_idf_score.items(), key = itemgetter(1), reverse = True)[:NewsUtils.KEYWORDS]).keys())
    
    def _check_sent(self, word: str, sentences):
        """ parse_keywords helper - Check if word present in sentence list """
        final = [all([w in x for w in word]) for x in sentences] 
        sent_len = [sentences[i] for i in range(0, len(final)) if final[i]]
        return int(len(sent_len))
