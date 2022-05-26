// retrieve canvas element from `trend_chart.html` to plot trend chart for hotel booking income.
var ctx = document.getElementById('bar_chart').getContext('2d');


$(document).ready(function () {
    $('#username').change(function () {
        var username = $('#username').val();
        $.ajax({
            url: '/dashboard/bar_chart_by_user',
            type: 'POST',
            data: {
                username: username
            },
            success: function (data) {

                // retrieve hotel booking income data (chart dimension) and x-axis labels (chart labels).
                var xLabels = data.chartDim;
                var yLabels = data.labels;
                var due_target = data.user_name;

                console.log(yLabels)
                console.log(xLabels)

                // crude way to clear the chart as we got new data coming as we click on the select dropdown
                // TODO: consider to implement supdate instead
                let chartStatus = Chart.getChart("bar_chart")
                if (chartStatus) {
                    chartStatus.destroy()
                }

                if (due_target != "Select One") {
                    // given existing canvas element, create a trend chart for display of income data
                    var barChart = new Chart(ctx, {
                        type: "bar",
                        data: {
                            labels: xLabels,
                            datasets: [
                                {
                                    label: `Booking Due Per User By ${due_target}`,
                                    data: yLabels,
                                    backgroundColor: "#c9a946"
                                }
                            ]
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
                                        padding: 10,
                                    }
                                }
                            }
                        }
                    });
                }
                else {
                    ctx.font = "20px Montserrat";
                    ctx.textAlign = "center";
                    ctx.fillText("Please Select an Option!", ctx.canvas.width / 2, ctx.canvas.height / 2);
                }
            }
        });
    });
});