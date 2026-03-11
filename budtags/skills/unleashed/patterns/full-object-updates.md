# Full Object Updates - CRITICAL Pattern

The most important pattern to understand when working with the Unleashed API.

---

## The Rule

**The Unleashed API does NOT support partial updates.** When you send a PUT request, you MUST include ALL fields. Any field not included will be **overwritten with a blank value**, causing data loss.

This applies to ALL 13 editable resources.

---

## Safe Update Pattern

ALWAYS follow this GET -> Modify -> PUT cycle:

```php
public function update_customer(string $guid, array $changes): array
{
    // 1. GET the complete current object
    $response = $this->api->get("/Customers/{$guid}");
    $customer = $response->json();

    // 2. Merge your changes into the complete object
    $customer = array_merge($customer, $changes);

    // 3. PUT the complete object back
    $response = $this->api->put("/Customers/{$guid}", $customer);

    return $response->json();
}
```

---

## WRONG: Partial Update (DO NOT USE)

```php
// This DESTROYS all fields except CreditLimit!
$this->api->put("/Customers/{$guid}", [
    'CreditLimit' => 50000,
]);
// Result: CustomerName = blank, Email = blank, Addresses = gone, etc.
```

---

## Field Preservation Checklist

Before sending a PUT request, verify:

1. You fetched the current object with GET first
2. All existing fields are preserved in the request body
3. Only the intended fields are modified
4. Nested objects (Customer, Warehouse, Tax, etc.) are included
5. Array fields (SalesOrderLines, Addresses, etc.) are complete

---

## Known Exceptions

A few fields on certain resources explicitly state "null or missing property will not override existing information":

- **Products**: `MinimumOrderQuantity`, `MinimumSaleQuantity`, `MinimumSellPrice`
- **Customers**: `DeliveryInstruction`
- **Sales Orders**: `DeliveryInstruction`

These are documented exceptions. For all other fields, assume they WILL be blanked if missing.

---

## Resources This Applies To

All editable resources:
- Sales Orders
- Customers
- Products
- Stock Adjustments
- Purchase Orders
- Sales Shipments
- Credit Notes
- Supplier Returns
- Assemblies
- Bill of Materials
- Salespersons
- Warehouse Stock Transfers
- Attribute Sets

---

## Common Mistakes

1. **Building objects from scratch**: Always start from the GET response, never build a PUT body manually
2. **Removing unused fields**: Even if you don't need a field, keep it in the PUT body
3. **Ignoring nested objects**: The Customer, Warehouse, Currency objects must be preserved too
4. **Array truncation**: If an order has 10 lines, include all 10 in the PUT even if you only changed 1

---

## Best Practices

- ALWAYS: Fetch before update (GET -> Modify -> PUT)
- ALWAYS: Include all nested objects and arrays
- NEVER: Build a PUT request body from scratch
- NEVER: Remove fields from the response before sending it back
- CONSIDER: Implementing a generic `safe_update()` method in your API service class
- CONSIDER: Adding a test that compares field counts before/after update
