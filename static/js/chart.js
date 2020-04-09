document.addEventListener("DOMContentLoaded", () => {
  const options = {
    chart: {
      type: "column",
      zoomType: "xy",
    },
    title: {
      text: "Complete Chart",
    },
    yAxis: {
      text: "Y axis features",
    },
  };

  fetch("Sample.csv")
    .then((res) => {
      return res.text();
    })
    .then((csv) => {
      options.data = {
        csv,
      };
      Highcharts.chart("container", option);
    });
});
