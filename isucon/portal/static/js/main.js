$(function() {
    $.ajaxSetup({
        crossDomain: false,
        beforeSend: function(xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    });

    // $('.table').tablesorter();
});



function flipAlpha(colorString) {
    var c = Chart.helpers.color(colorString);
    if (c.rgb.a === 1) {
        c.alpha(0.2);
    } else {
        c.alpha(1);
    }
    return c.rgbString();
}

function renderingGraph (elem, url) {
    fetch(url, {headers: {
        'X-Requested-With': 'XMLHttpRequest'
    }})
        .then((res) => {
            if (res.status !== 200) {
                throw new Error('グラフデータの取得に失敗しました')
            }
            return res.json()
        })
        .then((json) => {
            const myTeamId =
                parseInt(elem?.getAttribute('data-my-team') || '') ||
                undefined;
            const rank = json.ranking.find((rank) => rank.team.id === myTeamId);
            if (rank) {
                for (const dataset of json.graph_datasets) {
                    if (!dataset.label.startsWith(rank.team.name)) {
                        continue;
                    }
                    dataset.borderColor = flipAlpha(dataset.borderColor);
                    dataset.backgroundColor = flipAlpha(dataset.backgroundColor);
                    dataset.borderWidth = 2;
                }
            }


            let ctx = elem.getContext('2d');

            let config = {
				type: 'line',
				data: {
					datasets: json.graph_datasets,
				},
				options: {
					animation: false,
					transitions: {
						resize: {
							animation: {
								duration: 0,
							},
						},
						active: {
							animation: {
								duration: 0,
							},
						},
					},
					hover: {
						mode: 'nearest',
						axis: 'r',
					},
					scales: {
						x: {
							title: {
								display: false,
								text: '時間',
								font: {
									size: 10,
								},
							},
							type: 'time',
							time: {
								parser: 'yyyy-MM-dd HH:mm:ss',
								tooltipFormat: 'yyyy-MM-dd HH:mm:ss',
								displayFormats: {
									millisecond: 'HH:mm:ss',
									second: 'HH:mm:ss',
									minute: 'HH:mm',
									hour: 'MM-dd HH:mm',
									day: 'MM-dd',
									week: 'MM-dd',
									month: 'yyyy-MM',
									quarter: 'yyyy-MM',
									year: 'yyyy',
								},
							},
							min: json.graph_min,
							max: json.graph_max,
							ticks: {
								source: 'auto',
							},
						},
						y: {
							title: {
								display: false,
								text: 'スコア',
								font: {
									size: 10,
								},
							},
							ticks: {
								format: {
									style: 'decimal',
								},
							},
							beginAtZero: true,
							min: 0,
						},
					},
					onClick: function (e) {
						const chart = window.myChart;
						if (!chart) return;
						const points = chart.getElementsAtEventForMode(
							e,
							'nearest',
							{},
							false,
						);

						for (const point of points ?? []) {
							const meta = config.data.datasets[point.datasetIndex];
							meta.backgroundColor = flipAlpha(meta.backgroundColor);
							meta.borderColor = flipAlpha(meta.borderColor);
							chart.update();
						}
					},
					datasets: {
						line: {
							stepped: true,
						},
					},
					plugins: {
						tooltip: {
							mode: 'nearest',
							intersect: false,
							animation: false,
						},
						legend: {
							display: false,
						},
					},
				},
			};
            window.myChart = new Chart(ctx, config);
        })
        .catch((err) => {
            throw new Error(err)
        })
}
