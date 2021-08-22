// Similar articles components
let articleRangeBefore = document.getElementById("article-range-before");
let articleRangeAfter = document.getElementById("article-range-after");
let articleDateFilters = document.getElementById("article-date-filters");
let articleDateWarning = document.getElementById("article-date-warning");
let enableDateFiltering = document.getElementById("should-filter-article-range");
let blackListAddButton = document.getElementById("blacklist-add");
let censorImageCheckbox = document.getElementById("censor-images");

// Sensitive content filter components
let filterSlider = document.getElementById("filter-level")

// Render page
function initializeOptions() {
    chrome.storage.sync.get(["enableSimilarArticleFiltering", "articleRangeBefore", "articleRangeAfter", "filterLevel", "censorImages"], (data) => {
        let enableSimilarArticleFiltering = data.enableSimilarArticleFiltering;
        enableDateFiltering.checked = enableSimilarArticleFiltering;
        disableDateFiltering(enableSimilarArticleFiltering);

        let beforeDate = data.articleRangeBefore;
        if (beforeDate != undefined) {
            articleRangeBefore.value = beforeDate;
        }

        let afterDate = data.articleRangeAfter;
        if (afterDate != undefined) {
            articleRangeAfter.value = afterDate;
        }

        checkArticleRangeValidity()

        let filterLevel = data.filterLevel;
        if (filterLevel != undefined) {
            filterSlider.value = filterLevel;
        } else {
            filterSlider.value = "0";
        }

        censorImageCheckbox.checked = data.censorImages;

        updateFilterWarning()

        renderBlackList();
    });

    articleRangeBefore.addEventListener('input', updateArticleRangeBeforeValue);
    articleRangeAfter.addEventListener('input', updateArticleRangeAfterValue);
    enableDateFiltering.addEventListener('input', updateEnableDateFiltering);
    blackListAddButton.addEventListener('click', addToBlackList)
    filterSlider.addEventListener('input', updateExplicitFiltering);
    censorImageCheckbox.addEventListener('input', updateCensorImages);
}

// Article date filtering
function updateEnableDateFiltering(value) {
    let enableSimilarArticleFiltering = value.target.checked;
    chrome.storage.sync.set({enableSimilarArticleFiltering});
    disableDateFiltering(enableSimilarArticleFiltering);
    checkArticleRangeValidity()
}

function disableDateFiltering(enabled) {
    if (!enabled) {
        articleDateFilters.setAttribute("hidden", null);
    } else {
        articleDateFilters.removeAttribute("hidden");
    }
}

function updateArticleRangeBeforeValue(value) {
    let date = value.target.value;
    chrome.storage.sync.set({articleRangeBefore: date});
    checkArticleRangeValidity()
}

function updateArticleRangeAfterValue(value) {
    let date = value.target.value;
    chrome.storage.sync.set({articleRangeAfter: date});
    checkArticleRangeValidity()
}

function checkArticleRangeValidity() {
    if (articleRangeBefore.value == "" || articleRangeAfter.value == "") {
        articleDateWarning.removeAttribute("hidden");
    } else {
        articleDateWarning.setAttribute("hidden", null);
    }
}

// Blacklist
function addToBlackList() {
    let url = document.getElementById("blacklist-input").value.toLowerCase();
    chrome.storage.sync.get("blackList", (data) => {
        if (/^[A-z0-9]*\.[a-z]{2,3}$/.test(url)) {
            if (!data.blackList.includes(url)) {
                data.blackList.push(url);
                chrome.storage.sync.set({blackList: data.blackList});
                renderBlackList();
            }
        } else {
            window.alert("Not a valid url (formatting: \"opbop.com\")");
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

// Content filtering
function updateExplicitFiltering(value) {
    let filterLevel = value.target.value;
    chrome.storage.sync.set({filterLevel});
    updateFilterWarning();
}

function updateFilterWarning() {
    let filterWarning = document.getElementById("filter-description");

    let filterLevel = filterSlider.value;
    if (filterLevel == "0") {
        filterWarning.innerHTML = "Block unsafe text (profane language, prejudiced or hateful language, something that could be NSFW)"
    } else if (filterLevel == "1") {
        filterWarning.innerHTML = "Block sensitive text and above (could be talking about something political, religious, or talking about a protected class)"
    } else {
        filterWarning.innerHTML = "Let all content through, and parse (summarize and simplify) accordingly."
    }
}

function updateCensorImages(value) {
    let censorImages = value.target.checked;
    chrome.storage.sync.set({ censorImages })
}

initializeOptions();
