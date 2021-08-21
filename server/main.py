# General
from flask import Flask, Response, request, jsonify
import os

# Custom wrappers
from newsutils import NewsUtils
from otherthings import summarize
import openai
from dotenv import load_dotenv

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

    ret = news_utils.parse_maintext_title(request.json["url"])
    maintext = ret["maintext"]
    keywords = news_utils.parse_keywords(ret["title"])

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
    text = request.args.get("maintext")

    simplified = openai.Completion.create(
        # engine='davinci',
        engine='davinci-instruct-beta',
        # prompt=f"My second grader asked me what this passage means:\n\"\"\"\n{text}\n\"\"\"\nI rephrased it for him, in plain language a second grader can understand:\n\"\"\"\n",
        prompt=f"explain the following text in a way a second grader would understand:\n\\\n{text}\n",
        temperature=0,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=["\"\"\""],
        max_tokens=len(text.split())
    )

    text_saftey = openai.Completion.create(
      engine="content-filter-alpha-c4",
      prompt = "<|endoftext|>"+text+"\n--\nLabel:",
      temperature=0,
      max_tokens=1,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0,
      logprobs=10
    )

    return jsonify(
        maintext=simplified['choices'][0]['text'],
        sensitivity=text_saftey["choices"][0]["text"]
    )



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
    load_dotenv()
    openai.api_key = os.getenv('OPENAI_SK')
    port = int(os.environ.get('PORT', 5000))
    app.run(port=port)
