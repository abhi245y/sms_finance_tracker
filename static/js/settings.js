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

	let categoryCreationState = {
		allExistingCategories: [],
		selectedIconType: 'feather',
		selectedIconValue: null,
		uploadedSvgContent: null,
		isCreatingNewCategory: false
	};

	// Emoji categories
	const EMOJI_CATEGORIES = {
		food: ['🍕', '🍔', '🍟', '🌭', '🍿', '🧂', '🥓', '🥞', '🧇', '🥯', '🍞', '🥐', '🥨', '🧀', '🥚', '🍳', '🧈', '🥞', '🥪', '🌮', '🌯', '🥙', '🧆', '🥗', '🍲', '🍛', '🍜', '🍝', '🍠', '🍢', '🍣', '🍤', '🍙', '🍘', '🍱', '🍚'],
		transport: ['🚗', '🚕', '🚙', '🚌', '🚎', '🏎️', '🚓', '🚑', '🚒', '🚐', '🛻', '🚚', '🚛', '🚜', '🏍️', '🛵', '🚲', '🛴', '🛹', '🛼', '🚁', '✈️', '🛩️', '🛫', '🛬', '🪂', '💺', '🚀', '🛸', '🚊', '🚝', '🚞', '🚋', '🚃', '🚈', '🚂', '🚆', '🚄', '🚅', '🚈'],
		activities: ['⚽', '🏀', '🏈', '⚾', '🥎', '🎾', '🏐', '🏉', '🥏', '🎱', '🪀', '🏓', '🏸', '🏒', '🏑', '🥍', '🏏', '🪃', '🥅', '⛳', '🪁', '🏹', '🎣', '🤿', '🥊', '🥋', '🎽', '🛹', '🛷', '⛸️', '🥌', '🎿', '⛷️', '🏂', '🪂', '🏋️', '🤸', '🤾', '🏌️', '🏇', '🧘', '🏃', '🚴', '🤽', '🏊'],
		objects: ['💡', '🔦', '🕯️', '🪔', '🧯', '🛢️', '💸', '💳', '💎', '⚖️', '🪜', '🧰', '🪛', '🔧', '🔨', '⚒️', '🛠️', '⛏️', '🪚', '🔩', '⚙️', '🪤', '🧱', '⛓️', '🧲', '🔫', '💣', '🧨', '🪓', '🔪', '🗡️', '⚔️', '🛡️', '🚬', '⚰️', '🪦', '⚱️', '🏺', '🔮', '📿', '🧿', '💈', '⚗️', '🔭', '🔬', '🕳️', '🩹', '🩺', '💊', '💉', '🧬', '🦠', '🧪', '🌡️', '🧹', '🪣', '🧽', '🧴', '🛎️', '🔑', '🗝️', '🚪', '🪑', '🛏️', '🛋️', '🪞', '🚿', '🛁', '🚽', '🪠', '🧻', '🪒', '🧼', '🪥', '🧴', '🧷', '🧹', '🧺', '🧸', '🪆', '🖼️', '🪬', '🪩', '🪬'],
		symbols: ['💰', '💴', '💵', '💶', '💷', '🪙', '💳', '💎', '⚖️', '💼', '📊', '📈', '📉', '💹', '💱', '💲', '🏦', '🏧', '🪪', '📋', '📌', '📍', '📎', '🖇️', '📏', '📐', '✂️', '🗃️', '🗂️', '🗞️', '📰', '📄', '📃', '📑', '📊', '📈', '📉', '🗒️', '🗓️', '📅', '📆', '🗑️', '📇', '🗃️', '🗂️', '🗞️', '🔖', '🏷️', '💼', '📁', '📂', '🗂️', '📋']
	};

	const categoryCreationElements = {
		modal: null,
		openBtn: null,
		closeBtn: null,
		saveBtn: null,

		categoryNameInput: null,
		categoryDescriptionInput: null,
		subcategoryNameInput: null,
		categoryDropdown: null,

		customEmojiInput: null,
		emojiAddBtn: null,

		iconPreview: null,
		iconPreviewLabel: null,
		iconTypeTabs: null,
		iconPanels: null,

		featherSearchInput: null,
		featherGrid: null,

		emojiCategoryBtns: null,
		emojiGrid: null,

		uploadArea: null,
		svgFileInput: null,

		isReimbursableCheckbox: null,
		excludeFromBudgetCheckbox: null
	};

    function getAllFeatherIcons() {
    // Popular icons to show first
    const popularIcons = [
        'shopping-bag', 'coffee', 'car', 'home', 'phone', 'credit-card', 'dollar-sign',
        'gift', 'heart', 'music', 'camera', 'book', 'briefcase', 'calendar',
        'umbrella', 'airplane', 'bicycle', 'bus', 'train', 'truck',
        'pizza', 'wine', 'cup', 'utensils', 'apple', 'sandwich',
        'gamepad', 'tv', 'headphones', 'smartphone', 'laptop', 'monitor',
        'pill', 'thermometer', 'activity', 'dumbbell', 'zap', 'sun',
        'moon', 'cloud', 'droplet', 'wind', 'fire', 'leaf',
        'star', 'flag', 'lock', 'key', 'shield', 'tool'
    ];
    
    // Get all feather icons from the loaded library
    const allIcons = window.feather ? Object.keys(window.feather.icons) : popularIcons;
    
    // Sort: popular first, then alphabetically
    const popularSet = new Set(popularIcons);
    const popular = allIcons.filter(icon => popularSet.has(icon));
    const others = allIcons.filter(icon => !popularSet.has(icon)).sort();
    
    return [...popular, ...others];
}


	// --- API Fetch Utility ---
	async function fetchApi(endpoint, options = {}) {
		setLoading(true);
		try {
			const headers = {
				'Content-Type': 'application/json',
				'X-API-Key': '1d3d5ea1d406e27b3586a7bb2e7f3d858223a61d1863c3fcdc03720085faae82',
				...options.headers,
			};
			const response = await fetch(`${state.apiBaseUrl}${endpoint}`, {
				...options,
				headers
			});
			if (!response.ok) {
				const errorData = await response.json().catch(() => ({
					detail: response.statusText
				}));
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
		return 'brand/bank-icon-default';
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
				body: JSON.stringify({
					year,
					month,
					budget_amount: amountValue
				}),
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
				body: JSON.stringify({
					purpose: newPurpose
				}),
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

	// === Initialize Category Creation Modal ===
	function initializeCategoryCreationModal() {
    // Cache DOM elements
    categoryCreationElements.modal = document.getElementById('categoryCreationModal');
    categoryCreationElements.openBtn = document.getElementById('create-category-subcategory-btn');
    categoryCreationElements.closeBtn = document.getElementById('closeCategoryCreationModalBtn');
    categoryCreationElements.saveBtn = document.getElementById('saveCategoryCreationBtn');
    
    categoryCreationElements.categoryNameInput = document.getElementById('category-name-input');
    categoryCreationElements.categoryDescriptionInput = document.getElementById('category-description-input');
    categoryCreationElements.subcategoryNameInput = document.getElementById('subcategory-name-input');
    categoryCreationElements.categoryDropdown = document.getElementById('category-dropdown');
    
    categoryCreationElements.iconPreview = document.getElementById('icon-preview');
    categoryCreationElements.iconPreviewLabel = document.getElementById('icon-preview-label');
    
    categoryCreationElements.featherSearchInput = document.getElementById('feather-search');
    categoryCreationElements.featherGrid = document.getElementById('feather-icon-grid');
    categoryCreationElements.emojiGrid = document.getElementById('emoji-grid');
    categoryCreationElements.customEmojiInput = document.getElementById('custom-emoji-input');
    categoryCreationElements.emojiAddBtn = document.getElementById('emoji-add-btn');
    
    categoryCreationElements.uploadArea = document.getElementById('upload-area');
    categoryCreationElements.svgFileInput = document.getElementById('svg-file-input');
    
    categoryCreationElements.isReimbursableCheckbox = document.getElementById('is-reimbursable-checkbox');
    categoryCreationElements.excludeFromBudgetCheckbox = document.getElementById('exclude-from-budget-checkbox');

    if (!categoryCreationElements.modal) return;

    // Setup event listeners
    setupCategoryCreationEventListeners();
    
    // Initialize UI components
    populateFeatherIconsGrid();
    populateEmojiGrid('food'); // Default category
    
    // Load existing categories
    loadExistingCategories();
	
    }
function setupCategoryCreationEventListeners() {
    // Modal open/close
    categoryCreationElements.openBtn?.addEventListener('click', openCategoryCreationModal);
    categoryCreationElements.closeBtn?.addEventListener('click', closeCategoryCreationModal);
    categoryCreationElements.saveBtn?.addEventListener('click', handleSaveCategoryCreation);
    
    // Close on backdrop click
    categoryCreationElements.modal?.addEventListener('click', (e) => {
        if (e.target === categoryCreationElements.modal) {
            closeCategoryCreationModal();
        }
    });
    
    // Category input and dropdown
    categoryCreationElements.categoryNameInput?.addEventListener('input', handleCategoryNameInput);
    categoryCreationElements.categoryNameInput?.addEventListener('focus', showCategoryDropdown);
    categoryCreationElements.categoryNameInput?.addEventListener('blur', () => {
        // Delay hiding to allow dropdown clicks
        setTimeout(hideCategoryDropdown, 150);
    });
    
    // Icon type tabs
    document.querySelectorAll('.icon-type-tab').forEach(tab => {
        tab.addEventListener('click', () => switchIconTab(tab.dataset.tab));
    });
    
    // Feather icon search
    categoryCreationElements.featherSearchInput?.addEventListener('input', handleFeatherIconSearch);
    
    // Emoji category buttons
    document.querySelectorAll('.emoji-category-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.emoji-category-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            populateEmojiGrid(btn.dataset.category);
        });
    });
    
    // Custom emoji input
    categoryCreationElements.customEmojiInput?.addEventListener('input', handleCustomEmojiInput);
    categoryCreationElements.customEmojiInput?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {	
            handleAddCustomEmoji();
        }
    });
    categoryCreationElements.emojiAddBtn?.addEventListener('click', handleAddCustomEmoji);
    
    // Upload area
    setupUploadArea();
}

// === Modal Management ===
function openCategoryCreationModal() {
    categoryCreationElements.modal.style.display = 'flex';
    resetCategoryCreationForm();
    feather.replace(); // Re-render feather icons
}

function closeCategoryCreationModal() {
    categoryCreationElements.modal.style.display = 'none';
    resetCategoryCreationForm();
}

function resetCategoryCreationForm() {
    // Reset form inputs
    categoryCreationElements.categoryNameInput.value = '';
    categoryCreationElements.categoryDescriptionInput.value = '';
    categoryCreationElements.categoryDescriptionInput.disabled = true;
    categoryCreationElements.subcategoryNameInput.value = '';
    
    // Reset icon selection
    categoryCreationState.selectedIconType = 'feather';
    categoryCreationState.selectedIconValue = null;
    categoryCreationState.uploadedSvgContent = null;
    
    updateIconPreview(null, 'No icon selected');
    switchIconTab('feather');
    
    // Reset checkboxes
    categoryCreationElements.isReimbursableCheckbox.checked = false;
    categoryCreationElements.excludeFromBudgetCheckbox.checked = false;
    
    // Reset state
    categoryCreationState.isCreatingNewCategory = false;
    hideCategoryDropdown();
}

// === Category Dropdown ===
async function loadExistingCategories() {
    try {
        const categories = await fetchApi('/categories/all_details');
        categoryCreationState.allExistingCategories = categories || [];
    } catch (error) {
        console.error('Failed to load existing categories:', error);
        categoryCreationState.allExistingCategories = [];
    }
}

function handleCategoryNameInput(e) {
    const value = e.target.value.trim();
    const isExisting = categoryCreationState.allExistingCategories.some(
        cat => cat.name.toLowerCase() === value.toLowerCase()
    );
    
    categoryCreationState.isCreatingNewCategory = !isExisting && value.length > 0;
    
    // Enable/disable description input
    categoryCreationElements.categoryDescriptionInput.disabled = !categoryCreationState.isCreatingNewCategory;
    if (!categoryCreationState.isCreatingNewCategory) {
        categoryCreationElements.categoryDescriptionInput.value = '';
    }
    
    // Update dropdown
    updateCategoryDropdown(value);
}

function updateCategoryDropdown(searchValue) {
    const dropdown = categoryCreationElements.categoryDropdown;
    dropdown.innerHTML = '';
    
    if (!searchValue) {
        hideCategoryDropdown();
        return;
    }
    
    // Filter existing categories
    const matches = categoryCreationState.allExistingCategories.filter(cat =>
        cat.name.toLowerCase().includes(searchValue.toLowerCase())
    );
    
    // Add existing category matches
    matches.forEach(category => {
        const item = document.createElement('div');
        item.className = 'category-dropdown-item';
        item.innerHTML = `
            <span>${category.name}</span>
            <span style="font-size: 12px; color: #6b7280;">${category.subcategories?.length || 0} subcategories</span>
        `;
        item.addEventListener('click', () => selectExistingCategory(category));
        dropdown.appendChild(item);
    });
    
    // Add "Create New" option if no exact match
    const exactMatch = categoryCreationState.allExistingCategories.some(
        cat => cat.name.toLowerCase() === searchValue.toLowerCase()
    );
    
    if (!exactMatch && searchValue.length > 1) {
        const createItem = document.createElement('div');
        createItem.className = 'category-dropdown-item create-new';
        createItem.innerHTML = `
            <span>Create "${searchValue}"</span>
            <i data-feather="plus" style="width: 14px; height: 14px;"></i>
        `;
        createItem.addEventListener('click', () => selectNewCategory(searchValue));
        dropdown.appendChild(createItem);
    }
    
    showCategoryDropdown();
    feather.replace();
}

function selectExistingCategory(category) {
    categoryCreationElements.categoryNameInput.value = category.name;
    categoryCreationState.isCreatingNewCategory = false;
    categoryCreationElements.categoryDescriptionInput.disabled = true;
    categoryCreationElements.categoryDescriptionInput.value = '';
    hideCategoryDropdown();
}

function selectNewCategory(name) {
    categoryCreationElements.categoryNameInput.value = name;
    categoryCreationState.isCreatingNewCategory = true;
    categoryCreationElements.categoryDescriptionInput.disabled = false;
    categoryCreationElements.categoryDescriptionInput.focus();
    hideCategoryDropdown();
}

function showCategoryDropdown() {
    categoryCreationElements.categoryDropdown.classList.add('active');
}

function hideCategoryDropdown() {
    categoryCreationElements.categoryDropdown.classList.remove('active');
}

// === Icon Selection ===
function switchIconTab(tabType) {
    // Update tabs
    document.querySelectorAll('.icon-type-tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.tab === tabType);
    });
    
    // Update panels
    document.querySelectorAll('.icon-panel').forEach(panel => {
        panel.classList.toggle('active', panel.id === `${tabType}-panel`);
    });
    
    categoryCreationState.selectedIconType = tabType;
    feather.replace();
}

function populateFeatherIconsGrid(searchTerm = '') {
    const grid = categoryCreationElements.featherGrid;
    if (!grid) return;
    
    const allIcons = getAllFeatherIcons();
    const filteredIcons = searchTerm 
        ? allIcons.filter(icon => icon.toLowerCase().includes(searchTerm.toLowerCase()))
        : allIcons;
    
    grid.innerHTML = '';
    
    // Add total count info
    if (searchTerm) {
        const countDiv = document.createElement('div');
        countDiv.className = 'icon-count-info';
        countDiv.innerHTML = `<span style="font-size: 12px; color: #6b7280; margin-bottom: 8px; display: block;">${filteredIcons.length} icons found</span>`;
        grid.appendChild(countDiv);
    }
    
    filteredIcons.forEach(iconName => {
        const item = document.createElement('div');
        item.className = 'icon-item';
        item.dataset.iconValue = iconName;
        item.title = iconName; // Tooltip with icon name
        item.innerHTML = `<i data-feather="${iconName}"></i>`;
        item.addEventListener('click', () => selectFeatherIcon(iconName, item));
        grid.appendChild(item);
    });
    
    feather.replace();
}

function handleFeatherIconSearch(e) {
    const searchTerm = e.target.value;
    populateFeatherIconsGrid(searchTerm);
}

function handleCustomEmojiInput(e) {
    const value = e.target.value.trim();
    const addBtn = categoryCreationElements.emojiAddBtn;
    
    // Enable/disable add button based on input
    if (addBtn) {
        addBtn.disabled = !isValidEmoji(value);
    }
}


function isValidEmoji(text) {
    if (!text || text.length === 0) return false;
    
    // Basic emoji validation - check if it contains emoji characters
    // This is a simple check, you could make it more sophisticated
    const emojiRegex = /[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/u;
    return emojiRegex.test(text) && text.length <= 10;
}

function handleAddCustomEmoji() {
    const input = categoryCreationElements.customEmojiInput;
    const value = input.value.trim();
    
    if (!isValidEmoji(value)) {
        showMessage('Please enter a valid emoji', 'error');
        return;
    }
    
    // Select the custom emoji
    selectCustomEmoji(value);
    
    // Clear input
    input.value = '';
    categoryCreationElements.emojiAddBtn.disabled = true;
    
    showMessage('Custom emoji selected!', 'success');
}

function selectCustomEmoji(emoji) {
    // Clear existing selections
    document.querySelectorAll('#emoji-grid .emoji-item').forEach(item => {
        item.classList.remove('selected');
    });
    
    // Update state and preview
    categoryCreationState.selectedIconValue = emoji;
    updateIconPreview(`<span class="emoji-icon">${emoji}</span>`, emoji);
}



function selectFeatherIcon(iconName, element) {
    // Update selection UI
    document.querySelectorAll('#feather-icon-grid .icon-item').forEach(item => {
        item.classList.remove('selected');
    });
    element.classList.add('selected');
    
    // Update state and preview
    categoryCreationState.selectedIconValue = iconName;
    updateIconPreview(`<i data-feather="${iconName}"></i>`, iconName);
}

function populateEmojiGrid(category) {
    const grid = categoryCreationElements.emojiGrid;
    if (!grid || !EMOJI_CATEGORIES[category]) return;
    
    grid.innerHTML = '';
    EMOJI_CATEGORIES[category].forEach(emoji => {
        const item = document.createElement('div');
        item.className = 'emoji-item';
        item.dataset.iconValue = emoji;
        item.textContent = emoji;
        item.addEventListener('click', () => selectEmoji(emoji, item));
        grid.appendChild(item);
    });
}

function selectEmoji(emoji, element) {
    // Update selection UI
    document.querySelectorAll('#emoji-grid .emoji-item').forEach(item => {
        item.classList.remove('selected');
    });
    element.classList.add('selected');
    
    // Update state and preview
    categoryCreationState.selectedIconValue = emoji;
    updateIconPreview(`<span class="emoji-icon">${emoji}</span>`, emoji);
}

function updateIconPreview(iconHtml, label) {
    if (iconHtml) {
        categoryCreationElements.iconPreview.outerHTML = iconHtml.includes('data-feather') 
            ? iconHtml.replace('>', ' id="icon-preview">') 
            : `<div id="icon-preview">${iconHtml}</div>`;
        categoryCreationElements.iconPreview = document.getElementById('icon-preview');
    } else {
        categoryCreationElements.iconPreview.outerHTML = '<i data-feather="circle" id="icon-preview"></i>';
        categoryCreationElements.iconPreview = document.getElementById('icon-preview');
    }
    
    categoryCreationElements.iconPreviewLabel.textContent = label;
    feather.replace();
}

// === File Upload ===
function setupUploadArea() {
    const uploadArea = categoryCreationElements.uploadArea;
    const fileInput = categoryCreationElements.svgFileInput;
    
    if (!uploadArea || !fileInput) return;
    
    // Click to upload
    uploadArea.addEventListener('click', () => fileInput.click());
    
    // File input change
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFileUpload(file);
    }
}

function handleFileUpload(file) {
    // Validate file
    if (!file.type.includes('svg') && !file.name.endsWith('.svg')) {
        showMessage('Please select an SVG file only.', 'error');
        return;
    }
    
    if (file.size > 100 * 1024) { // 100KB limit
        showMessage('File size must be under 100KB.', 'error');
        return;
    }
    
    // Read file
    const reader = new FileReader();
    reader.onload = (e) => {
        const svgContent = e.target.result;
        categoryCreationState.uploadedSvgContent = svgContent;
        categoryCreationState.selectedIconValue = svgContent;
        
        // Update preview (simplified for now)
        updateIconPreview(`<div style="width: 24px; height: 24px; background: #e5e7eb; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 10px;">SVG</div>`, file.name);
        
        showMessage('SVG file uploaded successfully!', 'success');
    };
    
    reader.onerror = () => {
        showMessage('Failed to read the SVG file.', 'error');
    };
    
    reader.readAsText(file);
}

// === Save Category Creation ===
async function handleSaveCategoryCreation() {
    try {
        // Validate form
        const categoryName = categoryCreationElements.categoryNameInput.value.trim();
        const subcategoryName = categoryCreationElements.subcategoryNameInput.value.trim();
        
        if (!categoryName) {
            showMessage('Please enter a category name.', 'error');
            return;
        }
        
        if (!subcategoryName) {
            showMessage('Please enter a subcategory name.', 'error');
            return;
        }
        
        if (!categoryCreationState.selectedIconValue) {
            showMessage('Please select an icon for the subcategory.', 'error');
            return;
        }
        
        setLoading(true);
        
        // Prepare API payload
        const payload = {
            category_name: categoryName,
            category_description: categoryCreationState.isCreatingNewCategory 
                ? categoryCreationElements.categoryDescriptionInput.value.trim() || `Custom category: ${categoryName}`
                : undefined,
            subcategory_name: subcategoryName,
            subcategory_icon_type: categoryCreationState.selectedIconType,
            subcategory_icon_value: categoryCreationState.selectedIconValue,
            is_reimbursable: categoryCreationElements.isReimbursableCheckbox.checked,
            exclude_from_budget: categoryCreationElements.excludeFromBudgetCheckbox.checked
        };
        
        // Make API call
        const response = await fetchApi('/categories/create-with-subcategory', {
            method: 'POST',
            body: JSON.stringify(payload),
        });
        
        // Success feedback
        const message = categoryCreationState.isCreatingNewCategory 
            ? `Created new category "${response.category.name}" with subcategory "${response.subcategory.name}"`
            : `Added subcategory "${response.subcategory.name}" to "${response.category.name}"`;
        
        showMessage(message, 'success');
        
        // Close modal and refresh data
        closeCategoryCreationModal();
        loadExistingCategories(); // Refresh for next time
        
        // Optionally refresh the subcategory rules section
        if (typeof fetchAndDisplayCategoriesAndSubcategories === 'function') {
            await fetchAndDisplayCategoriesAndSubcategories();
        }
        
    } catch (error) {
		alert(`Error creating category/subcategory: ${error.message}`)
        showMessage(`Error creating category/subcategory: ${error.message}`, 'error');
    } finally {
        setLoading(false);
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
		initializeCategoryCreationModal();
		feather.replace();
		tg.ready();
	}

	initialize();
});