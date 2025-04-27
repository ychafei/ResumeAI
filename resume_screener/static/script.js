function filterScores() {
    let filterValue = document.getElementById("filter").value;
    let rows = document.getElementById("applicantTable").getElementsByTagName("tr");

    for (let row of rows) {
        let score = parseFloat(row.getAttribute("data-score"));
        if (filterValue === "above_75" && score < 75) {
            row.style.display = "none";
        } else if (filterValue === "below_75" && score >= 75) {
            row.style.display = "none";
        } else {
            row.style.display = "";
        }
    }
}
