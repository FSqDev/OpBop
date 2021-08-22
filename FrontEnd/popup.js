// Api call params
const basePath = 'https://opbop.herokuapp.com/'
const apiPath = basePath + 'api/'

const urls = {
    banana : apiPath + 'banana',
    main : apiPath + 'dothething'
}

// Main function - parse and show
let parseButton = document.getElementById("parse-button")
parseButton.addEventListener("click", async () => {
    let [tab] = await chrome.tabs.query({active: true, currentWindow: true});
    let url = tab.url;

    parse(url);
});

function parse(url) {
    parseButton.setAttribute("hidden", null);
    document.body.style.paddingBottom = "5px";
    document.getElementById("loading-message").innerHTML = getLoadingMessage();
    document.getElementById("parse-idle").removeAttribute("hidden")
    chrome.storage.sync.get(["enableSimilarArticleFiltering", "articleRangeBefore", "articleRangeAfter", "enableExplicitFiltering", "blackList", "filterLevel"], data => {
        fetch(urls.main,
            {
                method: "post",
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    url: url,
                    articleRange: data.enableSimilarArticleFiltering ? {
                        from: data.articleRangeAfter,
                        to: data.articleRangeBefore
                    } : null,
                    filterExplicit: data.filterLevel == undefined ? "0" : data.filterLevel,
                    blacklist: data.blackList == undefined ? [] : data.blackList
                })
            }
        ).then(function (res) {
            if (res.status === 200) {
                res.json().then(function (data) {
                    populateTldr(data.tldr, data.reduction);
                    populateSimplified(data.simplified);
                    populateSimilarArticles(data.articles, data.censored);
                    document.body.style.width = "500px"; // TODO: smooth this transition
                    document.getElementById("parse-idle").setAttribute("hidden", null)
                    document.getElementById("parsed-container").removeAttribute("hidden")
                });
            } else {
                document.getElementById("parse-idle").setAttribute("hidden", null)
                document.getElementById("error-image").setAttribute("src", "https://http.cat/" + res.status + ".jpg")
                document.getElementById("error-div").removeAttribute("hidden")
            }
        });
    });
}

// Populate fields with API return
function populateTldr(tldrText, reductionPercent) {
    let tldr = document.getElementById("tldr-text");
    tldr.innerHTML = tldrText;

    let tldrReduction = document.getElementById("tldr-reduction");
    tldrReduction.innerHTML = `Article length reduced by <b>${reductionPercent}%</b>`;
}

function populateSimplified(simiplifiedText) {
    let simplified = document.getElementById("simplified-text");
    simplified.innerText = simiplifiedText;
}

function populateSimilarArticles(articles, censorImages) {
    const similarArticleDiv = document.getElementById("nav-similar");
    similarArticleDiv.innerHTML = "";
    let articleNumber = 0;
    articles.forEach((article) => {
        let articleWrapper = document.createElement("a")
        articleWrapper.id = "article-" + articleNumber++;
        articleWrapper.setAttribute("href", article.url);
        let articleTile = document.createElement("div");
        articleTile.classList.add("article-tile")
        let articleImg = document.createElement("img");
        chrome.storage.sync.get("censorImages", (data) => {
            if (data.censorImages && censorImages) {
                articleImg.setAttribute("src", article.image);
            } {
                articleImg.setAttribute("src", getPlaceHolderImage())
            }
        })
        articleTile.appendChild(articleImg);
        let articleTitle = document.createElement("div");
        articleTitle.classList.add("article-title")
        articleTitle.innerHTML = article.title;
        articleTile.appendChild(articleTitle);
        let articleSource = document.createElement("div");
        articleSource.classList.add("article-source")
        articleSource.innerHTML = article.source;
        articleTile.appendChild(articleSource);
        articleWrapper.appendChild(articleTile)
        similarArticleDiv.appendChild(articleWrapper);

        let similarArticle = document.getElementById(articleWrapper.id);
        similarArticle.addEventListener("click", function () {
            openUrl(article.url);
        }, false);
    })
}

function openUrl(url) {
    chrome.tabs.create({ url: url});
}

// Because comedy
function getLoadingMessage () {
    let messages = [
        "Bending the spoon...",
        "Filtering morale...",
        "Have a good day.",
        "(Insert quarter)",
        "Are we there yet?",
        "Just count to 10",
        "Why so serious?",
        "Don't panic...",
        "Is this Windows?",
        "Granting wishes...",
        "git happens",
        "Dividing by zero...",
        "Spawn more Overlord!",
        "Proving P=NP...",
        "Twiddling thumbs...",
        "Winter is coming...",
        "Aw, snap! Not..",
        "What the what?",
        "format C: ...",
        "What's under there?",
        "Pushing pixels...",
        "Building a wall...",
        "Updating Updater...",
        "Work, work...",
        "Feeding unicorns...",
    ];

    const random = Math.floor(Math.random() * messages.length);
    return messages[random];
}

// Options page button
let optionsButton = document.getElementById("options-icon")
optionsButton.addEventListener("click", () => {
    if (chrome.runtime.openOptionsPage) {
        chrome.runtime.openOptionsPage();
    } else {
        window.open(chrome.runtime.getURL('options.html'));
    }
});

function getPlaceHolderImage() {
    let images = [
        "./images/egguana.jpg",
        "./images/gatsby.jpg",
        "./images/lion_cat.jpg",
        "./images/stitch.jpg"
    ]

    const random = Math.floor(Math.random() * images.length);
    return images[random];
}