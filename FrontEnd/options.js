let beforeDate = document.getElementById("article-range-before");
let afterDate = document.getElementById("article-range-after");
let enableDateFiltering = document.getElementById("should-filter-article-range");
let enableExplicitFilter = document.getElementById("enable-explicit-filter");

function initializeSimilarArticleRangeInput() {
    chrome.storage.sync.get("enableSimilarArticleFiltering", (data) => {
        let enabled = data.enableSimilarArticleFiltering;
        enableDateFiltering.checked = enabled;
        disableDateFiltering(enabled);
    });

    chrome.storage.sync.get("similarArticleRangeBefore", (data) => {
        let date = data.similarArticleRangeBefore;
        if (date != null) {
            beforeDate.value = date;
        }
    });

    chrome.storage.sync.get("similarArticleRangeAfter", (data) => {
        let date = data.similarArticleRangeAfter;
        if (date != null) {
            afterDate.value = date;
        }
    });

    chrome.storage.sync.get("enableExplicitFiltering", (data) => {
        let enabled = data.enableExplicitFiltering;
        enableExplicitFilter.checked = enabled;
    });

    beforeDate.addEventListener('input', updateBeforeValue);
    afterDate.addEventListener('input', updateAfterValue);
    enableDateFiltering.addEventListener('input', updateEnableDateFiltering);
    enableExplicitFilter.addEventListener('input', updateExplicitFiltering)
}

function updateEnableDateFiltering(value) {
    let enableSimilarArticleFiltering = value.target.checked;
    chrome.storage.sync.set({ enableSimilarArticleFiltering });
    disableDateFiltering(enableSimilarArticleFiltering);
}

function disableDateFiltering(enabled) {
    beforeDate.disabled = !enabled;
    afterDate.disabled = !enabled;
}

function updateBeforeValue(value) {
    let similarArticleRangeBefore = value.target.value;
    chrome.storage.sync.set({ similarArticleRangeBefore });
}

function updateAfterValue(value) {
    let similarArticleRangeAfter = value.target.value;
    chrome.storage.sync.set({ similarArticleRangeAfter });
}

function updateExplicitFiltering(value) {
    let enableExplicitFiltering = value.target.checked;
    chrome.storage.sync.set({ enableExplicitFiltering });
}

initializeSimilarArticleRangeInput();
