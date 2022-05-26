// retrieve canvas element from `trend_chart.html` to plot trend chart for hotel booking income.
var ctx = document.getElementById('trend_chart').getContext('2d')

/**
 * [Function to map hotel income data in appropriate format for chart.js]
 * @param  {[Array]} num Array for hotel booking income, where -1 is for no data.
 * @return {[Number|Null]}       null, if no data, else return the actual hotel booking income.
 */
function replaceMissingData(num) {
    if (num == -1)
        return null;
    else
        return num;
}

$.ajax({
    url: "/dashboard/trend_chart",
    type: "POST",
    data: {},
    error: function () {
        alert("Error. Issues with loading data, please refresh the page!");
    },
    success: function (data, status, xhr) {

        var hotelBookingsIncome = {};

        // retrieve hotel booking income data (chart dimension) and x-axis labels (chart labels).
        var hotelBookingsIncome = data.chartDim;
        var dateLabels = data.labels;
        console.log(dateLabels)

        var incomeLabels = [];
        var incomeData = [];

        for (const [key, values] of Object.entries(hotelBookingsIncome)) {
            incomeLabels.push(key);
            let newValues = values.map(replaceMissingData);
            incomeData.push(newValues);
        }

        // given existing canvas element, create a trend chart for display of income data
        var trendChart = new Chart(ctx, {
            type: "line",
            data: {
                labels: dateLabels,
                datasets: []
            },
            options: {
                responsive: true,
                maintainaspectratio: false,
                scales: {
                    y: {
                        ticks: {
                            beginAtZero: true,
                        }
                    },
                    x: {
                        ticks: {
                            autoSkip: true,
                            padding: 10
                        }
                    }
                }
            }
        });

        // iterate through all the income labels (all hotels has same length in processed income data)
        for (i = 0; i < incomeLabels.length; i++) {
            trendChart.data.datasets.push({
                label: incomeLabels[i],
                type: "line",
                borderColor: '#' + (0x1100000 + Math.random() * 0xffffff).toString(16).substr(1, 6),
                backgroundColor: "rgba(249, 238, 236, 0.74)",
                data: incomeData[i],
                spanGaps: true
            });
            trendChart.update();
        }

    }
})