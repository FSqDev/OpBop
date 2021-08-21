let articleRange = document.getElementById("article-range");
let enableDateFiltering = document.getElementById("should-filter-article-range");
let enableExplicitFilter = document.getElementById("enable-explicit-filter");
let blackListAddButton = document.getElementById("blacklist-add");

function initializeSimilarArticleRangeInput() {
    chrome.storage.sync.get(["enableSimilarArticleFiltering", "articleRange", "enableExplicitFiltering"], (data) => {
        let enableSimilarArticleFiltering = data.enableSimilarArticleFiltering;
        enableDateFiltering.checked = enableSimilarArticleFiltering;
        disableDateFiltering(enableSimilarArticleFiltering);

        let days = data.articleRange;
        if (days != undefined) {
            articleRange.value = days;
        }

        let enableExplicitFiltering = data.enableExplicitFiltering;
        enableExplicitFilter.checked = enableExplicitFiltering;

        renderBlackList();
    });

    articleRange.addEventListener('input', updateArticleRangeValue);
    enableDateFiltering.addEventListener('input', updateEnableDateFiltering);
    enableExplicitFilter.addEventListener('input', updateExplicitFiltering);
    blackListAddButton.addEventListener('click', addToBlackList)

}

function updateEnableDateFiltering(value) {
    let enableSimilarArticleFiltering = value.target.checked;
    chrome.storage.sync.set({enableSimilarArticleFiltering});
    disableDateFiltering(enableSimilarArticleFiltering);
}

function disableDateFiltering(enabled) {
    articleRange.disabled = !enabled;
}

function updateArticleRangeValue(value) {
    let articleRange = value.target.value;
    chrome.storage.sync.set({articleRange});
}

function updateExplicitFiltering(value) {
    let enableExplicitFiltering = value.target.checked;
    chrome.storage.sync.set({enableExplicitFiltering});
}

function addToBlackList() {
    let url = document.getElementById("blacklist-input").value;
    chrome.storage.sync.get("blackList", (data) => {
        if (!data.blackList.includes(url)) {
            data.blackList.push(url);
            chrome.storage.sync.set({blackList: data.blackList});
            renderBlackList();
        }
    });
}

function renderBlackList() {
    let list = document.getElementById("blacklist-list");
    list.innerHTML = "";
    chrome.storage.sync.get("blackList", (data) => {
        let id = 0;
        data.blackList.forEach((entry) => {
            list.appendChild(createBlackListEntry(entry, id++));
        })
    });
}

function createBlackListEntry(url, id) {
    let entry = document.createElement("div");
    entry.id = "blacklist-entry-" + id;
    entry.innerHTML = url;
    let deleteButton = document.createElement("button");
    deleteButton.id = "blacklist-entry-button-" + id;
    deleteButton.innerHTML = "x";
    entry.appendChild(deleteButton);

    deleteButton.addEventListener("click", function () {
        deleteBlackListEntry(id);
    }, false)
    return (entry);
}

function deleteBlackListEntry(id) {
    chrome.storage.sync.get("blackList", (data) => {
        data.blackList.splice(id, 1);
        chrome.storage.sync.set({blackList: data.blackList});
        renderBlackList();
    });
}

initializeSimilarArticleRangeInput();
