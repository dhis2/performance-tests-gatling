// Available databases and their test suites
let testSuites = {
};

// Color palette for versions
const colorPalette = [
    '#36a2eb', '#ff6384', '#4bc0c0', '#ff9f40',
    '#9966ff', '#ffcd56', '#c9cbcf', '#8c9eff',
    '#ff8a80', '#a7ffeb', '#b388ff', '#ff80ab'
];

// DOM Elements
const navContent = document.getElementById('nav-content');
const chartsContainer = document.getElementById('charts');
const tooltip = document.getElementById('tooltip');

// Initialize navigation by loading the test structure JSON
async function initializeNavigation() {
    try {
        const response = await fetch('data/test_structure.json');
        if (!response.ok) throw new Error('Failed to load test structure');
        
        const testStructure = await response.json();
        testSuites = testStructure.databases;
        
        // For each database, create its navigation group
        Object.entries(testStructure.databases).forEach(([dbName, suites]) => {
            const dbGroup = document.createElement('div');
            dbGroup.className = 'db-group';
            
            const dbTitle = document.createElement('div');
            dbTitle.className = 'db-title';
            dbTitle.textContent = dbName.toUpperCase();
            dbGroup.appendChild(dbTitle);
            
            const suiteList = document.createElement('ul');
            suiteList.className = 'suite-list';
            
            // Add test suites for this database
            Object.entries(suites).forEach(([suiteName, resultFile]) => {
                const suiteItem = document.createElement('li');
                suiteItem.className = 'suite-item';
                suiteItem.textContent = suiteName;
                suiteItem.dataset.db = dbName;
                suiteItem.dataset.suite = suiteName;
                
                suiteItem.addEventListener('click', () => {
                    // Remove active class from all items
                    document.querySelectorAll('.suite-item').forEach(item => {
                        item.classList.remove('active');
                    });
                    // Add active class to clicked item
                    suiteItem.classList.add('active');
                    // Load the selected test suite
                    loadTestSuite(dbName, suiteName);
                    // Update URL
                    updateURL(dbName, suiteName);
                });
                
                suiteList.appendChild(suiteItem);
            });
            
            dbGroup.appendChild(suiteList);
            navContent.appendChild(dbGroup);
        });
        
        // Check URL parameters for initial selection
        const params = new URLSearchParams(window.location.search);
        const db = params.get('db');
        const suite = params.get('suite');
        
        if (db && suite) {
            const suiteItem = document.querySelector(`.suite-item[data-db="${db}"][data-suite="${suite}"]`);
            if (suiteItem) {
                suiteItem.classList.add('active');
                loadTestSuite(db, suite);
            } else {
                // If URL parameters are invalid, load the first suite
                loadFirstSuite();
            }
        } else {
            // If no URL parameters, load the first suite
            loadFirstSuite();
        }
    } catch (error) {
        console.error('Error initializing navigation:', error);
        navContent.innerHTML = '<p>Error loading test structure</p>';
    }
}

// Load the first available test suite
function loadFirstSuite() {
    const firstDb = document.querySelector('.db-group');
    if (firstDb) {
        const firstSuite = firstDb.querySelector('.suite-item');
        if (firstSuite) {
            firstSuite.classList.add('active');
            loadTestSuite(firstSuite.dataset.db, firstSuite.dataset.suite);
            updateURL(firstSuite.dataset.db, firstSuite.dataset.suite);
        }
    }
}

// Update URL with current selections
function updateURL(db, suite) {
    const params = new URLSearchParams();
    params.set('db', db);
    params.set('suite', suite);
    const newUrl = window.location.pathname + '?' + params.toString();
    window.history.pushState({}, '', newUrl);
}

// Load test suite data
async function loadTestSuite(db, suite) {
    try {

        // find the suite in the testSuites object
        const suiteResults = testSuites[db][suite]; 

        const response = await fetch(`../src/test/resources/test-scenarios/${db}/${suiteResults}`);
        const data = await response.json();
        displayCharts(data);
    } catch (error) {
        console.error('Error loading test suite:', error);
        chartsContainer.innerHTML = '<p>Error loading test suite data</p>';
    }
}

// Format query parameters
function formatQueryParams(query) {
    const params = new URLSearchParams(query.split('?')[1]);
    let formatted = '';
    
    params.forEach((value, key) => {
        formatted += `<div class="query-param">
            <span class="param-key">${key}:</span>
            <span class="param-value">${value}</span>
        </div>`;
    });
    
    return formatted;
}

// Get version colors from data
function getVersionColors(data) {
    const versions = new Set();
    data.scenarios.forEach(scenario => {
        scenario.expectations.forEach(exp => versions.add(exp.release));
    });
    
    const versionColors = {};
    Array.from(versions).sort().forEach((version, i) => {
        versionColors[version] = colorPalette[i % colorPalette.length];
    });
    
    return versionColors;
}

// Display charts
function displayCharts(data) {
    chartsContainer.innerHTML = '';
    
    // Get version colors for this dataset
    const versionColors = getVersionColors(data);

    createVisualization(data, versionColors);
    
    // data.scenarios.forEach((scenario, index) => {
    //     const chartContainer = document.createElement('div');
    //     chartContainer.className = 'chart-container';
        
    //     // Add query information
    //     const queryInfo = document.createElement('div');
    //     queryInfo.className = 'query-info';
    //     queryInfo.innerHTML = `
    //         <div class="full-query">
    //             <span class="endpoint">${scenario.endpoint}</span>
    //         </div>
    //         ${formatQueryParams(scenario.query)}
    //     `;
    //     chartContainer.appendChild(queryInfo);
        
    //     // Add chart
    //     const chartDiv = document.createElement('div');
    //     chartDiv.className = 'chart';
    //     chartContainer.appendChild(chartDiv);
        
    //     chartsContainer.appendChild(chartContainer);
        
    //     // Create chart using D3
    //     createChart(chartDiv, scenario, versionColors);
    // });
}

// Handle browser back/forward navigation
window.addEventListener('popstate', () => {
    const params = new URLSearchParams(window.location.search);
    const db = params.get('db');
    const suite = params.get('suite');
    
    if (db && suite) {
        const suiteItem = document.querySelector(`.suite-item[data-db="${db}"][data-suite="${suite}"]`);
        if (suiteItem) {
            // Remove active class from all items
            document.querySelectorAll('.suite-item').forEach(item => {
                item.classList.remove('active');
            });
            // Add active class to selected item
            suiteItem.classList.add('active');
            // Load the test suite
            loadTestSuite(db, suite);
        }
    }
});

// Initialize the application
document.addEventListener('DOMContentLoaded', initializeNavigation); 