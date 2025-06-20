document.addEventListener('DOMContentLoaded', function() {
    'use strict';
    const tg = window.Telegram.WebApp;

    // --- Initialize Telegram Web App ---
    if (tg.initDataUnsafe?.user) {
        tg.expand();
        tg.setHeaderColor(tg.themeParams.secondary_bg_color || '#f0f0f0');
        tg.setBackgroundColor(tg.themeParams.secondary_bg_color || '#f0f0f0');
    } else {
        console.warn("Telegram WebApp user data not available. Some features might not work.");
    }
    tg.MainButton.setParams({
        text: 'CLOSE', 
        // color: '#3b82f6', 
        // text_color: '#ffffff',
    }).onClick(() => tg.close());
    tg.MainButton.show();


    // --- DOM Element Cache ---
    const elements = {
        loadingOverlay: document.getElementById('loading-overlay'),
        budgetMonthYearInput: document.getElementById('budget-month-year'),
        budgetAmountInput: document.getElementById('budget-amount'),
        saveMonthlyBudgetBtn: document.getElementById('save-monthly-budget-btn'),
        currentBudgetDisplay: document.getElementById('current-budget-display'),
    };

    // --- State Management ---
    let state = {
        apiBaseUrl: '/api/v1', 
        currentSelectedYear: null,
        currentSelectedMonth: null,
        // No API token needed if using cookie-based auth for Mini Apps or if endpoints are public within trusted context
        // If your API key is needed, you'd get it from initData or a launch param
    };

    // --- API Fetch Utility ---
    async function fetchApi(endpoint, options = {}) {
        setLoading(true);
        try {
            const headers = {
                'Content-Type': 'application/json',
                'X-API-Key': '1d3d5ea1d406e27b3586a7bb2e7f3d858223a61d1863c3fcdc03720085faae82', 
                ...options.headers,
            };
            const response = await fetch(`${state.apiBaseUrl}${endpoint}`, { ...options, headers });
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: response.statusText }));
                throw new Error(`API Error (${response.status}): ${errorData.detail || response.statusText}`);
            }
            return response.status === 204 ? null : response.json(); 
        } finally {
            setLoading(false);
        }
    }

    // --- UI Helpers ---
    function setLoading(isLoading) {
        if (elements.loadingOverlay) {
            elements.loadingOverlay.style.display = isLoading ? 'flex' : 'none';
        }
    }
    function showMessage(message, type = 'info') {
        tg.showAlert(message);
        if (type === 'error') console.error(message);
        else console.log(message);
    }


    // --- Budget Management Logic ---
    function setDefaultMonthYear() {
        const today = new Date();
        const year = today.getFullYear();
        const month = (today.getMonth() + 1).toString().padStart(2, '0')
        elements.budgetMonthYearInput.value = `${year}-${month}`;
        state.currentSelectedYear = year;
        state.currentSelectedMonth = parseInt(month, 10);
        fetchAndDisplayBudgetForSelectedMonth(); 
    }

    async function fetchAndDisplayBudgetForSelectedMonth() {
        if (!state.currentSelectedYear || !state.currentSelectedMonth) {
            elements.currentBudgetDisplay.textContent = "Please select a month and year.";
            return;
        }

        try {
            const budgetData = await fetchApi(`/budget/${state.currentSelectedYear}/${state.currentSelectedMonth}`);
            if (budgetData && typeof budgetData.budget_amount !== 'undefined') {
                elements.budgetAmountInput.value = budgetData.budget_amount;
                elements.currentBudgetDisplay.textContent = `Current budget for ${state.currentSelectedMonth}/${state.currentSelectedYear}: ₹${budgetData.budget_amount.toFixed(2)}`;
            } else {
                elements.budgetAmountInput.value = '';
                elements.currentBudgetDisplay.textContent = `No budget set for ${state.currentSelectedMonth}/${state.currentSelectedYear}.`;
            }
        } catch (error) {
            if (error.message.includes("404")) { 
                 elements.budgetAmountInput.value = '';
                 elements.currentBudgetDisplay.textContent = `No budget set for ${state.currentSelectedMonth}/${state.currentSelectedYear}.`;
            } else {
                showMessage(`Error fetching budget: ${error.message}`, 'error');
                elements.currentBudgetDisplay.textContent = "Error loading budget.";
            }
        }
    }

    async function handleSaveMonthlyBudget() {
        const monthYearValue = elements.budgetMonthYearInput.value;
        const amountValue = parseFloat(elements.budgetAmountInput.value);

        if (!monthYearValue) {
            showMessage("Please select a month and year.", 'error');
            return;
        }
        if (isNaN(amountValue) || amountValue <= 0) {
            showMessage("Please enter a valid positive budget amount.", 'error');
            return;
        }

        const [year, month] = monthYearValue.split('-').map(Number);

        try {
            await fetchApi('/budget/', {
                method: 'POST',
                body: JSON.stringify({ year, month, budget_amount: amountValue }),
            });
            showMessage(`Budget for ${month}/${year} saved successfully!`, 'success');
            state.currentSelectedYear = year;
            state.currentSelectedMonth = month;
            fetchAndDisplayBudgetForSelectedMonth(); 
        } catch (error) {
            showMessage(`Error saving budget: ${error.message}`, 'error');
        }
    }

    // --- Event Listeners ---
    function setupEventListeners() {
        if (elements.budgetMonthYearInput) {
            elements.budgetMonthYearInput.addEventListener('change', (event) => {
                const [year, month] = event.target.value.split('-').map(Number);
                state.currentSelectedYear = year;
                state.currentSelectedMonth = month;
                fetchAndDisplayBudgetForSelectedMonth();
            });
        }

        if (elements.saveMonthlyBudgetBtn) {
            elements.saveMonthlyBudgetBtn.addEventListener('click', handleSaveMonthlyBudget);
        }
    }

    // --- Main Initialization ---
    function initialize() {
        if (elements.budgetMonthYearInput) {
            setDefaultMonthYear();
        }
        setupEventListeners();
        feather.replace(); 
        tg.ready(); 
    }

    initialize();
});