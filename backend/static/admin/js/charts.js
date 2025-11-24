/**
 * Chart.js Configuration and Initialization
 * Handles all chart visualizations for the admin dashboard
 */

(function() {
  'use strict';

  // Wait for DOM and Chart.js to be ready
  document.addEventListener('DOMContentLoaded', function() {
    // Check if Chart.js is loaded
    if (typeof Chart === 'undefined') {
      console.error('Chart.js is not loaded');
      return;
    }

    initializeCharts();
  });

  /**
   * Initialize all charts on the page
   */
  function initializeCharts() {
    initAttendanceTrendChart();
    initActivityHeatmap();
  }

  /**
   * Initialize attendance trend line chart
   */
  function initAttendanceTrendChart() {
    const canvas = document.getElementById('attendanceTrendChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');

    // Get theme colors from CSS variables
    const primaryColor = getComputedStyle(document.documentElement)
      .getPropertyValue('--primary-600').trim();
    const secondaryColor = getComputedStyle(document.documentElement)
      .getPropertyValue('--secondary-500').trim();

    // Sample data - will be replaced with real data from backend
    const data = {
      labels: generateDateLabels(30),
      datasets: [{
        label: 'Attendance Rate (%)',
        data: generateSampleData(30, 70, 95),
        borderColor: primaryColor,
        backgroundColor: createGradient(ctx, primaryColor),
        borderWidth: 2,
        fill: true,
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 6,
        pointHoverBackgroundColor: primaryColor,
        pointHoverBorderColor: '#ffffff',
        pointHoverBorderWidth: 2,
      }]
    };

    const config = {
      type: 'line',
      data: data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          intersect: false,
          mode: 'index',
        },
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            padding: 12,
            titleFont: {
              size: 14,
              weight: '600',
            },
            bodyFont: {
              size: 13,
            },
            borderColor: 'rgba(255, 255, 255, 0.1)',
            borderWidth: 1,
            displayColors: false,
            callbacks: {
              label: function(context) {
                return 'Attendance: ' + context.parsed.y.toFixed(1) + '%';
              }
            }
          }
        },
        scales: {
          x: {
            grid: {
              display: false,
            },
            ticks: {
              maxRotation: 0,
              autoSkipPadding: 20,
              font: {
                size: 11,
              }
            }
          },
          y: {
            beginAtZero: true,
            max: 100,
            grid: {
              color: 'rgba(0, 0, 0, 0.05)',
            },
            ticks: {
              callback: function(value) {
                return value + '%';
              },
              font: {
                size: 11,
              }
            }
          }
        }
      }
    };

    const chart = new Chart(ctx, config);

    // Handle filter buttons
    const filterButtons = document.querySelectorAll('.chart-filters .filter-btn');
    filterButtons.forEach(function(btn) {
      btn.addEventListener('click', function() {
        // Remove active class from all buttons
        filterButtons.forEach(function(b) {
          b.classList.remove('active');
        });
        
        // Add active class to clicked button
        this.classList.add('active');
        
        // Get selected range
        const range = this.getAttribute('data-range');
        
        // Update chart data based on range
        updateChartData(chart, range);
      });
    });
  }

  /**
   * Initialize activity heatmap
   */
  function initActivityHeatmap() {
    const container = document.getElementById('activityHeatmap');
    if (!container) return;

    // Days of week
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    
    // Generate sample heatmap data (7 days x 24 hours)
    const heatmapData = generateHeatmapData();

    // Create heatmap HTML
    let html = '<div class="heatmap-wrapper">';
    
    // Add hour labels
    html += '<div class="heatmap-hours">';
    for (let hour = 0; hour < 24; hour++) {
      html += `<div class="hour-label">${hour}</div>`;
    }
    html += '</div>';
    
    // Add heatmap grid
    html += '<div class="heatmap-grid-container">';
    
    // Add day labels
    html += '<div class="heatmap-days">';
    days.forEach(function(day) {
      html += `<div class="day-label">${day}</div>`;
    });
    html += '</div>';
    
    // Add heatmap cells
    html += '<div class="heatmap-grid">';
    for (let day = 0; day < 7; day++) {
      for (let hour = 0; hour < 24; hour++) {
        const value = heatmapData[day][hour];
        const level = getHeatmapLevel(value);
        html += `<div class="heatmap-cell heatmap-cell--level-${level}" 
                      data-day="${days[day]}" 
                      data-hour="${hour}" 
                      data-value="${value}"
                      title="${days[day]} ${hour}:00 - ${value} activities"></div>`;
      }
    }
    html += '</div>';
    
    html += '</div>';
    
    // Add legend
    html += '<div class="heatmap-legend">';
    html += '<span class="legend-label">Less</span>';
    for (let i = 0; i <= 4; i++) {
      html += `<div class="legend-cell heatmap-cell--level-${i}"></div>`;
    }
    html += '<span class="legend-label">More</span>';
    html += '</div>';
    
    html += '</div>';
    
    container.innerHTML = html;
  }

  /**
   * Create gradient for chart fill
   */
  function createGradient(ctx, color) {
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, color + '40'); // 25% opacity
    gradient.addColorStop(1, color + '00'); // 0% opacity
    return gradient;
  }

  /**
   * Generate date labels for chart
   */
  function generateDateLabels(days) {
    const labels = [];
    const today = new Date();
    
    for (let i = days - 1; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
    }
    
    return labels;
  }

  /**
   * Generate sample data for chart
   */
  function generateSampleData(count, min, max) {
    const data = [];
    for (let i = 0; i < count; i++) {
      data.push(Math.floor(Math.random() * (max - min + 1)) + min);
    }
    return data;
  }

  /**
   * Generate sample heatmap data
   */
  function generateHeatmapData() {
    const data = [];
    for (let day = 0; day < 7; day++) {
      const dayData = [];
      for (let hour = 0; hour < 24; hour++) {
        // Generate more activity during typical class hours (8-18)
        let value;
        if (hour >= 8 && hour <= 18 && day < 5) {
          value = Math.floor(Math.random() * 50) + 10;
        } else {
          value = Math.floor(Math.random() * 10);
        }
        dayData.push(value);
      }
      data.push(dayData);
    }
    return data;
  }

  /**
   * Get heatmap intensity level (0-4)
   */
  function getHeatmapLevel(value) {
    if (value === 0) return 0;
    if (value <= 10) return 1;
    if (value <= 20) return 2;
    if (value <= 35) return 3;
    return 4;
  }

  /**
   * Update chart data based on selected time range
   */
  function updateChartData(chart, range) {
    let days;
    switch(range) {
      case 'week':
        days = 7;
        break;
      case 'month':
        days = 30;
        break;
      case 'year':
        days = 365;
        break;
      default:
        days = 30;
    }

    chart.data.labels = generateDateLabels(days);
    chart.data.datasets[0].data = generateSampleData(days, 70, 95);
    chart.update();
  }

  // Expose functions to global scope if needed
  window.AdminCharts = {
    initializeCharts: initializeCharts,
    updateChartData: updateChartData
  };

})();
