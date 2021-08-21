

let parseButton = document.getElementById("parse-button")

// When the button is clicked, inject setPageBackgroundColor into current page
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
    chrome.storage.sync.get(["enableSimilarArticleFiltering", "similarArticleRangeBefore", "similarArticleRangeAfter", "enableExplicitFiltering"], data => {
        fetch(urls.main,
            {
                method: "post",
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    url: url,
                    beforeDate: data.enableSimilarArticleFiltering ? data.similarArticleRangeBefore : null,
                    afterDate: data.enableSimilarArticleFiltering ? data.similarArticleRangeAfter : null,
                    filterExplicit: data.enableExplicitFiltering == null ? false : data.enableExplicitFiltering
                })
            }
        ).then(function (res) {
            res.json().then(function(data) {
                populateTldr(data.tldr, data.reduction);
                populateSimplified(data.simplified);
                populateSimilarArticles(data.articles);
                document.body.style.width = "500px"; // TODO: smooth this transition
                document.getElementById("parse-idle").setAttribute("hidden", null)
                document.getElementById("parsed-container").removeAttribute("hidden")
            });
        });
    });
}

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

function populateSimilarArticles(articles) {
    const similarArticleDiv = document.getElementById("nav-similar");
    similarArticleDiv.innerHTML = "";
    articles.forEach((article) => {
        let articleWrapper = document.createElement("a")
        articleWrapper.setAttribute("href", article.url);
        let articleTile = document.createElement("div");
        articleTile.classList.add("article-tile")
        let articleImg = document.createElement("img");
        articleImg.setAttribute("src", article.image);
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
    })
}

//api
const basePath = 'https://opbop.herokuapp.com/'
const apiPath = basePath + 'api/'

const urls = {
    banana : apiPath + 'banana',
    main : apiPath + 'dothethingdev'
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
