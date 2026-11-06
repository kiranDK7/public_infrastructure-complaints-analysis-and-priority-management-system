/**
 * SMART CIVICCARE 2.0 - DASHBOARD & FORECASTING VISUALIZATIONS
 */

document.addEventListener('DOMContentLoaded', function () {
  initDashboardCharts();
  initForecastingChart();
});

function initDashboardCharts() {
  const catCanvas = document.getElementById('chartCategory');
  const priCanvas = document.getElementById('chartPriority');
  const deptCanvas = document.getElementById('chartDepartment');

  if (!catCanvas && !priCanvas && !deptCanvas) return;

  fetch('/api/analytics/charts')
    .then(res => res.json())
    .then(data => {
      // 1. Category Distribution
      if (catCanvas) {
        new Chart(catCanvas, {
          type: 'doughnut',
          data: {
            labels: data.categories.labels,
            datasets: [{
              data: data.categories.counts,
              backgroundColor: ['#0d9488', '#0284c7', '#ca8a04', '#eab308', '#dc2626', '#16a34a'],
              borderWidth: 2,
              borderColor: '#ffffff'
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { position: 'bottom', labels: { boxWidth: 10, font: { size: 11 } } }
            },
            cutout: '65%'
          }
        });
      }

      // 2. Priority Risk
      if (priCanvas) {
        new Chart(priCanvas, {
          type: 'bar',
          data: {
            labels: data.priorities.labels,
            datasets: [{
              label: 'Complaints',
              data: data.priorities.counts,
              backgroundColor: ['#ef4444', '#f59e0b', '#10b981'],
              borderRadius: 6
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true, ticks: { stepSize: 2 } } }
          }
        });
      }

      // 3. Department Performance
      if (deptCanvas && data.departments) {
        new Chart(deptCanvas, {
          type: 'bar',
          data: {
            labels: data.departments.map(d => d.code),
            datasets: [
              {
                label: 'Assigned Work',
                data: data.departments.map(d => d.total),
                backgroundColor: '#cbd5e1',
                borderRadius: 4
              },
              {
                label: 'Completed & Verified',
                data: data.departments.map(d => d.resolved),
                backgroundColor: '#0d9488',
                borderRadius: 4
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: { legend: { position: 'top', labels: { boxWidth: 12 } } },
            scales: { x: { beginAtZero: true, ticks: { stepSize: 1 } } }
          }
        });
      }
    })
    .catch(err => console.error("Dashboard analytics error:", err));
}

function initForecastingChart() {
  const forecastCanvas = document.getElementById('chartForecastCurve');
  if (!forecastCanvas) return;

  const horizon = forecastCanvas.getAttribute('data-horizon') || 30;
  const ward = forecastCanvas.getAttribute('data-ward') || 'Ward 42';

  fetch(`/api/forecasting/curve?horizon=${horizon}&ward=${encodeURIComponent(ward)}`)
    .then(res => res.json())
    .then(resData => {
      if (!resData.success) return;
      const curve = resData.data;

      new Chart(forecastCanvas, {
        type: 'line',
        data: {
          labels: curve.labels,
          datasets: [
            {
              label: 'Upper Confidence Limit (95%)',
              data: curve.upper_bound,
              borderColor: 'rgba(239, 68, 68, 0.4)',
              backgroundColor: 'rgba(239, 68, 68, 0.08)',
              borderDash: [5, 5],
              fill: '+1',
              tension: 0.35,
              pointRadius: 0
            },
            {
              label: 'Projected Complaint Demand',
              data: curve.projected,
              borderColor: '#0d9488',
              backgroundColor: 'rgba(13, 148, 136, 0.15)',
              borderWidth: 3,
              tension: 0.35,
              pointBackgroundColor: '#0d9488',
              pointRadius: 4,
              fill: false
            },
            {
              label: 'Lower Confidence Limit',
              data: curve.lower_bound,
              borderColor: 'rgba(2, 132, 199, 0.4)',
              borderDash: [5, 5],
              tension: 0.35,
              pointRadius: 0,
              fill: false
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'top', labels: { boxWidth: 12, font: { size: 11 } } },
            tooltip: { mode: 'index', intersect: false }
          },
          scales: {
            y: {
              beginAtZero: true,
              title: { display: true, text: 'Expected Weekly Complaints' }
            },
            x: {
              title: { display: true, text: 'Projection Timeline' }
            }
          }
        }
      });
    })
    .catch(err => console.error("Forecast curve error:", err));
}

