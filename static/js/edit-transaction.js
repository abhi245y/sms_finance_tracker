document.addEventListener('DOMContentLoaded', function() {
    'use strict';
    const tg = window.Telegram.WebApp;
    tg.expand();
    tg.setHeaderColor('secondary_bg_color');

    // --- DOM Elements ---
    const loadingOverlay = document.getElementById('loading-overlay');
    const merchantEl = document.getElementById('merchant-name');
    const amountEl = document.getElementById('transaction-amount');
    const dateEl = document.getElementById('transaction-date');
    const accountDetailsEl = document.getElementById('account-details');
    const categoryDetailsEl = document.getElementById('category-details').querySelector('span');
    const descriptionTextarea = document.getElementById('description');

    // --- STATE ---
    let access_token = '';
    const API_BASE_URL = 'https://finance.arlp.live/api/v1';

    // --- MAIN ---
    async function initialize() {
        setLoading(true);
        try {
            const urlParams = new URLSearchParams(window.location.search);
            access_token = urlParams.get('token');
            if (!access_token) throw new Error("Access token not found.");

            const transaction = await fetchTransaction();
            populateUI(transaction);
            configureMainButton();
        } catch (error) {
            showError(error.message);
        } finally {
            setLoading(false);
        }
    }

    // --- API ---
    async function fetchTransaction() {
        const response = await fetch(`${API_BASE_URL}/transactions/get/by-token`, {
            headers: { 'Authorization': `Bearer ${access_token}` },
        });
        if (!response.ok) throw new Error(`API Error: ${response.statusText}`);
        return await response.json();
    }

    // --- UI HELPERS ---
    function setLoading(isLoading) {
        loadingOverlay.style.display = isLoading ? 'flex' : 'none';
    }

    function showError(message) {
        tg.showAlert(message);
        tg.MainButton.hide();
    }

    function populateUI(transaction) {
        merchantEl.textContent = transaction.merchant_vpa || 'Unknown Merchant';
        amountEl.textContent = `- ₹${transaction.amount.toFixed(2)}`;
        descriptionTextarea.value = transaction.description || '';

        if (transaction.category_obj) {
            categoryDetailsEl.textContent = transaction.category_obj.name;
        } else {
            categoryDetailsEl.textContent = 'Uncategorized';
        }

        if (transaction.account) {
            accountDetailsEl.textContent = `${transaction.account.name} · ${transaction.account.account_last4}`;
        } else {
            accountDetailsEl.textContent = 'Unknown Account';
        }

        if (transaction.transaction_datetime_from_sms) {
            const date = new Date(transaction.transaction_datetime_from_sms);
            dateEl.textContent = date.toLocaleString('en-US', {
                month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit', hour12: true
            });
        } else {
            dateEl.textContent = 'No Date';
        }
        
        feather.replace({ width: '22px', height: '22px', 'stroke-width': 1.8 });
    }

    // --- TELEGRAM BUTTONS ---
    function configureMainButton() {
        tg.MainButton.setParams({
            text: 'Save Notes',
            color: '#31b545',
            text_color: '#ffffff',
        });
        tg.MainButton.show();
        tg.MainButton.onClick(handleSave);
    }

    async function handleSave() {
        if (!tg.MainButton.isVisible || !tg.MainButton.isActive) return;
        tg.MainButton.showProgress();
        try {
            const newDescription = descriptionTextarea.value;
            await fetch(`${API_BASE_URL}/transactions/by-token`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${access_token}` },
                body: JSON.stringify({ description: newDescription }),
            });
            tg.close();
        } catch (error) {
            tg.showAlert(`Error: ${error.message}`);
        } finally {
            tg.MainButton.hideProgress();
        }
    }

    // --- RUN ---
    initialize();
});