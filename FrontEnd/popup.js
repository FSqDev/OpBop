let parseButton = document.getElementById("parse-button")

// When the button is clicked, inject setPageBackgroundColor into current page
parseButton.addEventListener("click", async () => {
    let [tab] = await chrome.tabs.query({active: true, currentWindow: true});
    let url = tab.url;

    parse(url);
});

const parse = (url) => {
    fetch(urls.main,
        {
            method: "post",
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({url: url})
        }
    ).then(function (res) {
        res.json().then(function(data) {
            populateTldr(data.tldr);
            populateSimplified(data.simplified);
            populateSimilarArticles(data.articles);
        });
    });
}

const populateTldr = (tldrText) => {
    let tldr = document.getElementById("tldr-text");
    tldr.innerHTML = tldrText;
}

const populateSimplified = (simiplifiedText) => {
    let simplified = document.getElementById("simplified-text");
    simplified.innerText = simiplifiedText;
}

const populateSimilarArticles = (articles) => {
    const similarArticleList = document.getElementById("related-articles");
    similarArticleList.innerHTML = "";
    articles.forEach((article) => {
        let articleLi = document.createElement("LI");
        let articleLink = document.createElement("a")
        articleLink.href = article.url;
        let articleTitle = document.createTextNode(article.title);
        articleLink.appendChild(articleTitle);
        articleLi.appendChild(articleLink);
        similarArticleList.appendChild(articleLi);
    })
}

//api
const basePath = 'https://opbop.herokuapp.com/'
const apiPath = basePath + 'api/'

const urls = {
    banana : apiPath + 'banana',
    main : apiPath + 'dothethingdev'
}