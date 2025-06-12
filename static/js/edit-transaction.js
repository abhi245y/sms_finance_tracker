// Immediately execute this code when the script is loaded
(function() {
    'use strict';

    // 1. Initialize Telegram Mini App
    const tg = window.Telegram.WebApp;
    tg.expand();
    // Use Telegram's theme settings
    tg.setHeaderColor(tg.themeParams.secondary_bg_color || '#ffffff');
    tg.setBackgroundColor(tg.themeParams.bg_color || '#ffffff');


    // --- DOM Elements ---
    const transactionAmountEl = document.getElementById('transaction-amount');
    const transactionMerchantEl = document.getElementById('transaction-merchant'); 
    const transactionAccountDateEl = document.getElementById('transaction-account-date');
    const descriptionTextarea = document.getElementById('description');
    const loadingOverlay = document.getElementById('loading-overlay');

    // --- State ---
    let access_token = '';
    const API_BASE_URL = 'https://finance.arlp.live/api/v1';

    // 2. Main function to initialize the app
    async function initialize() {
        setLoading(true);
        try {
            const urlParams = new URLSearchParams(window.location.search);
            access_token = urlParams.get('token');

            if (!access_token) {
                showError("Access token not found.");
                return;
            }

            const transaction = await fetchTransaction();
            populateUI(transaction);
            configureMainButton();
        } catch (error) {
            showError(`Failed to load transaction: ${error.message}`);
        } finally {
            setLoading(false);
        }
    }

    // 3. API Fetch function
    async function fetchTransaction() {
        const response = await fetch(`${API_BASE_URL}/transactions/get/by-token`, {
            headers: { 'Authorization': `Bearer ${access_token}` },
        });
        if (!response.ok) throw new Error(`API Error: ${response.statusText}`);
        return await response.json();
    }

    // 4. Helper functions
    function setLoading(isLoading) {
        loadingOverlay.style.display = isLoading ? 'flex' : 'none';
    }

    function showError(message) {
        tg.showAlert(message);
        tg.MainButton.hide();
    }

    function populateUI(transaction) {
        transactionAmountEl.textContent = `${transaction.amount.toFixed(2)} ${transaction.currency}`;
        transactionMerchantEl.textContent = transaction.merchant_vpa || 'Unknown Merchant';
        
        const accountName = transaction.account ? transaction.account.name : 'Unknown Account';
        const date = new Date(transaction.transaction_datetime_from_sms).toLocaleString();
        transactionAccountDateEl.textContent = `${accountName} • ${date}`;
        
        descriptionTextarea.value = transaction.description || '';
    }

    function configureMainButton() {
        tg.MainButton.setText('Save Description');
        tg.MainButton.setTextColor(tg.themeParams.button_text_color || '#ffffff');
        tg.MainButton.color = tg.themeParams.button_color || '#2481cc';
        tg.MainButton.show();
        tg.MainButton.onClick(handleSave);
    }

    // 5. Event handler for saving
    async function handleSave() {
        if (!tg.MainButton.isVisible || !tg.MainButton.isActive) return;

        tg.MainButton.showProgress();
        try {
            const newDescription = descriptionTextarea.value;
            const response = await fetch(`${API_BASE_URL}/transactions/by-token`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${access_token}`,
                },
                body: JSON.stringify({ description: newDescription }),
            });

            if (!response.ok) throw new Error('Failed to save description.');

            tg.showPopup({
                title: 'Success',
                message: 'Description has been updated!',
                buttons: [{ type: 'ok', text: 'Done' }]
            }, () => tg.close());

        } catch (error) {
            tg.showAlert(`Error: ${error.message}`);
        } finally {
            tg.MainButton.hideProgress();
        }
    }

    // Run the initialization
    initialize();

})();