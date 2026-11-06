/**
 * Chart.js Analytics Visualizations for Admin Dashboard
 */

document.addEventListener('DOMContentLoaded', function () {
  initAdminCharts();
});

function initAdminCharts() {
  const catCanvas = document.getElementById('chartCategory');
  const priCanvas = document.getElementById('chartPriority');
  const statCanvas = document.getElementById('chartStatus');
  const deptCanvas = document.getElementById('chartDepartment');

  if (!catCanvas && !priCanvas && !statCanvas && !deptCanvas) return;

  fetch('/api/analytics/charts')
    .then(res => res.json())
    .then(data => {
      // 1. Category Distribution (Doughnut)
      if (catCanvas) {
        new Chart(catCanvas, {
          type: 'doughnut',
          data: {
            labels: data.categories.labels,
            datasets: [{
              data: data.categories.counts,
              backgroundColor: [
                '#0d9488', '#0284c7', '#10b981', '#f59e0b', '#6366f1', '#ec4899'
              ],
              borderWidth: 2,
              borderColor: '#ffffff'
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } }
            },
            cutout: '65%'
          }
        });
      }

      // 2. Priority Distribution (Bar)
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
            plugins: {
              legend: { display: false }
            },
            scales: {
              y: { beginAtZero: true, ticks: { stepSize: 1 } },
              x: { grid: { display: false } }
            }
          }
        });
      }

      // 3. Status Distribution (Pie / Doughnut)
      if (statCanvas) {
        new Chart(statCanvas, {
          type: 'doughnut',
          data: {
            labels: data.statuses.labels,
            datasets: [{
              data: data.statuses.counts,
              backgroundColor: [
                '#64748b', '#8b5cf6', '#0284c7', '#d97706', '#10b981', '#ef4444'
              ],
              borderWidth: 2,
              borderColor: '#ffffff'
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } }
            },
            cutout: '60%'
          }
        });
      }

      // 4. Department Performance (Horizontal Bar)
      if (deptCanvas && data.departments) {
        const deptLabels = data.departments.map(d => d.code);
        const totalAssigned = data.departments.map(d => d.total);
        const totalResolved = data.departments.map(d => d.resolved);

        new Chart(deptCanvas, {
          type: 'bar',
          data: {
            labels: deptLabels,
            datasets: [
              {
                label: 'Assigned Work',
                data: totalAssigned,
                backgroundColor: '#cbd5e1',
                borderRadius: 4
              },
              {
                label: 'Resolved',
                data: totalResolved,
                backgroundColor: '#0d9488',
                borderRadius: 4
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
              legend: { position: 'top', labels: { boxWidth: 12, font: { size: 11 } } }
            },
            scales: {
              x: { beginAtZero: true, ticks: { stepSize: 1 } },
              y: { grid: { display: false } }
            }
          }
        });
      }
    })
    .catch(err => console.error('Error fetching chart data:', err));
}

