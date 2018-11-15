Feature: The shopcarts store service back-end
  As a Shopcart Service Owner
  I need a RESTful catalog service
  So that I can keep track of all shopcarts

Background:
  Given data for shopcart entries
    | product_id | user_id | quantity | price |
    | 1          | 1       | 1        | 10.00 |
    | 2          | 1       | 1        | 15.00 |
    | 1          | 2       | 1        | 10.00 |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Shopcarts REST API Service" in the title
    And I should not see "404 Not Found"

Scenario: Add a new product
    When I visit the "Home Page"
    And I set the "Product Id" to 1
    And I set the "User Id" to 3
    And I set the "Quantity" to 1
    And I set the "Price" to 11.00
    And I press the "Create" button
    Then I should see the message "Success"

Scenario: Add same product
    When I visit the "Home Page"
    And I set the "Product Id" to 1
    And I set the "User Id" to 1
    And I set the "Quantity" to 1
    And I set the "Price" to 10.00
    And I press the "Create" button
    Then I should see the message "Success"
    And I should see 2 in the "Quantity" field
