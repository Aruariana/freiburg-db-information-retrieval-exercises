document.querySelector("#search").addEventListener("input", async function() {
    const query = document.querySelector("#search").value;
    console.log("Query: ", query);
    const response_json = await fetch("/api/search?query=" + query).then(response => response.json());

    const resultsContainer = document.querySelector("#result");
        resultsContainer.innerHTML = "";
    if (response_json.results && response_json.results.length > 0) {
        response_json.results.forEach((item, index) => {
            const itemElement = document.createElement("div");
            itemElement.innerHTML = `<b>Result ${index + 1}:</b> ${JSON.stringify(item)}`;
            resultsContainer.appendChild(itemElement);
        })
    }

    document.querySelector("#query").innerHTML = query;
    document.querySelector("#result").innerHTML = resultsContainer.innerHTML;
});