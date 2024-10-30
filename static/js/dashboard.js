// Example chart script for Mobile/Desktop Users
var ctx = document.getElementById('mobileDesktopChart').getContext('2d');
var mobileDesktopChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        datasets: [{
            label: 'Mobile Users',
            data: [50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160],
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
        }, {
            label: 'Desktop Users',
            data: [30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140],
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            borderColor: 'rgba(255, 99, 132, 1)',
            borderWidth: 1
        }]
    },
    options: {
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});

// Example script for the radar chart (Interests)
var ctx2 = document.getElementById('interestsChart').getContext('2d');
var interestsChart = new Chart(ctx2, {
    type: 'radar',
    data: {
        labels: ['Technology', 'Sports', 'Media', 'Gaming', 'Arts'],
        datasets: [{
            label: 'User Interests',
            data: [80, 20, 70, 40, 60],
            backgroundColor: 'rgba(153, 102, 255, 0.2)',
            borderColor: 'rgba(153, 102, 255, 1)',
            borderWidth: 1
        }]
    },
    options: {
        scales: {
            r: {
                beginAtZero: true
            }
        }
    }
});

