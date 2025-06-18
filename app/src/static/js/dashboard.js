// Chart Theme Configuration
const chartTheme = {
    dark: {
        color: '#fff',
        gridColor: 'rgba(255, 255, 255, 0.1)',
        borderColor: 'rgba(255, 255, 255, 0.1)'
    },
    light: {
        color: '#666',
        gridColor: 'rgba(0, 0, 0, 0.1)',
        borderColor: 'rgba(0, 0, 0, 0.1)'
    }
};

// Update chart theme based on current mode
function updateChartTheme(chart, isDark) {
    const theme = isDark ? chartTheme.dark : chartTheme.light;
    
    chart.options.scales.x.grid.color = theme.gridColor;
    chart.options.scales.y.grid.color = theme.gridColor;
    chart.options.scales.x.ticks.color = theme.color;
    chart.options.scales.y.ticks.color = theme.color;
    chart.options.plugins.legend.labels.color = theme.color;
    
    chart.update();
}

// Format currency for charts
function formatCurrency(value) {
    return new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
}

// Format percentage for charts
function formatPercentage(value) {
    return new Intl.NumberFormat('id-ID', {
        style: 'percent',
        minimumFractionDigits: 1,
        maximumFractionDigits: 1
    }).format(value / 100);
}

// Gradient background for charts
function createGradient(ctx, colors) {
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    colors.forEach((color, index) => {
        gradient.addColorStop(index / (colors.length - 1), color);
    });
    return gradient;
}