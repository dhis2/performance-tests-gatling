// Create visualization for the test suite data
function createVisualization(data, versionColors) {
    const chartsContainer = d3.select('#charts');
    const toggleButton = d3.select('#toggle-query-params');
    let isCollapsed = true;

    // Set up global toggle
    toggleButton.on('click', function() {
        isCollapsed = !isCollapsed;
        toggleButton.classed('collapsed', isCollapsed);
        
        // Update toggle text
        toggleButton.select('.toggle-text')
            .text(isCollapsed ? 'Show Query Parameters' : 'Hide Query Parameters');
        
        // Toggle all query parameter containers
        d3.selectAll('.query-params-container')
            .classed('collapsed', isCollapsed);
    });

    // Set initial state of toggle button
    toggleButton.classed('collapsed', isCollapsed);
    toggleButton.select('.toggle-text')
        .text('Show Query Parameters');

    chartsContainer.html('');

    data.scenarios.forEach((scenario, index) => {
        // Create chart container
        const chartDiv = chartsContainer.append('div')
            .attr('class', 'chart-container');

        // Add query info with formatted parameters
        const queryInfo = chartDiv.append('div')
            .attr('class', 'query-info');
        
        // Add query number
        queryInfo.append('div')
            .attr('class', 'query-title')
            .text(`Query ${index + 1}`);
        
        const formattedQuery = formatQueryParams(scenario.query);
        const hasQueryParams = scenario.query.includes('?');
        
        // Add full query with bold endpoint
        const fullQueryDiv = queryInfo.append('div')
            .attr('class', 'full-query')
            .html(hasQueryParams 
                ? `<span class="endpoint">${scenario.query.split('?')[0]}</span>?${scenario.query.split('?')[1]}`
                : `<span class="endpoint">${scenario.query}</span>`);
        
        // Only add parameters container if there are query parameters
        if (hasQueryParams) {
            const paramsContainer = queryInfo.append('div')
                .attr('class', 'query-params-container')
                .classed('collapsed', isCollapsed)
                .html(formattedQuery);
        }

        // Create plot container
        const plotContainer = chartDiv.append('div')
            .attr('class', 'plot-container')
            .style('width', '100%')
            .style('height', '200px');

        // Prepare data for Plotly
        const releases = scenario.expectations.map(e => e.release);
        const meanValues = scenario.expectations.map(e => e.mean);
        const maxValues = scenario.expectations.map(e => e.max);
        const minValues = scenario.expectations.map(e => e.min);

        // Create arrays of objects to sort
        const data = releases.map((release, i) => ({
            release,
            mean: meanValues[i],
            max: maxValues[i],
            min: minValues[i]
        }));

        // Sort by release number in descending order
        data.sort((a, b) => {
            const aNum = parseInt(a.release.match(/\d+/)[0]);
            const bNum = parseInt(b.release.match(/\d+/)[0]);
            return aNum - bNum; // Descending sort (highest first)
        });

        // Extract sorted arrays
        const sortedReleases = data.map(d => d.release);
        const sortedMeanValues = data.map(d => d.mean);
        const sortedMaxValues = data.map(d => d.max);
        const sortedMinValues = data.map(d => d.min);

        // Create error bar data
        const errorBars = {
            type: 'symmetric',
            array: sortedMaxValues.map((max, i) => max - sortedMeanValues[i]),
            arrayminus: sortedMeanValues.map((mean, i) => mean - sortedMinValues[i]),
            color: sortedReleases.map(r => {
                // Convert hex to RGB
                const hex = versionColors[r].substring(1);
                const rr = parseInt(hex.substring(0, 2), 16);
                const gg = parseInt(hex.substring(2, 4), 16);
                const bb = parseInt(hex.substring(4, 6), 16);
                
                // Darken by 30%
                const darken = 0.3;
                const dr = Math.max(0, Math.floor(rr * (1 - darken)));
                const dg = Math.max(0, Math.floor(gg * (1 - darken)));
                const db = Math.max(0, Math.floor(bb * (1 - darken)));
                
                // Convert back to hex
                return `#${dr.toString(16).padStart(2, '0')}${dg.toString(16).padStart(2, '0')}${db.toString(16).padStart(2, '0')}`;
            })
        };

        // Create Plotly trace
        const trace = {
            type: 'bar',
            x: sortedMeanValues,
            y: sortedReleases.map((_, i) => sortedReleases.length - 1 - i),
            orientation: 'h',
            error_x: errorBars,
            marker: {
                color: sortedReleases.map(r => versionColors[r]),
                opacity: 0.7
            },
            hovertemplate: 
                'Mean: %{x:,.0f}ms<br>' +
                'Min: %{customdata[0]:,.0f}ms<br>' +
                'Max: %{customdata[1]:,.0f}ms<br>' +
                '<extra></extra>',
            customdata: sortedReleases.map((_, i) => [sortedMinValues[i], sortedMaxValues[i]])
        };

        // Layout configuration
        const layout = {
            title: {
                text: `Test ${index + 1} Response Times (ms)`,
                font: { size: 12, color: '#e0e0e0' }
            },
            xaxis: {
                // title: 'Response Time (ms)',
                tickformat: ',d',
                color: '#e0e0e0',
                gridcolor: '#404040',
                linecolor: '#404040',
                tickcolor: '#e0e0e0'
            },
            yaxis: {
                title: '',
                automargin: true,
                tickmode: 'array',
                tickvals: sortedReleases.map((_, i) => sortedReleases.length - 1 - i),
                ticktext: sortedReleases,
                tickfont: {
                    size: 12,
                    weight: 'bold',
                    color: '#e0e0e0'
                },
                showgrid: false,
                zeroline: false,
                range: [-0.5, sortedReleases.length - 0.5],
                ticklen: 0,
                tickwidth: 20,
                side: 'left',
                ticklabelposition: 'outside'
            },
            margin: {
                l: 80,
                r: 20,
                t: 20,
                b: 20
            },
            showlegend: false,
            hovermode: 'closest',
            height: 200,
            bargap: 0.3,
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            annotations: sortedReleases.map((_, i) => ({
                x: sortedMeanValues[i],
                y: sortedReleases.length - 1 - i,
                text: sortedMeanValues[i].toLocaleString() + 'ms',
                showarrow: false,
                font: {
                    size: 10,
                    color: '#b0b0b0'
                },
                xanchor: 'left',
                yanchor: 'middle',
                xshift: 5
            }))
        };

        // Create the plot
        Plotly.newPlot(plotContainer.node(), [trace], layout, {
            displayModeBar: false,
            responsive: true
        });

        // Add resize observer to handle size changes
        const resizeObserver = new ResizeObserver(entries => {
            for (const entry of entries) {
                Plotly.Plots.resize(entry.target);
            }
        });

        resizeObserver.observe(plotContainer.node());
    });
} 