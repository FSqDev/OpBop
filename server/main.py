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
    return jsonify({
    "articles": [
        {
            "source": "CTV News",
            "title": "Hidilyn Diaz wins Philippines' first Olympic gold medal with weightlifting - CTV News",
            "url": "https://www.ctvnews.ca/sports/hidilyn-diaz-wins-philippines-first-olympic-gold-medal-with-weightlifting-1.5524746"
        },
        {
            "source": "CNBC",
            "title": "Philippines’ first Olympic gold medalist was briefly accused of being part of 'plot' against Duterte - CNBC",
            "url": "https://www.cnbc.com/2021/07/30/philippine-olympic-gold-medalist-linked-to-alleged-plot-to-oust-duterte.html"
        },
        {
            "source": "TIME",
            "title": "Bermuda and the Philippines Have Won Their First Olympic Gold Medals—Ever - TIME",
            "url": "https://time.com/6084202/bermuda-philippines-gold-medal-olympics/"
        },
        {
            "source": "Rappler",
            "title": "Take a bow: Philippines' golden campaign in the Tokyo Olympics - Rappler",
            "url": "https://www.rappler.com/sports/philippines-golden-campaign-tokyo-olympics"
        }
    ],
    "reduction": 49,
    "sensitivity": "0",
    "simplified": "\nThe Philippines won its first Olympic gold medal after nearly 100 years of trying. Hidilyn Diaz, a weightlifter, won the gold medal in the 55-kilogram category of women's weightlifting. She also set an Olympic record with her combined weight total of 224 kilograms across two successful lifts. After her historic win, a tearful Diaz celebrated with her coaches before taking the top spot on the podium in Tokyo. Standing where no Filipino had stood before, Diaz, who serves in the Philippine air force, snapped off a salute and sang along to her country's national anthem. \"I sacrificed a lot. I wasn't able to be with my mother and father for how many months and years and then of course, training was excruciating,\" Diaz said afterward, according to the Philippine Daily Inquirer. \"But God had a plan.\" The gold medal contest came down to Diaz's last lift, thanks to a tight battle with China's Liao Qiuyun, the world record-holder in the event. YouTube Both Diaz and Liao lifted 97 kilograms (about 214 pounds) in their first-round snatch lift. For the following clean and jerk, Liao lifted 126 kilograms (nearly 278 pounds). Diaz responded by lifting 127 kilograms — another Olympic record — which finally broke the Philippines' gold drought. Liao settled for silver, and Zulfiya Chinshanlo of Kazakhstan won bronze. The snatch lift is very fast as weightlifters try to pick up the bar and raise it above their heads in one smooth motion. The clean and jerk has two main movements: Competitors first lift the bar to their shoulders before raising it above their heads. By winning a long-awaited gold Monday, Diaz even overshadowed Philippine President Rodrigo Duterte's final State of the Nation address, Rappler reported. Diaz, 30, is at her fourth Olympics. Even before Monday's landmark win, she had secured her place in sports history by winning a silver medal at the Rio Olympics in 2016 — the first medal won by a woman from her country. Her breakthrough performance in Rio earned Diaz a place in Filipinos' hearts, particularly as many were inspired by her personal story of rising out of a childhood marked by poverty to pursue her dreams at the highest level. She took up weightlifting as a child, using plastic pipes that held concrete weights. \"When she was 11, the Filipina was given a barbell to train with after a local weight",
    "tldr": "The country had been trying to reach the podium's top spot for nearly 100 years: It sent its first Olympic delegation to Paris for the 1924 Games.Diaz won gold in the 55-kilogram category of women's weightlifting — and in the process, she also set an Olympic record with her combined weight total of 224 kilograms across two successful lifts.After her historic win, a tearful Diaz celebrated with her coaches before taking the top spot on the podium in Tokyo. Even before Monday's landmark win, she had secured her place in sports history by winning a silver medal at the Rio Olympics in 2016 — the first medal won by a woman from her country.Her breakthrough performance in Rio earned Diaz a place in Filipinos' hearts, particularly as many were inspired by her personal story of rising out of a childhood marked by poverty to pursue her dreams at the highest level.She took up weightlifting as a child, using plastic pipes that held concrete weights. The Philippines Wins Its First Olympic Gold After Nearly 100 Years Of TryingEnlarge this image toggle caption An Lingjun/CHINASPORTS/VCG via Getty Images An Lingjun/CHINASPORTS/VCG via Getty ImagesWeightlifter Hidilyn Diaz made history Monday, winning the Philippines' first gold medal at the Summer Olympics in Tokyo. \"The gold medal contest came down to Diaz's last lift, thanks to a tight battle with China's Liao Qiuyun, the world record-holder in the event.YouTubeBoth Diaz and Liao lifted 97 kilograms (about 214 pounds) in their first-round snatch lift."
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
