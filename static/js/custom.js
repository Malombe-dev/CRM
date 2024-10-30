// custom.js

// Function to fetch data and render charts
function renderCharts(locationData, loanStatusData) {
    // Data for Location Chart (Orange bars)
    const locationChartData = {
        labels: locationData.labels,
        datasets: [{
            label: 'Location',
            data: locationData.data,
            backgroundColor: 'orange',
            borderColor: 'black',
            borderWidth: 1
        }]
    };

    // Data for Loan Status Chart (Blue bars)
    const loanStatusChartData = {
        labels: loanStatusData.labels,
        datasets: [{
            label: 'Loan Status',
            data: loanStatusData.data,
            backgroundColor: 'rgba(54, 162, 235, 0.6)',
            borderColor: 'black',
            borderWidth: 1
        }]
    };

    // Configuration and rendering for Location Chart
    const locationConfig = {
        type: 'bar',
        data: locationChartData,
        options: {
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { font: { weight: 'bold', size: 14 }}
                },
                y: {
                    beginAtZero: true,
                    grid: { display: false },
                    ticks: { font: { weight: 'bold', size: 14 }, stepSize: 1 }
                }
            },
            plugins: {
                legend: { labels: { font: { weight: 'bold' }}}
            }
        }
    };

    // Configuration and rendering for Loan Status Chart
    const loanConfig = {
        type: 'bar',
        data: loanStatusChartData,
        options: {
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { font: { weight: 'bold', size: 14 }}
                },
                y: {
                    beginAtZero: true,
                    grid: { display: false },
                    ticks: { font: { weight: 'bold', size: 14 }, stepSize: 1 }
                }
            },
            plugins: {
                legend: { labels: { font: { weight: 'bold' }}}
            }
        }
    };

    // Check if the canvas elements exist
    const locationChartElement = document.getElementById('locationChart');
    const loanStatusChartElement = document.getElementById('loanStatusChart');

    // Ensure the chart elements exist before initializing
    if (locationChartElement) {
        new Chart(locationChartElement, locationConfig);
    } else {
        console.error('Location chart canvas element not found.');
    }

    if (loanStatusChartElement) {
        new Chart(loanStatusChartElement, loanConfig);
    } else {
        console.error('Loan status chart canvas element not found.');
    }
}

// Fetch data and render charts when the document is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Retrieve data from the template
    const locationData = {
        labels: {{ location_data | map(attribute=0) | list | tojson | safe }},
        data: {{ location_data | map(attribute=1) | list | tojson | safe }}
    };
    const loanStatusData = {
        labels: {{ loan_status_data | map(attribute=0) | list | tojson | safe }},
        data: {{ loan_status_data | map(attribute=1) | list | tojson | safe }}
    };

    // Log the data for debugging
    console.log(locationData, loanStatusData);

    // Call the function to render charts
    renderCharts(locationData, loanStatusData);
});
