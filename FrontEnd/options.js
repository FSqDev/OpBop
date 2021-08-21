let articleRange = document.getElementById("article-range");
let enableDateFiltering = document.getElementById("should-filter-article-range");
let enableExplicitFilter = document.getElementById("enable-explicit-filter");

function initializeSimilarArticleRangeInput() {
    chrome.storage.sync.get(["enableSimilarArticleFiltering", "articleRange", "enableExplicitFiltering"], (data) => {
        let enableSimilarArticleFiltering = data.enableSimilarArticleFiltering;
        enableDateFiltering.checked = enableSimilarArticleFiltering;
        disableDateFiltering(enableSimilarArticleFiltering);

        let days = data.articleRange;
        if (days != null) {
            articleRange.value = days;
        }

        let enableExplicitFiltering = data.enableExplicitFiltering;
        enableExplicitFilter.checked = enableExplicitFiltering;
    });

    articleRange.addEventListener('input', updateArticleRangeValue);
    enableDateFiltering.addEventListener('input', updateEnableDateFiltering);
    enableExplicitFilter.addEventListener('input', updateExplicitFiltering)
}

function updateEnableDateFiltering(value) {
    let enableSimilarArticleFiltering = value.target.checked;
    chrome.storage.sync.set({ enableSimilarArticleFiltering });
    disableDateFiltering(enableSimilarArticleFiltering);
}

function disableDateFiltering(enabled) {
    articleRange.disabled = !enabled;
}

function updateArticleRangeValue(value) {
    let articleRange = value.target.value;
    chrome.storage.sync.set({ articleRange });
}

function updateExplicitFiltering(value) {
    let enableExplicitFiltering = value.target.checked;
    chrome.storage.sync.set({ enableExplicitFiltering });
}

initializeSimilarArticleRangeInput();
