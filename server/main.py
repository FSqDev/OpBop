# General
from flask import Flask, Response, request, jsonify
import os
from dotenv import load_dotenv

# Custom wrappers
from newsutils import NewsUtils
from otherthings import summarize
import openai
from dotenv import load_dotenv
from pprint import pprint

# Debugging
import time

app = Flask("app")
news_utils = NewsUtils()


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
        Int recency: max age (in days) of returned articles, 0 for any time
    returns:
        List[JSON] articles: similar articles (Title, URL, Source)
    """
    if "keywords" not in request.json:
        return Response("Expected parameter 'keywords' in body", status=400)
    if "recency" not in request.json:
        return Response("Expected parameter 'recency' in body", status=400)
    elif request.json["recency"] < 0:
        return Response("Cannot have negative value for recency", status=400)

    ret = news_utils.similar_articles(request.json["keywords"], request.json["recency"])

    return jsonify({
        "articles": ret
    })


@app.route('/api/shorten', methods=['POST'])
def shorten():
    """
    Takes the input text and shortens it in a tl;dr style using SMMRY

    args:
        String maintext: whatever text needs to be shortened
    returns:
        String summary: shortened text
    """
    if "maintext" not in request.json:
        return Response("Expected parameter 'maintext' in body", status=400)

    return jsonify(summarize(request.json["maintext"]))


@app.route('/api/simplify', methods=['POST'])
def simplify():
    """
    Takes the input text and simplifies it to "2nd grader English" using OpenAI

    args:
        String maintext: whatever text needs to be simplified
    returns:
        String maintext: simplified text
        String sensitivity: flag indicating sensitive content (0 none, 1 sensitive, 2 explicit)
    """
    if "maintext" not in request.json:
        return Response("Expected parameter 'maintext' in body", status=400)

    text = request.json["maintext"]

    simplified = openai.Completion.create(
        engine='davinci-instruct-beta',
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

    args:
        String url: url of the webpage
    returns:
        String tldr: shortened text
        Int reduction: percentage of reduction performed by tldr algorithm
        String simplified: simplified text
        String sensitivity: sensitive content flag
        List articles: similar articles
    """
    if "url" not in request.json:
        return Response("Expected parameter 'url' in body", status=400)

    parsed = news_utils.parse_maintext_title(request.json["url"])
    maintext = parsed["maintext"]
    tldr = summarize(maintext)
    reduction = int(100 * (len(maintext) - len(tldr)) / len(maintext))
    reduction = ""
    while True:
        try:
            simplified = openai.Completion.create(
                engine='davinci-instruct-beta',
                prompt=f"explain the following text in a way a second grader would understand:\n\\\n{tldr}\n",
                temperature=0,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                stop=["\"\"\""],
                max_tokens=len(tldr.split())
            )
            break
        except openai.error.InvalidRequestError:
            tldr = summarize(tldr)
            reduction = int(100 * (len(maintext) - len(tldr)) / len(maintext))

    sensitivity = openai.Completion.create(
      engine="content-filter-alpha-c4",
      prompt = "<|endoftext|>"+maintext+"\n--\nLabel:",
      temperature=0,
      max_tokens=1,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0,
      logprobs=10
    )

    articles = news_utils.similar_articles(news_utils.parse_keywords(parsed["title"]), 0)

    return jsonify({
        "tldr": tldr,
        "reduction": reduction,
        "simplified": simplified['choices'][0]['text'],
        "sensitivity": sensitivity["choices"][0]["text"],
        "articles": articles
    })


# ========================================= BELOW IS TESTING/DEVELOPMENT APIS, NOT MEANT FOR ACTUAL USE =========================================
@app.route('/api/openaikeychange', methods=['POST'])
def openaikeychange():
    """
    Changes the API key so we can swap between accounts on prod
    """
    if "key" not in request.json:
        return Response("Expected parameter 'key' in body", status=400)

    openai.api_key = request.json["key"]
    return Response("Success", status=200)


@app.route('/api/dothethingdev', methods=['POST'])
def dothethingdev():
    """
    Testing endpoint for frontend, to prevent overuse of OpenAi tokens
    """
    time.sleep(3)

    return jsonify({
    "articles": [
        {
            "image": "https://storage.googleapis.com/afs-prod/media/2e6bcf5dd59f499aa031f920df0c1d3d/3000.jpeg",
            "source": "Associated Press",
            "title": "Taliban killings fuel fear, drive more chaos outside airport - Associated Press",
            "url": "https://apnews.com/article/europe-race-and-ethnicity-taliban-e51255ff3d954e8f95bea4dc1c209b32"
        },
        {
            "image": "https://storage.googleapis.com/afs-prod/media/b761afb663e443bd97fc1745d64766b7/3000.jpeg",
            "source": "Associated Press",
            "title": "[AP] Taliban take over Afghanistan: What we know and what's next - Associated Press",
            "url": "https://apnews.com/article/taliban-takeover-afghanistan-what-to-know-1a74c9cd866866f196c478aba21b60b6"
        },
        {
            "image": "https://cdn.cnn.com/cnnnext/dam/assets/210816084223-09-afghanistan-0815-kabul-super-tease.jpg",
            "source": "CNN",
            "title": "Who are the Taliban and how did they take control of Afghanistan so swiftly? - CNN",
            "url": "https://www.cnn.com/2021/08/16/middleeast/taliban-control-afghanistan-explained-intl-hnk/index.html"
        },
        {
            "image": "https://static01.nyt.com/images/2021/08/19/opinion/19JacksonV3-inyt/17JacksonV3-facebookJumbo.jpg",
            "source": "The New York Times",
            "title": "Opinion | How Will the Taliban Rule Afghanistan? - The New York Times",
            "url": "https://www.nytimes.com/2021/08/17/opinion/taliban-afghanistan.html"
        }
    ],
    "reduction": 50,
    "sensitivity": "0",
    "simplified": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Parturient montes nascetur ridiculus mus. Rutrum quisque non tellus orci. Purus sit amet luctus venenatis lectus magna. Mattis vulputate enim nulla aliquet porttitor lacus luctus accumsan tortor. Mi eget mauris pharetra et ultrices neque ornare aenean. Ac felis donec et odio pellentesque diam volutpat commodo sed. Gravida in fermentum et sollicitudin ac orci phasellus egestas. Amet justo donec enim diam vulputate. Nec ullamcorper sit amet risus nullam. Vitae justo eget magna fermentum iaculis. Sed odio morbi quis commodo odio aenean sed adipiscing. Diam quis enim lobortis scelerisque fermentum dui faucibus. Varius sit amet mattis vulputate enim nulla aliquet porttitor lacus. Quis lectus nulla at volutpat diam ut venenatis tellus in. Tortor consequat id porta nibh venenatis cras sed felis. Mollis nunc sed id semper risus in hendrerit gravida. Nisl vel pretium lectus quam id leo. In nisl nisi scelerisque eu ultrices vitae auctor eu augue. Blandit libero volutpat sed cras ornare. Morbi tristique senectus et netus et malesuada fames. Vestibulum mattis ullamcorper velit sed ullamcorper morbi tincidunt. Tortor at risus viverra adipiscing at. Porta lorem mollis aliquam ut porttitor leo a diam. Posuere morbi leo urna molestie at elementum eu facilisis sed. Risus nec feugiat in fermentum posuere urna nec. Viverra maecenas accumsan lacus vel. Nisi quis eleifend quam adipiscing vitae proin sagittis nisl rhoncus. Quam elementum pulvinar etiam non quam lacus suspendisse faucibus. Tincidunt eget nullam non nisi est. Ipsum a arcu cursus vitae congue. Aliquet eget sit amet tellus.",
    "tldr": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Parturient montes nascetur ridiculus mus. Rutrum quisque non tellus orci. Purus sit amet luctus venenatis lectus magna. Mattis vulputate enim nulla aliquet porttitor lacus luctus accumsan tortor. Mi eget mauris pharetra et ultrices neque ornare aenean. Ac felis donec et odio pellentesque diam volutpat commodo sed. Gravida in fermentum et sollicitudin ac orci phasellus egestas. Amet justo donec enim diam vulputate. Nec ullamcorper sit amet risus nullam. Vitae justo eget magna fermentum iaculis. Sed odio morbi quis commodo odio aenean sed adipiscing. Diam quis enim lobortis scelerisque fermentum dui faucibus. Varius sit amet mattis vulputate enim nulla aliquet porttitor lacus. Quis lectus nulla at volutpat diam ut venenatis tellus in. Tortor consequat id porta nibh venenatis cras sed felis. Mollis nunc sed id semper risus in hendrerit gravida. Nisl vel pretium lectus quam id leo. In nisl nisi scelerisque eu ultrices vitae auctor eu augue. Blandit libero volutpat sed cras ornare. Morbi tristique senectus et netus et malesuada fames. Vestibulum mattis ullamcorper velit sed ullamcorper morbi tincidunt. Tortor at risus viverra adipiscing at. Porta lorem mollis aliquam ut porttitor leo a diam. Posuere morbi leo urna molestie at elementum eu facilisis sed. Risus nec feugiat in fermentum posuere urna nec. Viverra maecenas accumsan lacus vel. Nisi quis eleifend quam adipiscing vitae proin sagittis nisl rhoncus. Quam elementum pulvinar etiam non quam lacus suspendisse faucibus. Tincidunt eget nullam non nisi est. Ipsum a arcu cursus vitae congue. Aliquet eget sit amet tellus."
})


@app.route('/api/banana', methods=['POST'])
def banana():
    """ 
    Frontend requested this??
    """
    return jsonify({
        "value": "banana"
    })


if __name__ == "__main__":
    load_dotenv()
    openai.api_key = os.getenv('OPENAI_SK')
    port = int(os.environ.get('PORT', 5000))
    app.run(port=port)
