# General
from flask import Flask, Response, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import tldextract

# Custom wrappers
from newsutils import NewsUtils
from otherthings import summarize, load_reliability_data
import openai
from db import OpBopDb

# Debugging
import time
from flask_cors import CORS

app = Flask("app")
app.debug = True
cors = CORS(app)
news_utils = NewsUtils()
reliability_data = load_reliability_data()
dao = OpBopDb()


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
        List[String] blacklist: list of top level domains blocked by user
    returns:
        List[JSON] articles: similar articles (Title, URL, Source)
    """
    if "keywords" not in request.json:
        return Response("Expected parameter 'keywords' in body", status=400)
    if "recency" not in request.json:
        return Response("Expected parameter 'recency' in body", status=400)
    elif request.json["recency"] < 0:
        return Response("Invalid parameter: Cannot have negative value for recency", status=400)
    if "blacklist" not in request.json:
        return Response("Expected parameter 'blacklist' in body", status=400)

    ret = news_utils.similar_articles(request.json["keywords"], request.json["recency"], request.json["blacklist"])

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


@app.route('/api/findcached', methods=['POST'])
def find_cached():
    """
    Searches for cached version of an article, given a url
    Returns basic 200 if not found

    args:
        String url: url of the webpage
    returns:
        String tldr: shortened text
        Int reduction: percentage of reduction performed by tldr algorithm
        String simplified: simplified text
        String sensitivity: sensitive content flag
        List articles: similar articles
        String reliability: one of [unknown, high, mixed, low] representing source's factuality
    """
    if dao.db is None:
        return Response("Reset the API keys", status=400)

    if "url" not in request.json:
        return Response("Expected parameter 'url' in body", status=400)
    
    ret = dao.find_by_url(request.json["url"])
    if ret is None:
        return Response("Not cached", status=200)
    else:
        return jsonify(ret)


@app.route('/api/addtocache', methods=['POST'])
def add_to_cache():
    """
    Adds the article to the cache

    args:
        String url: the url of the website
        String tldr: shortened text
        Int reduction: percentage of reduction performed by tldr algorithm
        String simplified: simplified text
        String sensitivity: sensitive content flag
        List articles: similar articles
        String reliability: one of [unknown, high, mixed, low] representing source's factuality
    returns:
        None
    """
    if dao.db is None:
        return Response("Reset the API keys", status=400)

    if "url" not in request.json:
        return Response("Expected parameter 'url' in body", status=400)
    if "tldr" not in request.json:
        return Response("Expected parameter 'tldr' in body", status=400)
    if "reduction" not in request.json:
        return Response("Expected parameter 'reduction' in body", status=400)
    if "simplified" not in request.json:
        return Response("Expected parameter 'simplified' in body", status=400)
    if "sensitivity" not in request.json:
        return Response("Expected parameter 'sensitivity' in body", status=400)
    elif request.json["sensitivity"] not in ["0", "1", "2"]:
        return Response("Invalid parameter: Sensitivity should be one of 0, 1, or 2", status=400)
    if "articles" not in request.json:
        return Response("Expected parameter 'articles' in body", status=400)
    if "reliability" not in request.json:
        return Response("Expected parameter 'reliability' in body", status=400)

    dao.insert_article({
        "url": request.json["url"].lower(),
        "tldr": request.json["tldr"],
        "reduction": request.json["reduction"],
        "simplified": request.json["simplified"],
        "sensitivity": request.json["sensitivity"],
        "articles": request.json["articles"],
        "reliability": request.json["reliability"]
    })

    return Response("Success", status=200)


@app.route('/api/dothething', methods=['POST'])
def do_the_thing():
    """
    Basically every other API combined into one for 'internal' use

    args:
        String url: url of the webpage
        JSON ArticleRange:
            from String: ISO8601 Date, earliest publication date
            to String: ISO8601 Date, latest publication date
        String filterExplicit: maximum sensitivity tolerance of userm 0~2 as string
        List[String] blacklist: list of blacklisted sites for article suggestions
    returns:
        String tldr: shortened text
        Int reduction: percentage of reduction performed by tldr algorithm
        String simplified: simplified text
        String sensitivity: sensitive content flag
        List articles: similar articles
        Bool censored: whether or not the return content was censored by filter level
        String reliability: one of [unknown, high, mixed, low] representing source's factuality
    """
    if dao.db is None:
        return Response("Reset the API keys", status=400)

    # Request body validation
    if "url" not in request.json:
        return Response("Expected parameter 'url' in body", status=400)
    if "articleRange" not in request.json or not request.json["articleRange"]:
        range = {
            "from": "2020-08-21",
            "to": "2021-08-21"
        }
    else:
        range = request.json["articleRange"]
    if "filterExplicit" not in request.json:
        return Response("Expected parameter 'filterExplicit' in body", status=400)
    elif request.json["filterExplicit"] not in ["0", "1", "2"]:
        return Response("Invalid parameter: Filter level should be one of 0, 1, or 2", status=400)
    if "blacklist" not in request.json:
        return Response("Expected parameter 'blacklist' in body", status=400)

    # Check cache, return if found
    ret = dao.find_by_url(request.json["url"])
    if ret is not None:
        return jsonify({
        "tldr": ret["tldr"],
        "reduction": ret["reduction"],
        "simplified": ret["simplified"],
        "sensitivity": ret["sensitivity"],
        "articles": ret["articles"],
        "censored": (int(request.json["filterExplicit"]) < int(ret["sensitivity"])),
        "reliability": ret["reliability"]
    })

    # Parse article
    parsed = news_utils.parse_maintext_title(request.json["url"])
    maintext = parsed["maintext"]
    tldr = summarize(maintext)

    # Simplification, further summarization if needed
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
            reduction = int(100 * ((len(maintext) - len(tldr)) / len(maintext)))
            break
        except openai.error.InvalidRequestError:
            tldr = summarize(tldr)

    # Content filter
    sensitivity = None
    t = maintext
    try:
        sensitivity = openai.Completion.create(
            engine="content-filter-alpha-c4",
            prompt = "<|endoftext|>"+t+"\n--\nLabel:",
            temperature=0,
            max_tokens=1,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            logprobs=10
        )
    except openai.error.InvalidRequestError:
        t = tldr
        sensitivity = openai.Completion.create(
            engine="content-filter-alpha-c4",
            prompt = "<|endoftext|>"+t+"\n--\nLabel:",
            temperature=0,
            max_tokens=1,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            logprobs=10
        )
    sens = sensitivity["choices"][0]["text"]
    filterbaddybads = int(request.json["filterExplicit"])
    censored = False
    if filterbaddybads < int(sens):
        censored = True

    # Similar articles
    articles = news_utils.similar_articles(news_utils.parse_keywords(parsed["title"]), range['from'], range['to'], request.json["blacklist"])

    # Reliability
    try:
        do_be_reliable = reliability_data[
            '.'.join(tldextract.extract(request.json['url'])[1:])
        ]
    except KeyError:
        do_be_reliable = "unknown"

    # Add to cache and return
    simplified = simplified['choices'][0]['text'].strip("\n")

    dao.insert_article({
        "url": request.json["url"].lower(),
        "tldr": tldr,
        "reduction": reduction,
        "simplified": simplified,
        "sensitivity": sens,
        "articles": articles,
        "censored": censored,
        "reliability": do_be_reliable
    })
    return jsonify({
        "tldr": tldr,
        "reduction": reduction,
        "simplified": simplified,
        "sensitivity": sens,
        "articles": articles,
        "censored": censored,
        "reliability": do_be_reliable
    })


# ========================================= BELOW IS TESTING/DEVELOPMENT APIS, NOT MEANT FOR ACTUAL USE =========================================
@app.route('/api/apikeychange', methods=['POST'])
def openaikeychange():
    """
    Changes the API key so we can swap between accounts on prod

    args:
        String openai: OpenAI API key
        String mongo: MongoDB URI
    returns:
        "Success"
    """
    if "openai" not in request.json:
        return Response("Expected parameter 'openai' in body", status=400)
    if "mongo" not in request.json:
        return Response("Expected parameter 'mongo' in body", status=400)

    openai.api_key = request.json["openai"]
    dao.reset_db(request.json["mongo"])

    return Response("Success", status=200)


@app.route('/api/dothethingdev', methods=['POST'])
def dothethingdev():
    """
    Testing endpoint for frontend, to prevent overuse of OpenAi tokens

    args:
        None
    returns:
        Mimic response of real /dothethingdev endpoint
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
    "censored": True,
    "reduction": 50,
    "reliability": "low",
    "sensitivity": "0",
    "simplified": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Parturient montes nascetur ridiculus mus. Rutrum quisque non tellus orci. Purus sit amet luctus venenatis lectus magna. Mattis vulputate enim nulla aliquet porttitor lacus luctus accumsan tortor. Mi eget mauris pharetra et ultrices neque ornare aenean. Ac felis donec et odio pellentesque diam volutpat commodo sed. Gravida in fermentum et sollicitudin ac orci phasellus egestas. Amet justo donec enim diam vulputate. Nec ullamcorper sit amet risus nullam. Vitae justo eget magna fermentum iaculis. Sed odio morbi quis commodo odio aenean sed adipiscing. Diam quis enim lobortis scelerisque fermentum dui faucibus. Varius sit amet mattis vulputate enim nulla aliquet porttitor lacus. Quis lectus nulla at volutpat diam ut venenatis tellus in. Tortor consequat id porta nibh venenatis cras sed felis. Mollis nunc sed id semper risus in hendrerit gravida. Nisl vel pretium lectus quam id leo. In nisl nisi scelerisque eu ultrices vitae auctor eu augue. Blandit libero volutpat sed cras ornare. Morbi tristique senectus et netus et malesuada fames. Vestibulum mattis ullamcorper velit sed ullamcorper morbi tincidunt. Tortor at risus viverra adipiscing at. Porta lorem mollis aliquam ut porttitor leo a diam. Posuere morbi leo urna molestie at elementum eu facilisis sed. Risus nec feugiat in fermentum posuere urna nec. Viverra maecenas accumsan lacus vel. Nisi quis eleifend quam adipiscing vitae proin sagittis nisl rhoncus. Quam elementum pulvinar etiam non quam lacus suspendisse faucibus. Tincidunt eget nullam non nisi est. Ipsum a arcu cursus vitae congue. Aliquet eget sit amet tellus.",
    "tldr": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Parturient montes nascetur ridiculus mus. Rutrum quisque non tellus orci. Purus sit amet luctus venenatis lectus magna. Mattis vulputate enim nulla aliquet porttitor lacus luctus accumsan tortor. Mi eget mauris pharetra et ultrices neque ornare aenean. Ac felis donec et odio pellentesque diam volutpat commodo sed. Gravida in fermentum et sollicitudin ac orci phasellus egestas. Amet justo donec enim diam vulputate. Nec ullamcorper sit amet risus nullam. Vitae justo eget magna fermentum iaculis. Sed odio morbi quis commodo odio aenean sed adipiscing. Diam quis enim lobortis scelerisque fermentum dui faucibus. Varius sit amet mattis vulputate enim nulla aliquet porttitor lacus. Quis lectus nulla at volutpat diam ut venenatis tellus in. Tortor consequat id porta nibh venenatis cras sed felis. Mollis nunc sed id semper risus in hendrerit gravida. Nisl vel pretium lectus quam id leo. In nisl nisi scelerisque eu ultrices vitae auctor eu augue. Blandit libero volutpat sed cras ornare. Morbi tristique senectus et netus et malesuada fames. Vestibulum mattis ullamcorper velit sed ullamcorper morbi tincidunt. Tortor at risus viverra adipiscing at. Porta lorem mollis aliquam ut porttitor leo a diam. Posuere morbi leo urna molestie at elementum eu facilisis sed. Risus nec feugiat in fermentum posuere urna nec. Viverra maecenas accumsan lacus vel. Nisi quis eleifend quam adipiscing vitae proin sagittis nisl rhoncus. Quam elementum pulvinar etiam non quam lacus suspendisse faucibus. Tincidunt eget nullam non nisi est. Ipsum a arcu cursus vitae congue. Aliquet eget sit amet tellus."
})


@app.route('/api/banana', methods=['POST'])
def banana():
    """ Frontend requested this?? """
    return jsonify({
        "value": "banana"
    })


if __name__ == "__main__":
    load_dotenv()
    openai.api_key = os.getenv('OPENAI_SK')
    port = int(os.environ.get('PORT', 5000))
    app.run(port=port)
    # app.run(host='0.0.0.0', port=port)
