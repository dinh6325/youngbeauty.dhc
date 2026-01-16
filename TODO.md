# TODO List for E-commerce Features

## Cart Product Selection Feature
- [x] Update shop/templates/shop/cart.html: Add checkboxes for each product to allow selection, add form to submit selected products to checkout.
- [x] Update shop/views.py cart_view: Handle POST request with selected product IDs, filter cart to selected items, redirect to checkout with selected items.
- [x] Update shop/views.py checkout: Accept selected items from session or POST, process only selected products for order creation.

## PayOS Payment Success Redirect
- [x] Update payments/views.py payment_success: Extract order_id from PayOS response (e.g., from GET parameters), redirect to shop:order_tracking with order_id.

## Testing and Follow-up
- [ ] Test cart selection functionality: Add multiple products to cart, select some, proceed to checkout, verify only selected are processed.
- [ ] Test PayOS payment flow: Complete payment, ensure redirect to order tracking page.
- [ ] Ensure stock reduction only for selected/purchased products.
- [ ] Check for any regressions in cart, checkout, and payment flows.
