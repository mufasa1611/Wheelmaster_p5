class StockManager {
    constructor() {
        this.setupEventListeners();
        this.bagQuantities = {};
        this.loadBagQuantities();
    }

    loadBagQuantities() {
        // Load current quantities in bag for each product
        fetch('/bag/quantities/')
            .then(response => response.json())
            .then(data => {
                this.bagQuantities = data;
                this.updateStockDisplays(); // Update displays after loading quantities
            })
            .catch(error => console.error('Error loading bag quantities:', error));
    }

    setupEventListeners() {
        // Listen for quantity changes in bag
        document.querySelectorAll('.qty_input').forEach(input => {
            input.addEventListener('change', (e) => {
                const itemId = e.target.dataset.item_id;
                const size = e.target.dataset.size || 'default';
                const quantity = parseInt(e.target.value);
                
                // Update local bag quantities immediately
                if (!this.bagQuantities[itemId]) {
                    this.bagQuantities[itemId] = {};
                }
                this.bagQuantities[itemId][size] = quantity;
                
                // Update stock displays
                this.updateStockDisplays();

                // Update the bag via AJAX
                const form = e.target.closest('form');
                if (form) {
                    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                    const url = `/bag/adjust/${itemId}/`;
                    const formData = new FormData(form);

                    fetch(url, {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-CSRFToken': csrfToken,
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    })
                    .then(response => {
                        if (!response.ok) throw new Error('Network response was not ok');
                        // Refresh the page if quantity is 0
                        if (quantity === 0) window.location.reload();
                        // Otherwise update the subtotal
                        this.updateItemPrice(itemId);
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        window.location.reload(); // Reload on error to ensure consistency
                    });
                }
            });
        });

        // Listen for increment/decrement clicks
        document.querySelectorAll('.increment-qty, .decrement-qty').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const itemId = e.target.dataset.item_id;
                const qtyInput = document.querySelector(`#id_qty_${itemId}`);
                if (qtyInput) {
                    const currentValue = parseInt(qtyInput.value);
                    const isIncrement = e.target.classList.contains('increment-qty');
                    const newValue = isIncrement ? currentValue + 1 : currentValue - 1;
                    
                    if (newValue >= parseInt(qtyInput.min) && newValue <= parseInt(qtyInput.max)) {
                        qtyInput.value = newValue;
                        qtyInput.dispatchEvent(new Event('change'));
                    }
                }
            });
        });

        // Listen for add to bag clicks
        document.querySelectorAll('.add-to-bag').forEach(button => {
            button.addEventListener('click', (e) => this.validateStockBeforeSubmit(e));
        });

        // Listen for size changes if applicable
        const sizeSelector = document.querySelector('#id_product_size');
        if (sizeSelector) {
            sizeSelector.addEventListener('change', () => this.updateStockDisplays());
        }

        // Listen for remove item clicks
        document.querySelectorAll('.remove-item').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const itemId = e.target.closest('.remove-item').dataset.item_id;
                const size = e.target.closest('.remove-item').dataset.size || 'default';
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                
                // Update local bag quantities immediately
                if (this.bagQuantities[itemId]) {
                    if (size === 'default') {
                        delete this.bagQuantities[itemId];
                    } else {
                        delete this.bagQuantities[itemId][size];
                        if (Object.keys(this.bagQuantities[itemId]).length === 0) {
                            delete this.bagQuantities[itemId];
                        }
                    }
                }

                // Send remove request
                const url = `/bag/remove/${itemId}/`;
                const data = new FormData();
                data.append('csrfmiddlewaretoken', csrfToken);
                if (size !== 'default') data.append('product_size', size);

                fetch(url, {
                    method: 'POST',
                    body: data,
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => {
                    if (!response.ok) throw new Error('Network response was not ok');
                    // Remove the item row from the table
                    const row = e.target.closest('tr');
                    if (row) row.remove();
                    // Update stock displays
                    this.updateStockDisplays();
                    // Update grand total
                    this.updateTotalPrice();
                    // Reload if bag is empty
                    const bagItems = document.querySelectorAll('.bag-items tr');
                    if (bagItems.length === 0) window.location.reload();
                })
                .catch(error => {
                    console.error('Error:', error);
                    window.location.reload(); // Reload on error to ensure consistency
                });
            });
        });

        // Stock adjustment buttons
        document.querySelectorAll('.adjust-stock').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const productId = button.dataset.productId;
                const action = button.dataset.action;
                const input = button.closest('.stock-actions').querySelector('.stock-input');
                const quantity = parseInt(input.value);

                if (!quantity || quantity < 0) {
                    this.showToast('Please enter a valid quantity', 'error');
                    return;
                }

                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

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
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        throw new Error(data.error);
                    }
                    // Update the displayed quantities
                    const row = button.closest('tr');
                    row.querySelector('.stock-qty').textContent = data.stock_qty;
                    row.querySelector('.reserved-qty').textContent = data.reserved_qty;
                    row.querySelector('.available-qty').textContent = data.available_qty;
                    input.value = 0; // Reset input

                    // Show success message
                    const actionText = action === 'add' ? 'added to' : 'removed from';
                    this.showToast(`Successfully ${actionText} stock: ${quantity} items`, 'success');
                })
                .catch(error => {
                    this.showToast(error.message || 'Error adjusting stock', 'error');
                    console.error('Error:', error);
                });
            });
        });

        // Add toast display method if it doesn't exist
        if (!this.showToast) {
            this.showToast = (message, type = 'info') => {
                const toast = document.createElement('div');
                toast.className = `toast toast-${type}`;
                toast.textContent = message;
                
                const container = document.getElementById('toast-container');
                if (!container) {
                    const newContainer = document.createElement('div');
                    newContainer.id = 'toast-container';
                    document.body.appendChild(newContainer);
                }
                
                const toastContainer = document.getElementById('toast-container');
                toastContainer.appendChild(toast);
                
                setTimeout(() => {
                    toast.classList.add('show');
                    setTimeout(() => {
                        toast.classList.remove('show');
                        setTimeout(() => toast.remove(), 300);
                    }, 3000);
                }, 100);
            };
        }

        // Update stock when navigating back
        window.addEventListener('pageshow', (event) => {
            if (event.persisted) {
                // Page was loaded from cache (back/forward navigation)
                this.loadBagQuantities();
            }
        });
    }

    async updateStockDisplays() {
        const stockElements = document.querySelectorAll('[data-stock-qty]');
        stockElements.forEach(async (element) => {
            const productId = element.dataset.productId;
            if (productId) {
                await this.updateStockDisplay(element, productId);
            }
        });
    }

    async updateStockDisplay(element, productId) {
        try {
            const response = await fetch(`/products/stock/${productId}/`);
            if (!response.ok) throw new Error('Failed to fetch stock info');
            const data = await response.json();
            
            // The available_qty from the server already accounts for reserved quantities
            const actuallyAvailable = data.available_qty;
            
            // Update the display
            element.textContent = `${actuallyAvailable} in stock`;
            
            // Update visual indicators
            this.updateStockIndicators(element, actuallyAvailable);
            
            // Update quantity input max value if on product detail page
            const qtyInput = document.querySelector(`#id_qty_${productId}`);
            if (qtyInput) {
                qtyInput.max = actuallyAvailable;
                if (parseInt(qtyInput.value) > actuallyAvailable) {
                    qtyInput.value = actuallyAvailable;
                }
                // Update increment/decrement button states
                const itemId = qtyInput.dataset.item_id;
                if (itemId) {
                    this.handleEnableDisable(itemId);
                }
            }

            // Update add to bag button state
            const addToBagBtn = document.querySelector('.add-to-bag');
            if (addToBagBtn) {
                addToBagBtn.disabled = actuallyAvailable <= 0;
            }
        } catch (error) {
            console.error('Error updating stock display:', error);
        }
    }

    updateStockIndicators(element, quantity) {
        // Remove existing classes
        element.classList.remove('in-stock', 'low-stock', 'out-of-stock', 'high-stock', 'medium-stock');
        
        // Add appropriate class
        if (quantity <= 0) {
            element.classList.add('out-of-stock');
            element.closest('.product-item')?.classList.add('product-out-of-stock');
        } else if (quantity <= 5) {
            element.classList.add('low-stock');
            element.closest('.product-item')?.classList.add('product-low-stock');
        } else if (quantity <= 10) {
            element.classList.add('medium-stock');
            element.closest('.product-item')?.classList.remove('product-out-of-stock', 'product-low-stock');
        } else {
            element.classList.add('high-stock');
            element.closest('.product-item')?.classList.remove('product-out-of-stock', 'product-low-stock');
        }
    }

    handleEnableDisable(itemId) {
        const qtyInput = document.querySelector(`#id_qty_${itemId}`);
        if (!qtyInput) return;

        const currentValue = parseInt(qtyInput.value);
        const maxAvailable = parseInt(qtyInput.max);
        const minusDisabled = currentValue < 2;
        const plusDisabled = currentValue >= maxAvailable;

        const minusBtn = document.querySelector(`#decrement-qty_${itemId}`);
        const plusBtn = document.querySelector(`#increment-qty_${itemId}`);
        
        if (minusBtn) minusBtn.disabled = minusDisabled;
        if (plusBtn) plusBtn.disabled = plusDisabled;
    }

    validateStockBeforeSubmit(e) {
        const form = e.target.closest('form');
        const productId = form.querySelector('[name="product_id"]')?.value || form.querySelector('.qty_input')?.dataset.item_id;
        const quantity = parseInt(form.querySelector('[name="quantity"]').value);
        const size = form.querySelector('[name="product_size"]')?.value;

        if (!productId) return;

        const qtyInput = form.querySelector(`#id_qty_${productId}`);
        const maxAvailable = parseInt(qtyInput.max);

        if (quantity > maxAvailable) {
            e.preventDefault();
            alert('Sorry, there is not enough stock available for this quantity.');
        }
    }

    updateItemPrice(itemId) {
        const subtotalElement = document.querySelector(`#subtotal_${itemId}`);
        if (subtotalElement) {
            const qtyInput = document.querySelector(`#id_qty_${itemId}`);
            const priceElement = document.querySelector(`#price_${itemId}`);
            if (qtyInput && priceElement) {
                const quantity = parseInt(qtyInput.value);
                const price = parseFloat(priceElement.textContent);
                const subtotal = (quantity * price).toFixed(2);
                subtotalElement.textContent = subtotal;
                this.updateTotalPrice();
            }
        }
    }

    updateTotalPrice() {
        let total = 0;
        document.querySelectorAll('[id^="subtotal_"]').forEach(element => {
            total += parseFloat(element.textContent);
        });
        
        const grandTotal = document.querySelector('#grand_total');
        if (grandTotal) {
            grandTotal.textContent = total.toFixed(2);
        }

        const deliveryElement = document.querySelector('#delivery_cost');
        if (deliveryElement) {
            const deliveryCost = parseFloat(deliveryElement.textContent);
            const finalTotal = total + deliveryCost;
            const finalTotalElement = document.querySelector('#final_total');
            if (finalTotalElement) {
                finalTotalElement.textContent = finalTotal.toFixed(2);
            }
        }
    }
}

// Initialize stock management when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.stockManager = new StockManager();
});
