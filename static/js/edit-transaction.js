document.addEventListener('DOMContentLoaded', function() {
    'use strict';
    const tg = window.Telegram.WebApp;
    // --- Initialize Telegram Web App ---
    if (tg.initDataUnsafe?.user) {
        tg.expand();
        tg.setHeaderColor('#f8f9fa');
        tg.setBackgroundColor('#f8f9fa');
    }

    // --- DOM Element Cache ---
    const elements = {
        loadingOverlay: document.getElementById('loading-overlay'),
        // Main page elements
        transactionAmount: document.getElementById('transaction-amount'),
        mainCategoryIconWrapper: document.getElementById('main-category-icon-wrapper'),
        mainCategoryName: document.getElementById('main-category-name'),
        fromAccountIcon: document.getElementById('from-account-icon-initial'),
        fromAccountDetails: document.getElementById('from-account-details'),
        transactionDate: document.getElementById('transaction-date'),
        paidToMerchantName: document.getElementById('paid-to-merchant-name'),
        descriptionTextarea: document.getElementById('description'),
        categoryBadge: document.getElementById('category-badge-main'),
        fromAccountAction: document.getElementById('from-account-action'),
        moreDetailsAction: document.getElementById('more-details-action'),

        linkTransactionAction: document.getElementById('link-transaction-action'),
        linkedTransactionInfo: document.getElementById('linked-transaction-info'),

        // New: Reimbursable Override elements (main page)
        reimbursableOverrideCard: document.getElementById('reimbursable-override-card'), 
        reimbursableToggle: document.getElementById('reimbursable-toggle'), 

        // Modals
        moreDetailsModal: document.getElementById('moreDetailsModal'),
        closeMoreDetailsModalBtn: document.getElementById('closeMoreDetailsModalBtn'),
        detailsAmount: document.getElementById('details-amount'),
        detailsDebitedFrom: document.getElementById('details-debited-from'),
        detailsMerchant: document.getElementById('details-merchant'),
        detailsTimestamp: document.getElementById('details-timestamp'),
        detailsStatus: document.getElementById('details-status'),
        detailsUniqueHash: document.getElementById('details-unique-hash'),
        detailsRawSms: document.getElementById('details-raw-sms'),

        accountSelectModal: document.getElementById('accountSelectModal'),
        closeAccountSelectModalBtn: document.getElementById('closeAccountSelectModalBtn'),
        saveAccountSelectionBtn: document.getElementById('saveAccountSelectionBtn'),
        accountListContainer: document.getElementById('account-list-container'),
        
        // Preview elements inside the account modal
        accSelMerchantName: document.getElementById('account-select-merchant-name-preview'),
        accSelTransactionTime: document.getElementById('account-select-transaction-time-preview'),
        accSelAmount: document.getElementById('account-select-amount-preview'),
        accSelCategoryIconWrapper: document.getElementById('account-select-category-icon-wrapper'),
        accSelCategoryName: document.getElementById('account-select-category-name-preview'),
        accSelCurrentAccountIcon: document.getElementById('account-select-current-account-icon-preview'),

        // --- Category Select Modal elements ---
        categoryModal: document.getElementById('categoryModal'),
        closeCategoryModalBtn: document.getElementById('closeCategoryModalBtn'),
        saveCategorySelectionBtn: document.getElementById('saveCategorySelectionBtn'),
        categoryListContainer: document.getElementById('category-list-container'),
        categorySearchInput: document.getElementById('category-search-input'),
        
        // Preview elements inside the category modal
        catSelMerchantName: document.getElementById('cat-select-merchant-name-preview'),
        catSelTransactionTime: document.getElementById('cat-select-transaction-time-preview'),
        catSelAmount: document.getElementById('cat-select-amount-preview'),
        catSelCategoryIconWrapper: document.getElementById('cat-select-category-icon-wrapper'),
        catSelCategoryName: document.getElementById('cat-select-category-name-preview'),
        catSelCurrentAccountIcon: document.getElementById('cat-select-current-account-icon-preview'),

        // New: Link Transaction Modal elements
        linkTransactionModal: document.getElementById('linkTransactionModal'),
        closeLinkModalBtn: document.getElementById('closeLinkModalBtn'),
        saveLinkBtn: document.getElementById('saveLinkBtn'), 
        linkCurrentTransactionPreview: document.getElementById('link-current-transaction-preview'), 
        linkCurrentMerchantIconPreview: document.getElementById('link-current-merchant-icon-preview'),
        linkCurrentMerchantNamePreview: document.getElementById('link-current-merchant-name-preview'),
        linkCurrentTransactionTimePreview: document.getElementById('link-current-transaction-time-preview'),
        linkCurrentAmountPreview: document.getElementById('link-current-amount-preview'),
        linkCurrentCategoryIconWrapper: document.getElementById('link-current-category-icon-wrapper'),
        linkCurrentCategoryNamePreview: document.getElementById('link-current-category-name-preview'),
        linkCurrentAccountIconPreview: document.getElementById('link-current-account-icon-preview'),
        linkableTransactionsList: document.getElementById('linkable-transactions-list'),

    };

    // --- State Management ---
    let state = {
        transaction: null,
        allCategories: [],
        allAccounts: [],
        linkableTransactions: [],
        originalTransaction: {},
        tempSelectedSubcategoryId: null,
        tempSelectedAccountId: null,
        linkedTransactionDetails: null,
        hasUnsavedChanges: false,
        apiToken: '',
        apiBaseUrl: 'https://finance.arlp.live/api/v1',
    };

    // --- Main Initialization ---
    async function initialize() {
        setLoading(true);
        try {
            const urlParams = new URLSearchParams(window.location.search);
            state.apiToken = urlParams.get('token');
            if (!state.apiToken) throw new Error("Access token is missing.");

            const [transactionData, categories, accounts] = await Promise.all([
                fetchApi('/transactions/get/by-token'),
                fetchApi('/categories/all_details'),
                fetchApi('/accounts/for-mini-app')
            ]);
            
            state.transaction = transactionData;
            state.originalTransaction = JSON.parse(JSON.stringify(transactionData));
            state.allCategories = categories;
            state.allAccounts = accounts;
            state.tempSelectedSubcategoryId = transactionData.subcategory?.id;
            state.tempSelectedAccountId = transactionData.account?.id;

            populateUI();
            configureMainButton();
            setupEventListeners();

        } catch (error) {
            console.error("Initialization Error:", error);
            showError(error.message);
        } finally {
            setLoading(false);
            feather.replace({ width: '1em', height: '1em', 'stroke-width': 1.8 });
        }
    }

    // --- API Fetch Utility ---
    async function fetchApi(endpoint, options = {}) {
        const headers = {
            'Authorization': `Bearer ${state.apiToken}`,
            'Content-Type': 'application/json',
            ...options.headers,
        };
        const response = await fetch(`${state.apiBaseUrl}${endpoint}`, { ...options, headers });
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(`API Error: ${errorData.detail || response.statusText}`);
        }
        return response.json();
    }

    // --- UI Population ---
    function populateUI() {
        const { transaction } = state;
        if (!transaction) return;

        elements.transactionAmount.textContent = `-${getCurrencySymbol(transaction.currency)}${transaction.amount.toFixed(2)}`;
        elements.mainCategoryName.textContent = getSubcategoryDisplayName(transaction.subcategory).toUpperCase();
        elements.mainCategoryIconWrapper.innerHTML = createIconHTML(transaction.subcategory?.icon_name);
        
        if (transaction.account) {
            elements.fromAccountDetails.textContent = `***${transaction.account.account_last4}`;
            elements.fromAccountIcon.textContent = transaction.account.name?.charAt(0).toUpperCase() || 'A';
        } else {
            elements.fromAccountDetails.textContent = 'Select Account';
            elements.fromAccountIcon.textContent = '?';
        }
        
        elements.paidToMerchantName.textContent = transaction.merchant_vpa || 'Unknown Merchant';
        elements.descriptionTextarea.value = transaction.description || '';

        if (transaction.transaction_datetime_from_sms) {
            const date = new Date(transaction.transaction_datetime_from_sms);
            elements.transactionDate.textContent = date.toLocaleDateString('en-GB', { weekday: 'short', month: 'short', day: 'numeric', year: '2-digit' }).replace(/,/g, '');
        } else {
            elements.transactionDate.textContent = 'No Date';
        }

        updateReimbursableStatusDisplay();
        updateLinkedTransactionDisplay();
        
        feather.replace();
    }

    function updateReimbursableStatusDisplay() {
        const { transaction } = state;
        if (!transaction || !elements.reimbursableToggle) return;

        const currentOverride = transaction.override_reimbursable;
        const segments = elements.reimbursableToggle.querySelectorAll('.toggle-segment');
        let activeIndex = 0;

        if (currentOverride === true) {
            activeIndex = 1; 
        } else if (currentOverride === false) {
            activeIndex = 2; 
        }

        segments.forEach((segment, index) => {
            if (index === activeIndex) {
                segment.classList.add('active-text');
            } else {
                segment.classList.remove('active-text');
            }
        });
       
        const segmentWidth = (elements.reimbursableToggle.offsetWidth - 4) / 3; // Subtract total padding
        const transformValue = `translateX(${activeIndex * segmentWidth}px)`;
    
        elements.reimbursableToggle.style.setProperty('--slider-transform', transformValue);

    }

    async function updateLinkedTransactionDisplay() {
        const { transaction } = state;
        const linkActionTextElement = elements.linkTransactionAction.querySelector('#link-action-text'); 
        if (!transaction) return;

        if (transaction.linked_transaction_hash) {
            setLoading(true);
            try {
                const linkedTxDetails = await fetchApi(`/transactions/by-hash/${transaction.linked_transaction_hash}`);
                state.linkedTransactionDetails = linkedTxDetails; 

                if (linkedTxDetails) {
                    const displayDate = linkedTxDetails.transaction_datetime_from_sms 
                        ? new Date(linkedTxDetails.transaction_datetime_from_sms).toLocaleDateString('en-GB', { month: 'short', day: 'numeric' })
                        : 'Date N/A';
                    const displayAmount = `${getCurrencySymbol(linkedTxDetails.currency)}${linkedTxDetails.amount.toFixed(2)}`;
                    
                    elements.linkedTransactionInfo.textContent = `Linked: ${displayAmount} (${displayDate})`;
                    elements.linkedTransactionInfo.style.color = '#3b82f6';
                    if(linkActionTextElement) linkActionTextElement.textContent = 'Manage Link';
                } else {
                    elements.linkedTransactionInfo.textContent = "Linked (Details N/A)";
                    if(linkActionTextElement) linkActionTextElement.textContent = 'Link Transaction'; 
                    state.linkedTransactionDetails = null; 
                }
            } catch (error) {
                console.error("Failed to fetch linked transaction details:", error);
                elements.linkedTransactionInfo.textContent = "Linked (Error)";
                if(linkActionTextElement) linkActionTextElement.textContent = 'Link Transaction';
                state.linkedTransactionDetails = null; 
            } finally {
                setLoading(false);
            }
        } else {
            elements.linkedTransactionInfo.textContent = "Not Linked";
            elements.linkedTransactionInfo.style.color = ''; 
            if(linkActionTextElement) linkActionTextElement.textContent = 'Link Transaction';
            state.linkedTransactionDetails = null;
        }
    }
    
    function populateMoreDetailsModal() {
        const { transaction } = state;
        if (!transaction) return;

        elements.detailsAmount.textContent = `${getCurrencySymbol(transaction.currency)} ${transaction.amount.toFixed(2)}`;
        elements.detailsDebitedFrom.textContent = transaction.account ? `${transaction.account.name} (***${transaction.account.account_last4})` : 'N/A';
        elements.detailsMerchant.textContent = transaction.merchant_vpa || 'N/A';
        elements.detailsTimestamp.textContent = new Date(transaction.transaction_datetime_from_sms).toLocaleString('en-GB');
        elements.detailsStatus.textContent = transaction.status.replace('_', ' ').toUpperCase();
        elements.detailsUniqueHash.textContent = transaction.unique_hash;
        elements.detailsRawSms.textContent = transaction.raw_sms_content;
    }

    // "UI Population" section

    function populateAccountSelectModalPreview() {
        const { transaction, allAccounts } = state;
        if (!transaction) return;
        const accountToPreview = allAccounts.find(acc => acc.id === state.tempSelectedAccountId) || transaction.account;
        elements.accSelMerchantName.textContent = transaction.merchant_vpa || 'Unknown';
        elements.accSelAmount.textContent = `-${getCurrencySymbol(transaction.currency)}${transaction.amount.toFixed(2)}`;
        if (transaction.transaction_datetime_from_sms) {
            elements.accSelTransactionTime.textContent = new Date(transaction.transaction_datetime_from_sms).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
        } else {
            elements.accSelTransactionTime.textContent = "Time N/A";
        }
        
        elements.accSelCategoryName.textContent = getSubcategoryDisplayName(transaction.subcategory).toUpperCase();
        elements.accSelCategoryIconWrapper.innerHTML = createIconHTML(transaction.subcategory?.icon_name);
        
        if (accountToPreview) {
            elements.accSelCurrentAccountIcon.textContent = accountToPreview.name?.charAt(0).toUpperCase() || 'A';
        } else {
            elements.accSelCurrentAccountIcon.textContent = '?';
        }
        feather.replace();
    }

    function populateAccountsInModalList() {
        const { allAccounts, tempSelectedAccountId } = state;
        elements.accountListContainer.innerHTML = '';
        const groupedAccounts = allAccounts.reduce((acc, account) => {
            const type = account.account_type || 'UNKNOWN';
            if (!acc[type]) acc[type] = [];
            acc[type].push(account);
            return acc;
        }, {});

        const accountTypeOrder = ['savings_account', 'wallet', 'credit_card', 'unknown'];

        accountTypeOrder.forEach(typeKey => {
            const group = groupedAccounts[typeKey];
            if (!group) return;
            
            const groupDiv = document.createElement('div');
            groupDiv.className = 'account-group';
            
            const title = document.createElement('h4');
            title.className = 'account-group-title';
            title.textContent = typeKey.replace('_', ' ').toUpperCase() + 'S';
            groupDiv.appendChild(title);
            group.forEach(acc => {
                const itemDiv = document.createElement('div');
                itemDiv.className = 'account-item';
                itemDiv.dataset.accountId = acc.id;
                
                if (acc.id === tempSelectedAccountId) {
                    itemDiv.classList.add('selected');
                }

                const iconName = getBankIconClass(acc.name, acc.account_type);

                itemDiv.innerHTML = `
                    <div class="account-item-icon">
                    <img class="custom-icon" src="/static/images/icons/${iconName}" alt="${iconName.split('/').pop().split('.')[0]}">
                    </div>
                    <div class="account-item-details">
                        <span class="account-item-name">${acc.name}</span>
                        <span class="account-item-last4">***${acc.account_last4}</span>
                    </div>
                    <input type="radio" name="selectedAccountRadio" value="${acc.id}" class="account-item-radio" ${acc.id === tempSelectedAccountId ? 'checked' : ''}>
                `;

                
                groupDiv.appendChild(itemDiv);
            });
            elements.accountListContainer.appendChild(groupDiv);
        });
    }

    function populateCategorySelectModalPreview() {
        const { transaction, allCategories } = state;
        if (!transaction) return;

        // Populate the static parts of the preview
        elements.catSelMerchantName.textContent = transaction.merchant_vpa || 'Unknown';
        elements.catSelAmount.textContent = `-${getCurrencySymbol(transaction.currency)}${transaction.amount.toFixed(2)}`;
        elements.catSelCurrentAccountIcon.textContent = transaction.account?.name.charAt(0).toUpperCase() || '?';
        
        if (transaction.transaction_datetime_from_sms) {
            elements.catSelTransactionTime.textContent = new Date(transaction.transaction_datetime_from_sms).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
        } else {
            elements.catSelTransactionTime.textContent = "Time N/A";
        }

        // Find the currently selected subcategory to display its info
        let subcatToPreview = null;
        for (const parentCat of allCategories) {
            const found = parentCat.subcategories.find(sc => sc.id === state.tempSelectedSubcategoryId);
            if (found) {
                subcatToPreview = { ...found, parent_category_name: parentCat.name };
                break;
            }
        }
        
        elements.catSelCategoryName.textContent = getSubcategoryDisplayName(subcatToPreview).toUpperCase();
        elements.catSelCategoryIconWrapper.innerHTML = createIconHTML(subcatToPreview?.icon_name);
        feather.replace();
    }

    function populateCategoriesInModal(filterText = '') {
        const { allCategories, tempSelectedSubcategoryId } = state;
        elements.categoryListContainer.innerHTML = '';
        const searchTerm = filterText.toLowerCase();

        allCategories.forEach(parentCat => {
            // Filter subcategories based on search term
            const matchingSubcategories = parentCat.subcategories.filter(subCat => 
                subCat.name.toLowerCase().includes(searchTerm) || 
                parentCat.name.toLowerCase().includes(searchTerm)
            );

            // Only show the parent category if it has matching subcategories
            if (matchingSubcategories.length > 0) {
                const groupDiv = document.createElement('div');
                groupDiv.className = 'category-group';
                groupDiv.innerHTML = `
                    <div class="category-group-title">${parentCat.name}</div>
                    <div class="category-group-subtitle">${parentCat.description || ''}</div>
                `;
                
                const subcategoryGridDiv = document.createElement('div');
                subcategoryGridDiv.className = 'subcategory-grid';

                matchingSubcategories.forEach(subCat => {
                    const itemDiv = document.createElement('div');
                    itemDiv.className = 'subcategory-item';
                    itemDiv.dataset.subcategoryId = subCat.id;
                    if (subCat.id === tempSelectedSubcategoryId) {
                        itemDiv.classList.add('selected');
                    }
                    itemDiv.innerHTML = `
                        <div class="subcategory-icon-wrapper">${createIconHTML(subCat.icon_name)}</div>
                        <div class="subcategory-name">${subCat.name}</div>
                    `;
                    subcategoryGridDiv.appendChild(itemDiv);
                });

                groupDiv.appendChild(subcategoryGridDiv);
                elements.categoryListContainer.appendChild(groupDiv);
            }
        });
        feather.replace();
    }

    function populateLinkTransactionModalPreview() {
        const { transaction } = state;
        if (!transaction) return;

        elements.linkCurrentMerchantNamePreview.textContent = transaction.merchant_vpa || 'Unknown';
        elements.linkCurrentAmountPreview.textContent = `-${getCurrencySymbol(transaction.currency)}${transaction.amount.toFixed(2)}`;
        elements.linkCurrentAccountIconPreview.textContent = transaction.account?.name.charAt(0).toUpperCase() || '?';
        
        if (transaction.transaction_datetime_from_sms) {
            elements.linkCurrentTransactionTimePreview.textContent = new Date(transaction.transaction_datetime_from_sms).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
        } else {
            elements.linkCurrentTransactionTimePreview.textContent = "Time N/A";
        }
        
        elements.linkCurrentCategoryNamePreview.textContent = getSubcategoryDisplayName(transaction.subcategory).toUpperCase();
        elements.linkCurrentCategoryIconWrapper.innerHTML = createIconHTML(transaction.subcategory?.icon_name);
        feather.replace();
    }

    function populateLinkableTransactionsList() {
        elements.linkableTransactionsList.innerHTML = ''; 

        const currentLinkedHash = state.transaction.linked_transaction_hash;

        if (state.linkableTransactions.length === 0 && !currentLinkedHash) {
            elements.linkableTransactionsList.innerHTML = '<p style="text-align:center; color:#6b7280; padding: 20px;">No recent transactions available to link.</p>';
            return;
        }

        let displayList = [...state.linkableTransactions];
        
      
        if (currentLinkedHash && state.linkedTransactionDetails && !displayList.find(tx => tx.unique_hash === currentLinkedHash)) {
             displayList.unshift(state.linkedTransactionDetails); 
        }


        if (displayList.length === 0) {
             elements.linkableTransactionsList.innerHTML = '<p style="text-align:center; color:#6b7280; padding: 20px;">No transactions to display.</p>';
            return;
        }


        displayList.forEach(tx => {
            if (tx.unique_hash === state.transaction.unique_hash) {
                return;
            }

            const itemDiv = document.createElement('div');
            itemDiv.className = 'account-item linkable-tx-item';
            itemDiv.dataset.hash = tx.unique_hash;

            const isCurrentlyLinked = tx.unique_hash === currentLinkedHash;
            if (isCurrentlyLinked) {
                itemDiv.classList.add('currently-linked'); 
            }

            const txDate = tx.transaction_datetime_from_sms 
                ? new Date(tx.transaction_datetime_from_sms).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: '2-digit'})
                : 'Date N/A';
            const txAmount = `${getCurrencySymbol(tx.currency)}${tx.amount.toFixed(2)}`;
            const merchantOrDesc = tx.merchant_vpa || tx.description || 'Unknown Transaction';
            
            // const amountIcon = tx.amount > 0 ? `<i data-feather="arrow-down-circle" style="color: green;"></i>` : `<i data-feather="arrow-up-circle" style="color: red;"></i>`;

            const amountIcon = tx.amount > 0 ? createIconHTML(tx.subcategory?.icon_name) : `<i data-feather="arrow-up-circle" style="color: red;"></i>`;

            const buttonText = isCurrentlyLinked ? 'Unlink' : 'Link';
            const buttonClass = isCurrentlyLinked ? 'unlink-button' : 'link-button'; 

            itemDiv.innerHTML = `
                <div class="account-item-icon" style="background-color: #e5e7eb;">${amountIcon}</div>
                <div class="account-item-details">
                    <span class="account-item-name">${txAmount} - ${merchantOrDesc.substring(0, 25)}${merchantOrDesc.length > 25 ? '...' : ''}</span>
                    <span class="account-item-last4">${getSubcategoryDisplayName(tx.subcategory)} - ${txDate}</span>
                </div>
                <button class="${buttonClass}" style="padding: 6px 12px; border: none; border-radius: 8px; cursor: pointer;">${buttonText}</button>
            `;
            elements.linkableTransactionsList.appendChild(itemDiv);
        });
        feather.replace();
    }

    // --- UI Helpers ---
    function setLoading(isLoading) { elements.loadingOverlay.style.display = isLoading ? 'flex' : 'none'; }
    function showError(message) { tg.showAlert(message); if(tg.MainButton.isVisible) tg.MainButton.hide(); }
    function getCurrencySymbol(code) { return code === 'USD' ? '$' : '₹'; }

    function getSubcategoryDisplayName(subcategory) {
        if (!subcategory || !subcategory.name) return 'Uncategorized';
        const parentName = subcategory.parent_category_name;
        return (parentName && parentName.toLowerCase() !== 'general') ? `${parentName} (${subcategory.name})` : subcategory.name;
    }
    
    function createIconHTML(iconString) {
        if (!iconString) return `<i data-feather="circle"></i>`;
        if (iconString.startsWith('fthr:')) return `<i data-feather="${iconString.substring(5)}"></i>`;
        if (iconString.startsWith('img:')) return `<img src="/static/images/icons/${iconString.substring(4)}" class="custom-icon">`;
        if (iconString.startsWith('emoji:')) return `<span class="emoji-icon">${iconString.substring(6)}</span>`;
        return `<i data-feather="tag"></i>`; // Default
    }

    function setupClipboard() {
        document.querySelectorAll('.copy-btn').forEach(button => {
            button.addEventListener('click', (e) => {
                e.stopPropagation(); // Prevent modal from closing if clicked inside
                const targetSelector = button.dataset.clipboardTarget;
                const targetElement = document.querySelector(targetSelector);
                if (targetElement) {
                    navigator.clipboard.writeText(targetElement.textContent.trim())
                        .then(() => {
                            const originalIcon = button.innerHTML;
                            button.innerHTML = '<i data-feather="check" style="color: #31b545;"></i>';
                            feather.replace();
                            setTimeout(() => {
                                button.innerHTML = originalIcon;
                                feather.replace();
                            }, 1500);
                        })
                        .catch(err => console.error('Failed to copy text: ', err));
                }
            });
        });
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

    // --- Event Listeners ---
    function setupEventListeners() {
        elements.descriptionTextarea.addEventListener('input', () => { state.hasUnsavedChanges = true; });

        
        elements.moreDetailsAction.addEventListener('click', () => {
            populateMoreDetailsModal(); 
            elements.moreDetailsModal.style.display = 'flex';
            feather.replace();
        });

        elements.fromAccountAction.addEventListener('click', () => {
            state.tempSelectedAccountId = state.transaction.account?.id;
            populateAccountSelectModalPreview();
            populateAccountsInModalList();
            elements.accountSelectModal.style.display = 'flex';
        });

        elements.closeAccountSelectModalBtn.addEventListener('click', () => {
            elements.accountSelectModal.style.display = 'none';
        });

         elements.accountSelectModal.addEventListener('click', (e) => {
            if (e.target === elements.accountSelectModal) {
                elements.accountSelectModal.style.display = 'none';
            }
        });

        elements.saveAccountSelectionBtn.addEventListener('click', () => {
            if (state.tempSelectedAccountId !== state.transaction.account?.id) {
                state.transaction.account = state.allAccounts.find(acc => acc.id === state.tempSelectedAccountId);
                state.hasUnsavedChanges = true;
                populateUI();
            }
            elements.accountSelectModal.style.display = 'none';
        });

        elements.accountListContainer.addEventListener('click', (e) => {
            const item = e.target.closest('.account-item');
            if (item) {
                elements.accountListContainer.querySelectorAll('.account-item.selected').forEach(el => el.classList.remove('selected'));
                item.classList.add('selected');

                const radio = item.querySelector('.account-item-radio');
                if (radio) {
                    radio.checked = true;
                    state.tempSelectedAccountId = parseInt(radio.value, 10);
                    populateAccountSelectModalPreview(); 
                }
            }
        });

        elements.categoryBadge.addEventListener('click', () => {
            state.tempSelectedSubcategoryId = state.transaction.subcategory?.id; 
            populateCategorySelectModalPreview();
            populateCategoriesInModal();
            elements.categoryModal.style.display = 'flex';
        });

         elements.closeCategoryModalBtn.addEventListener('click', () => {
            elements.categoryModal.style.display = 'none';
        });
        
        elements.categoryModal.addEventListener('click', (e) => {
            if (e.target === elements.categoryModal) {
                elements.categoryModal.style.display = 'none';
            }
        });

        elements.saveCategorySelectionBtn.addEventListener('click', () => {
            if (state.tempSelectedSubcategoryId !== state.transaction.subcategory?.id) {
                for (const parentCat of state.allCategories) {
                    const foundSubcat = parentCat.subcategories.find(sc => sc.id === state.tempSelectedSubcategoryId);
                    if (foundSubcat) {
                        state.transaction.subcategory = { ...foundSubcat, parent_category_name: parentCat.name };
                        break;
                    }
                }
                state.hasUnsavedChanges = true;
                populateUI(); 
            }
            elements.categoryModal.style.display = 'none';
        });

        elements.categorySearchInput.addEventListener('input', (e) => {
            populateCategoriesInModal(e.target.value);
        });

        elements.categoryListContainer.addEventListener('click', (e) => {
            const item = e.target.closest('.subcategory-item');
            if (item) {
                elements.categoryListContainer.querySelectorAll('.subcategory-item.selected').forEach(el => el.classList.remove('selected'));
                item.classList.add('selected');
                state.tempSelectedSubcategoryId = parseInt(item.dataset.subcategoryId, 10);
                populateCategorySelectModalPreview(); 
            }
        });

         elements.closeMoreDetailsModalBtn.addEventListener('click', () => {
            elements.moreDetailsModal.style.display = 'none';
        });

        
        elements.moreDetailsModal.addEventListener('click', (e) => {
            if (e.target === elements.moreDetailsModal) {
                elements.moreDetailsModal.style.display = 'none';
            }
        });

         elements.linkTransactionAction.addEventListener('click', async () => {
            if (state.transaction.linked_transaction_hash) {
                console.log("Currently linked. Opening modal to manage/change link.");
            }
            
            setLoading(true);
            try {
                const linkableTxs = await fetchApi('/transactions/linkable');
                state.linkableTransactions = linkableTxs;
                populateLinkTransactionModalPreview(); 
                populateLinkableTransactionsList();     
                elements.linkTransactionModal.style.display = 'flex';
            } catch (error) {
                showError("Could not fetch linkable transactions: " + error.message);
            } finally {
                setLoading(false);
            }
        });

        // New: Event listeners for "Link Transaction" Modal
        elements.closeLinkModalBtn.addEventListener('click', () => {
            elements.linkTransactionModal.style.display = 'none';
        });

        elements.linkTransactionModal.addEventListener('click', (e) => { 
            if (e.target === elements.linkTransactionModal) {
                elements.linkTransactionModal.style.display = 'none';
            }
        });

        elements.linkableTransactionsList.addEventListener('click', (e) => {
            const buttonClicked = e.target.closest('button');
            if (!buttonClicked) return;

            const itemDiv = buttonClicked.closest('.linkable-tx-item');
            if (!itemDiv) return;

            const selectedHash = itemDiv.dataset.hash;

            if (buttonClicked.classList.contains('unlink-button')) { 
                state.transaction.linked_transaction_hash = null;
            } else { 
                state.transaction.linked_transaction_hash = selectedHash;
            }
            
            state.hasUnsavedChanges = true;
            updateLinkedTransactionDisplay(); 
            populateLinkableTransactionsList(); 
           
        });
        if (elements.reimbursableToggle) { 
            elements.reimbursableToggle.addEventListener('click', (e) => {
                const selectedSegment = e.target.closest('.toggle-segment');
                if (!selectedSegment) return; 

                const selectedValue = selectedSegment.dataset.value;
                let newOverrideValue = null;

                if (selectedValue === 'true') {
                    newOverrideValue = true;
                } else if (selectedValue === 'false') {
                    newOverrideValue = false;
                } 

                if (state.transaction.override_reimbursable !== newOverrideValue) {
                    state.transaction.override_reimbursable = newOverrideValue;
                    state.hasUnsavedChanges = true;
                    updateReimbursableStatusDisplay(); 
                }
            });
        }

        setupClipboard();
    }

    // --- Main Button & Save Logic ---
    function configureMainButton() {
        tg.MainButton.setParams({
            text: 'SAVE CHANGES',
            color: '#3b82f6',
            text_color: '#ffffff',
        }).show();
        tg.MainButton.onClick(handleSave);
    }

    async function handleSave() {
        if (!tg.MainButton.isActive) return;
        
        const patchData = {};
        if (state.hasUnsavedChanges) {
            patchData.description = elements.descriptionTextarea.value;
        }
        if (state.tempSelectedSubcategoryId !== state.transaction.subcategory?.id) {
            patchData.subcategory_id = state.tempSelectedSubcategoryId;
        }
        if (state.tempSelectedAccountId !== state.transaction.account?.id) {
            patchData.account_id = state.tempSelectedAccountId;
        }

         if (state.transaction.linked_transaction_hash !== (state.originalTransaction?.linked_transaction_hash || null)) {
            patchData.linked_transaction_hash = state.transaction.linked_transaction_hash;
            state.hasUnsavedChanges = true;
        }

        if (state.transaction.override_reimbursable !== (state.originalTransaction?.override_reimbursable || null)) {
            patchData.override_reimbursable = state.transaction.override_reimbursable;
            state.hasUnsavedChanges = true;
        }

        if (Object.keys(patchData).length === 0) {
            tg.close();
            return;
        }

        tg.MainButton.showProgress();
        try {
            await fetchApi('/transactions/by-token', {
                method: 'PATCH',
                body: JSON.stringify(patchData),
            });
            tg.close();
        } catch (error) {
            showError(`Error saving: ${error.message}`);
        } finally {
            tg.MainButton.hideProgress();
            state.hasUnsavedChanges = false;
        }
    }

    initialize();
});