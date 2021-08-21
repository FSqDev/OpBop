let parseButton = document.getElementById("parseButton")
let tldr = document.getElementById("tldr-text")
let tldrTab = document.getElementById("tldr-tab")

chrome.storage.sync.get("color", ({color}) => {
    changeColor.style.backgroundColor = color;
});

chrome.storage.sync.get("test", ({text}) => {
    testText.innerHTML = text;
});

// When the button is clicked, inject setPageBackgroundColor into current page
parseButton.addEventListener("click", async () => {
    let [tab] = await chrome.tabs.query({active: true, currentWindow: true});

    let text = tab.url;

    fetch("https://opbop.herokuapp.com/api/banana",
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