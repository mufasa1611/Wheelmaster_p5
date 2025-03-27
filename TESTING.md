# Table of Contents

1. [Testing Overview](#testing-overview)
2. [Types of Testing](#types-of-testing)
   - [Category View Tests](#category-view-tests)  
   - [Category Hierarchy Tests](#category-hierarchy-tests)  
   - [Product Stock Tests](#product-stock-tests)
   - [Manual Testing](#manual-testing)
   - [Browser and Responsiveness Testing](#browser-and-responsiveness-testing)
   - [Security Testing](#security-testing)
   - [Validation](#validation)
   - [Lighthouse Report](#lighthouse-report)
   - [Integration Testing](#integration-testing)
   - [User Feedback](#user-feedback)
3. [Known Issues](#known-issues)

## Testing Overview

A variety of testing methods were implemented to ensure the functionality, usability, and security of the Wheelmaster e-commerce site. These tests covered both manual and automated testing approaches, as well as user feedback.

## Types of Testing

### Category View Tests

The "TestCategoryViews" test ensures that the product categories and their relationships are correctly handled in the navigation and filtering logic.

- Setup: 
  The setUp method creates a parent category and two child categories, along with corresponding products.

- Tests Included:

1. test_category_navigation:  
   Verifies that parent and child categories are properly structured and rendered in the navigation.  
   Ensures that the nested relationships are correctly displayed.

2. test_parent_category_filter:  
   Tests that filtering by the parent category displays all related products, including those from child categories.

3. test_child_category_filter: 
   Checks that filtering by a child category only displays the corresponding products.

4. test_inactive_category:  
   Ensures that inactive categories do not appear in navigation or product listings.  
   Verifies that attempts to access inactive categories result in a redirect.

- How to Run the Tests:
python manage.py test products

### Category Hierarchy Tests

The "TestCategoryHierarchy" class validates the integrity of the category hierarchy and related behaviors.

- Setup:  
  The setUp method creates a parent category and two child categories to establish the category hierarchy.

- Tests Included:

1. test_parent_child_relationship:  
   Confirms that the parent-child relationships are correctly established.  
   Verifies that the parent category has the correct children and the child categories correctly reference their parent.

2. test_active_status:  
   Ensures that the "is_active" status flag affects the category hierarchy correctly.  
   Deactivating a parent category or child category reflects accurately in the active count and display logic.

3. test_friendly_name_formatting:  
   Checks that the "get_friendly_name" method returns the expected formatted names for both parent and child categories.

- How to Run the Tests:
python manage.py test products

### Product Stock Tests

The "ProductStockTests" class ensures that stock quantity management behaves as expected.

- Setup:  
  The "setUp" method creates a product with an initial stock quantity.

- Tests Included:

1. test_initial_stock:  
   Confirms the initial stock quantity is correctly set.

2. test_reduce_stock:  
   Validates that stock quantity reduces correctly when a valid quantity is reduced.

3. test_negative_stock_prevention:  
   Ensures that stock cannot be reduced below zero and raises an error if attempted.

4. test_add_stock:  
   Verifies that stock can be correctly increased.

5. test_zero_quantity:  
   Ensures that attempting to reduce the stock by zero raises an appropriate error.

6. test_invalid_quantity_type:  
   Checks that passing an invalid type (like a string) to the reduce method raises an error.

7. test_stock_status:  
   Tests the reporting of stock status (e.g., "In Stock", "Low Stock", "Out of Stock") based on the current stock quantity.
- How to Run the Tests:
python manage.py test products

### Manual Testing

Manual testing was performed to simulate real-world usage of the site and identify usability issues.

Key areas tested:

- Navigation and Usability:
  - Ensured the site is easy to navigate and that users can easily browse, search, and filter products.
  - Confirmed that the product pages display accurate product information, including descriptions and images.

- User Authentication:
  - Checked how the site handles invalid login attempts and password recovery.
  - Verified smooth user authentication for registration and login processes.

- Shopping Cart and Checkout:
  - Added various products to the cart, adjusted quantities, and tested the checkout process.
  - Ensured the checkout page displays the correct summary, including shipping and total cost.

- Error Handling:
  - Checked how the site responds to errors, such as attempting to add more items to the cart than are in stock.
  - Verified the correct handling of 404 pages for missing pages and products.

### Browser and Responsiveness Testing

The site was tested across various browsers and devices to ensure it is fully responsive and works well across all screen sizes.

- Browsers Tested:
  - Google Chrome, Safari, Microsoft Edge

- Devices Tested:
  - Desktop (Windows)
  - Tablets (iPad, Android)
  - Mobile devices (Android)

- Key issues addressed:
  - Ensured that the layout is responsive, with all elements properly resizing for smaller screens.

### Security Testing

- User Authentication & Authorization:
  Ensured that unauthorized users cannot access admin or sensitive pages.

- Payment Security:
  The checkout process was tested to ensure secure payment processing through Stripe.

### Validation

#### HTML

- HTML was validated using the [Markup Validation Service](https://validator.w3.org/) and returned mostly trailing slashes, but unfortunately I have not had the time to check all the .html pages.

#### CSS

- CSS was validated using the [CSS Validation Service](https://jigsaw.w3.org/css-validator/) and two minor errors were found and fixed.

![CSS Error report](media\images\css_errors.PNG)

![CSS last report](media\images\css_afterfix.PNG)

#### JavaScript

 JavaScript was validated using [JSHint](https://jshint.com/). I checked

- bag.js
- btn.js
- delete_edit.js
- main.js
- main-nav.js
- stock_management.js
- utils.js

and only found warnings, no errors.

#### Lighthouse Testing

- Lighthouse desktop homepage:
![Lighthouse mobile homepage](media\images\lighthouse_desktop.PNG)

- Lighthouse mobile homepage:
![Lighthouse mobile homepage](media\images\lighthouse_mobile.PNG)

#### Python Testing
I used the built-in Python testing library to test the backend functionality of the application, but have not had the time to run all tests with pep8 or similar checker.

### Integration Testing
Integration tests were performed to ensure that all components of the site interact as expected.

- Database Integration:
  Verified that data flows correctly between the front-end and back-end, ensuring proper functionality for adding products to the cart, processing orders, and saving customer information.

- Payment Gateway:
  Tested the integration with Stripe to ensure payments are processed smoothly and that orders are recorded properly in the database.

### User Feedback
After testing, user feedback was gathered from potential customers (friends, family) to identify any usability issues or areas of confusion.

### Known Issues
No significant issues were found during testing. Minor UI adjustments were made based on user feedback.
