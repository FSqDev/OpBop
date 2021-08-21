# General
from flask import Flask
import os


app = Flask("app")


@app.route('/')
def home():
    """ Basically just here to check if server is running """
    return 'OpBop server is running'


@app.route('/api/parsearticle', methods=['GET'])
def parsearticle():
    """
    Takes URL of a news article and extracts data used by other functions

    args:
        String url: String url of the article to parse
    returns:
        String maintext: main text of the article
        List[String] keywords: keywords extracted from maintext
        Int reliability: flag indicating reliability (1 unreliable, 2 somewhat unreliable, 3 mixed, 4 most reliable)
    """
    pass


@app.route('/api/findsimilar', methods=['GET'])
def findsimilar():
    """
    Finds relevant articles based on provided keywords and parameters

    args:
        List[String] keywords: list of keywords to search
        Int recency: max age (in days) of returned articles, -1 for any time
    returns:
        List[JSON] articles: similar articles (Title, URL, Source)
    """
    pass


@app.route('/api/shorten', methods=['GET'])
def shorten():
    """
    Takes the input text and shortens it in a tl;dr style using SMMRY

    args:
        String maintext: whatever text needs to be shortened
    returns:
        String maintext: shortened text
    """
    pass


@app.route('/api/simplify', methods=['GET'])
def simplify():
    """
    Takes the input text and simplifies it to "2nd grader English" using OpenAI

    args:
        String maintext: whatever text needs to be simplified
    returns:
        String maintext: simplified text
        Int sensitivity: flag indicating sensitive content (0 none, 1 sensitive, 2 explicit)
    """
    pass


@app.route('/api/dothething', methods=['GET'])
def dothething():
    """
    Basically every other API combined into one for 'internal' use
    TODO
    """
    pass


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(port=port)
