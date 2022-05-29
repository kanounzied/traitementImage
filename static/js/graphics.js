var ctxL = document.getElementById("lineChart").getContext('2d');
var myLineChart = new Chart(ctxL, {
  type: 'line',
  data: {
    labels: ["0", "150", "255"],
    datasets: [{
      label: "My First dataset",
      lineTension: 0,
      data: [0, 70, 255],
      backgroundColor: [
        'rgba(105, 0, 132, .2)',
      ],
      borderColor: [
        'rgba(200, 99, 132, .7)',
      ],
      borderWidth: 2
    },
    // {
    //   label: "My Second dataset",
    //   data: [28, 48, 40, 19, 86, 27, 90],
    //   backgroundColor: [
    //     'rgba(0, 137, 132, .2)',
    //   ],
    //   borderColor: [
    //     'rgba(0, 10, 130, .7)',
    //   ],
    //   borderWidth: 2
    // }
    ]
  },
  options: {
    responsive: true
  }
});
