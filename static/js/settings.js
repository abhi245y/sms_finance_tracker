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

        // Account Settings elements
        accountsListContainer: document.getElementById('accounts-list-container'),
        // New: Subcategory Settings elements
        categoriesAccordionContainer: document.getElementById('categories-accordion-container'),
    };

    // --- State Management ---
    let state = {
        apiBaseUrl: '/api/v1', 
        currentSelectedYear: null,
        currentSelectedMonth: null,
        allAccounts: [],

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

    function getBankIconClass(bankName, accountType) {
        if (accountType === 'CASH') return 'bank-icon-cash';
        const name = bankName?.toLowerCase() || '';
        if (name.includes('hdfc') && name.includes('dinner club')) return 'brand/diners-club.svg';
        if (name.includes('hdfc')) return 'brand/hdfc.svg';
        if (name.includes('icici') && name.includes('amazon')) return 'brand/amazon-icici-cc.svg';
        if (name.includes('icici')) return 'brand/icici.svg';
        if (name.includes('sbi') && name.includes('cashback')) return 'brand/sbi-cashback.svg';
        if (name.includes('sbi')) return 'brand/sbi.svg';
        if (name.includes('idfc')) return 'brand/idfc.svg';
        if (name.includes('federal') && name.includes('jupiter')) return 'brand/jupiter-fed.svg';
        if (name.includes('federal') && name.includes('fi')) return 'brand/fi.svg';
        if (name.includes('federal')) return 'brand/federal-bank-savings.svg';
        if (name.includes('amex') || name.includes('american express')) return 'brand/amex.svg';
        return 'bank-icon-default';
    }

    function createIconHTML(iconString) { 
        if (!iconString) return `<i data-feather="circle"></i>`;
        if (iconString.startsWith('fthr:')) return `<i data-feather="${iconString.substring(5)}"></i>`;
        if (iconString.startsWith('img:')) return `<img src="/static/images/icons/${iconString.substring(4)}" class="custom-icon" alt="icon">`;
        if (iconString.startsWith('emoji:')) return `<span class="emoji-icon">${iconString.substring(6)}</span>`;
        return `<i data-feather="tag"></i>`;
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

    // --- Account Purpose Management Logic ---
    async function fetchAndDisplayAccounts() {
        if (!elements.accountsListContainer) return;
        setLoading(true);
        try {
            const accountsData = await fetchApi('/accounts/for-mini-app');
            state.allAccounts = accountsData || [];
            renderAccountsList();
        } catch (error) {
            showMessage(`Error fetching accounts: ${error.message}`, 'error');
        } finally {
            setLoading(false);
        }
    }

    function renderAccountsList() {
        if (!elements.accountsListContainer) return;
        elements.accountsListContainer.innerHTML = ''; 

        if (state.allAccounts.length === 0) {
            elements.accountsListContainer.innerHTML = '<p>No accounts found.</p>';
            return;
        }

        state.allAccounts.forEach(account => {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'account-list-item';
            itemDiv.dataset.accountId = account.id;

            const iconName = getBankIconClass(account.name, account.account_type); 
            const iconHTML = `<img class="custom-icon" src="/static/images/icons/${iconName}" alt="...">`;

            itemDiv.innerHTML = `
                <div class="account-info">
                    <div class="account-item-icon">${iconHTML}</div> 
                    <div class="account-name-details">
                        <span class="account-name-settings">${account.name}</span>
                        <span class="account-meta-settings">${account.account_type.replace('_', ' ')} ***${account.account_last4}</span>
                    </div>
                </div>
                <div class="three-state-toggle account-purpose-toggle-style" data-account-id="${account.id}">
                    <button class="toggle-segment ${account.purpose === 'personal' ? 'active-text' : ''}" data-value="personal" data-index="0">Personal</button>
                    <button class="toggle-segment ${account.purpose === 'business' ? 'active-text' : ''}" data-value="business" data-index="1">Business</button>
                </div>
            `;
            elements.accountsListContainer.appendChild(itemDiv);

            const toggleElement = itemDiv.querySelector('.three-state-toggle');
            const activeIndex = account.purpose === 'business' ? 1 : 0;
            const segmentWidth = (140 - 4) / 2;
            const transformValue = `translateX(${activeIndex * segmentWidth}px)`;
            toggleElement.style.setProperty('--slider-transform', transformValue);
        });
        feather.replace(); 
    }

    async function handleAccountPurposeChange(accountId, newPurpose) {
        setLoading(true);
        try {
            await fetchApi(`/accounts/${accountId}`, {
                method: 'PATCH',
                body: JSON.stringify({ purpose: newPurpose }),
            });
            const accountInState = state.allAccounts.find(acc => acc.id === accountId);
            if (accountInState) {
                accountInState.purpose = newPurpose;
            }
            const toggleContainer = elements.accountsListContainer.querySelector(`[data-account-id="${accountId}"]`);
            if (toggleContainer) {
                const toggleElement = toggleContainer.querySelector('.three-state-toggle');
            
                toggleElement.querySelectorAll('.toggle-segment').forEach(segment => {
                    segment.classList.toggle('active-text', segment.dataset.value === newPurpose);
                });
            
                const activeIndex = newPurpose === 'business' ? 1 : 0;
                const segmentWidth = (140 - 4) / 2;
                const transformValue = `translateX(${activeIndex * segmentWidth}px)`;
                toggleElement.style.setProperty('--slider-transform', transformValue);
            }
        } catch (error) {
            showMessage(`Error updating account purpose: ${error.message}`, 'error');
        } finally {
            setLoading(false);
        }
    }

    // --- Subcategory Rule Management Logic ---
    async function fetchAndDisplayCategoriesAndSubcategories() {
        if (!elements.categoriesAccordionContainer) return;
        setLoading(true);
        try {
            const categoriesData = await fetchApi('/categories/all_details');
            state.allCategoriesWithSubcategories = categoriesData || [];
            renderCategoriesAccordion();
        } catch (error) {
            showMessage(`Error fetching categories: ${error.message}`, 'error');
        } finally {
            setLoading(false);
        }
    }

    function renderCategoriesAccordion() {
        if (!elements.categoriesAccordionContainer) return;
        elements.categoriesAccordionContainer.innerHTML = ''; 

        if (state.allCategoriesWithSubcategories.length === 0) {
            elements.categoriesAccordionContainer.innerHTML = '<p>No categories found.</p>';
            return;
        }

        state.allCategoriesWithSubcategories.forEach(category => {
            const categoryGroupDiv = document.createElement('div');
            categoryGroupDiv.className = 'category-group-settings';
            categoryGroupDiv.dataset.categoryId = category.id;

            const headerDiv = document.createElement('div');
            headerDiv.className = 'category-header-settings';
            headerDiv.innerHTML = `
                <span class="category-title-settings">${category.name}</span>
                <i data-feather="chevron-right" class="category-chevron"></i>
            `;

            const subcategoriesListDiv = document.createElement('div');
            subcategoriesListDiv.className = 'subcategories-list-settings';

            if (category.subcategories && category.subcategories.length > 0) {
                category.subcategories.forEach(sub => {
                    const subItemDiv = document.createElement('div');
                    subItemDiv.className = 'subcategory-item-settings';
                    subItemDiv.dataset.subcategoryId = sub.id;

                    subItemDiv.innerHTML = `
                        <div class="subcategory-info-settings">
                            <div class="subcategory-icon-settings">${createIconHTML(sub.icon_name)}</div>
                            <span class="subcategory-name-settings">${sub.name}</span>
                        </div>
                        <div class="subcategory-toggles-container">
                            <div class="subcategory-toggle-item">
                                <span class="subcategory-toggle-label">Reimbursable</span>
                                <label class="switch">
                                    <input type="checkbox" class="subcategory-flag-toggle" data-flag="is_reimbursable" ${sub.is_reimbursable ? 'checked' : ''}>
                                    <span class="slider"></span>
                                </label>
                            </div>
                            <div class="subcategory-toggle-item">
                                <span class="subcategory-toggle-label">Exclude from Budget</span>
                                <label class="switch">
                                    <input type="checkbox" class="subcategory-flag-toggle" data-flag="exclude_from_budget" ${sub.exclude_from_budget ? 'checked' : ''}>
                                    <span class="slider"></span>
                                </label>
                            </div>
                        </div>
                    `;
                    subcategoriesListDiv.appendChild(subItemDiv);
                });
            } else {
                subcategoriesListDiv.innerHTML = '<p style="padding: 10px 0; color: var(--tg-theme-hint-color);">No subcategories.</p>';
            }

            categoryGroupDiv.appendChild(headerDiv);
            categoryGroupDiv.appendChild(subcategoriesListDiv);
            elements.categoriesAccordionContainer.appendChild(categoryGroupDiv);
        });
        feather.replace();
    }

    async function handleSubcategoryFlagChange(subcategoryId, flagName, newValue) {
        setLoading(true);
        const patchData = {};
        patchData[flagName] = newValue; 

        try {
            await fetchApi(`/categories/subcategories/${subcategoryId}`, {
                method: 'PATCH',
                body: JSON.stringify(patchData),
            });
            showMessage(`Subcategory ${flagName.replace('_', ' ')} updated.`, 'success');
            // Update local state
            const parentCategory = state.allCategoriesWithSubcategories.find(cat => 
                cat.subcategories.some(sub => sub.id === subcategoryId)
            );
            if (parentCategory) {
                const subcategoryInState = parentCategory.subcategories.find(sub => sub.id === subcategoryId);
                if (subcategoryInState) {
                    subcategoryInState[flagName] = newValue;
                }
            }
        } catch (error) {
            showMessage(`Error updating subcategory: ${error.message}`, 'error');
            // Revert UI toggle if API call fails (optional, but good UX)
            // This would require finding the checkbox and setting its 'checked' property back.
            // For now, we'll rely on a page refresh or re-fetch to correct inconsistencies.
        } finally {
            setLoading(false);
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

        // Event listener for account purpose toggles (using event delegation)
        if (elements.accountsListContainer) {
            elements.accountsListContainer.addEventListener('click', (event) => {
                const segmentButton = event.target.closest('.toggle-segment');
                if (segmentButton && segmentButton.parentElement.classList.contains('three-state-toggle')) {
                    const accountId = parseInt(segmentButton.parentElement.dataset.accountId, 10);
                    const newPurpose = segmentButton.dataset.value;
                    
                    const accountInState = state.allAccounts.find(acc => acc.id === accountId);
                    if (accountInState && accountInState.purpose !== newPurpose) {
                        handleAccountPurposeChange(accountId, newPurpose);
                    }
                }
            });
        }

        //  Event listeners for category accordion and subcategory toggles
        if (elements.categoriesAccordionContainer) {
            elements.categoriesAccordionContainer.addEventListener('click', (event) => {
                const header = event.target.closest('.category-header-settings');
                if (header) {
                    header.classList.toggle('expanded');
                    const sublist = header.nextElementSibling;
                    if (sublist && sublist.classList.contains('subcategories-list-settings')) {
                        sublist.style.display = header.classList.contains('expanded') ? 'block' : 'none';
                    }
                    feather.replace(); 
                    return; 
                }

                const toggleInput = event.target.closest('.subcategory-flag-toggle');
                if (toggleInput) {
                    const subcategoryId = parseInt(toggleInput.closest('.subcategory-item-settings').dataset.subcategoryId, 10);
                    const flagName = toggleInput.dataset.flag;
                    const newValue = toggleInput.checked;
                    handleSubcategoryFlagChange(subcategoryId, flagName, newValue);
                }
            });
        }
    }

    // --- Main Initialization ---
    function initialize() {
        if (elements.budgetMonthYearInput) {
            setDefaultMonthYear();
        }
        fetchAndDisplayAccounts(); 
        fetchAndDisplayCategoriesAndSubcategories(); 
        setupEventListeners();
        feather.replace(); 
        tg.ready(); 
    }

    initialize();
});