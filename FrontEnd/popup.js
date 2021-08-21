let parseButton = document.getElementById("parse-button")
let tldr = document.getElementById("tldr-text")
let tldrTab = document.getElementById("tldr-tab")

// When the button is clicked, inject setPageBackgroundColor into current page
parseButton.addEventListener("click", async () => {
    let [tab] = await chrome.tabs.query({active: true, currentWindow: true});

    let text = tab.url;

    fetch(urls.banana,
        {
            method: "post",
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({mainText: 'ginormous banana'})
        }
    ).then(function (res) {
        res.json().then(function(data) {
            tldr.innerHTML = data.value;
        });
    });
});

//api
const basePath = 'https://opbop.herokuapp.com/'
const apiPath = basePath + 'api/'

const urls = {
    banana : apiPath + 'banana',
}