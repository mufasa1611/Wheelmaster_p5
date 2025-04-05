class StockManager {
    constructor() {
        this.setupEventListeners();
        this.bagQuantities = {};
        this.loadBagQuantities();
        this.initializeStockLevels();
    }

    loadBagQuantities() {
        fetch('/bag/quantities/')
            .then(response => response.json())
            .then(data => {
                this.bagQuantities = data;
                this.updateStockDisplays();
            })
            .catch(error => console.error('Error loading bag quantities:', error));
    }

    setupEventListeners() {
        // Use event delegation for stock adjustment buttons
        document.body.addEventListener('click', (e) => {
            if (e.target.closest('.adjust-stock')) {
                const button = e.target.closest('.adjust-stock');
                const productId = button.dataset.productId;
                const action = button.dataset.action;
                const input = button.closest('.stock-actions').querySelector('.stock-input');
                const quantity = parseInt(input.value) || 0;

                if (quantity > 0) {
                    this.adjustStock(productId, quantity, action);
                }
            }

            if (e.target.closest('.reset-reserved')) {
                this.handleResetReserved(e);
            }
        });

        // Use event delegation for stock input changes
        document.body.addEventListener('change', (e) => {
            if (e.target.classList.contains('stock-input')) {
                const value = parseInt(e.target.value);
                if (isNaN(value) || value < 0) {
                    e.target.value = 0;
                }
            }
        });
    }

    handleResetReserved(e) {
        const button = e.target.closest('.reset-reserved');
        const productId = button.dataset.productId;
        const row = button.closest('tr');

        if (!productId) return;

        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        // Reset reserved stock and clear from bag
        fetch(`/products/reset_reserved/${productId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) throw new Error(data.error);

            // Update displays
            const stockQty = row.querySelector('.stock-qty');
            const reservedQty = row.querySelector('.reserved-qty');
            const availableQty = row.querySelector('.available-qty');

            if (stockQty) stockQty.textContent = data.stock_qty;
            if (reservedQty) reservedQty.textContent = '0';
            if (availableQty) availableQty.textContent = data.available_qty;

            // Update bag mini if exists
            if (typeof updateBagTotal === 'function') {
                updateBagTotal();
            }

            this.showToast('Reserved stock reset successfully', 'success');
        })
        .catch(error => {
            this.showToast(error.message || 'Error resetting reserved stock', 'error');
            console.error('Error:', error);
        });
    }

    adjustStock(productId, quantity, action) {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        console.log(`Adjusting stock for Product ID: ${productId}, Quantity: ${quantity}, Action: ${action}`);

        if (!productId || !action || quantity <= 0) {
            console.error('Invalid data for stock adjustment:', { productId, quantity, action });
            this.showToast('Invalid data for stock adjustment', 'error');
            return;
        }

        fetch('/products/adjust_stock/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({
                product_id: productId,
                quantity: quantity,
                action: action
            })
        })
        .then(response => {
            if (!response.ok) {
                console.error(`Error adjusting stock: ${response.status} ${response.statusText}`);
                throw new Error(`Error adjusting stock: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                console.error(`Error adjusting stock: ${data.error}`);
                throw new Error(data.error);
            }

            console.log(`Stock adjusted successfully:`, data);

            const row = document.querySelector(`tr[data-product-id="${productId}"]`);
            if (row) {
                const stockQty = row.querySelector('.stock-qty');
                const availableQty = row.querySelector('.available-qty');
                const input = row.querySelector('.stock-input');

                if (stockQty) stockQty.textContent = data.stock_qty;
                if (availableQty) availableQty.textContent = data.available_qty;
                if (input) input.value = '0';
            }

            this.showToast(`Stock ${action}ed successfully`, 'success');
        })
        .catch(error => {
            this.showToast(error.message || 'Error adjusting stock', 'error');
            console.error('Error:', error);
        });
    }

    updateStockDisplays() {
        document.querySelectorAll('[data-stock-qty]').forEach(element => {
            const quantity = parseInt(element.dataset.stockQty) || 0;
            this.updateStockIndicators(element, quantity);
        });
    }

    updateStockIndicators(element, quantity) {
        if (!element) return;

        element.classList.remove('out-of-stock', 'low-stock', 'medium-stock', 'high-stock');
        
        if (quantity <= 0) {
            element.classList.add('out-of-stock');
        } else if (quantity <= 5) {
            element.classList.add('low-stock');
        } else if (quantity <= 20) {
            element.classList.add('medium-stock');
        } else {
            element.classList.add('high-stock');
        }
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        container.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }

    initializeStockLevels() {
        this.updateStockDisplays();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.stockManager = new StockManager();
});
