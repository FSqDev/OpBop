# General
from flask import Flask, Response, request, jsonify
import os

# Custom wrappers
from newsutils import NewsUtils
from summarize import summarize

app = Flask("app")
news_utils = NewsUtils(True)


@app.route('/')
def home():
    """ Basically just here to check if server is running """
    return 'OpBop server is running'


@app.route('/api/parsearticle', methods=['POST'])
def parse_article():
    """
    Takes URL of a news article and extracts data used by other functions

    args:
        String url: String url of the article to parse
    returns:
        String maintext: main text of the article
        List[String] keywords: keywords extracted from maintext
        Int reliability: flag indicating reliability (1 unreliable, 2 somewhat unreliable, 3 mixed, 4 most reliable)
    """
    if "url" not in request.json:
        return Response("Expected parameter 'url' in body", status=400)

    maintext = news_utils.parse_main_text(request.json["url"])
    keywords = news_utils.parse_keywords(maintext)

    return jsonify({
        "maintext": maintext,
        "keywords": keywords,
        "reliability": 0
    })


@app.route('/api/findsimilar', methods=['POST'])
def find_similar():
    """
    Finds relevant articles based on provided keywords and parameters

    args:
        List[String] keywords: list of keywords to search
        Int recency: max age (in days) of returned articles, -1 for any time
    returns:
        List[JSON] articles: similar articles (Title, URL, Source)
    """
    pass


@app.route('/api/shorten', methods=['POST'])
def shorten():
    """
    Takes the input text and shortens it in a tl;dr style using SMMRY

    args:
        String maintext: whatever text needs to be shortened
    returns:
        String maintext: shortened text
    """
    return summarize(request.args.get("maintext"))


@app.route('/api/simplify', methods=['POST'])
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


@app.route('/api/dothething', methods=['POST'])
def do_the_thing():
    """
    Basically every other API combined into one for 'internal' use
    TODO
    """
    pass


@app.route('/api/banana', methods=['POST'])
def banana():
    """ 
    Frontend request this
    """
    return jsonify({
        "value": "banana"
    })


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(port=port)
