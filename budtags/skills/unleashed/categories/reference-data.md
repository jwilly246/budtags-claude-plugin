# Reference Data Category (Read-Only)

All read-only reference resources not covered by other category files.

---

## Accounts
- `GET /Accounts` - List chart of accounts

---

## Batch Numbers
- `GET /BatchNumbers` - List batch numbers

---

## Companies
- `GET /Companies` - List companies (no pagination)

---

## Currencies
- `GET /Currencies` - List currencies (no pagination)

### Fields
| Field | Type | Length |
|-------|------|--------|
| `Guid` | GUID | - |
| `CurrencyCode` | string | 3 |
| `Description` | string | 200 |
| `DefaultBuyRate` | decimal | - |
| `DefaultSellRate` | decimal | - |

---

## Serial Numbers
- `GET /SerialNumbers` - List serial numbers

---

## Taxes
- `GET /Taxes` - List tax codes

### Fields
| Field | Type | Length |
|-------|------|--------|
| `Guid` | GUID | - |
| `TaxCode` | string | 25 |
| `Description` | string | 50 |
| `TaxRate` | decimal | - |
| `CanApplyToExpenses` | boolean | - |
| `CanApplyToRevenue` | boolean | - |
| `Obsolete` | boolean | - |

---

## Unit of Measures
- `GET /UnitOfMeasures` - List units of measure

### Fields
| Field | Type | Length |
|-------|------|--------|
| `Guid` | GUID | - |
| `Name` | string | 20 |
| `Obsolete` | boolean | - |

---

## Suppliers
- `GET /Suppliers` - List suppliers

### Fields
| Field | Type | Length |
|-------|------|--------|
| `Guid` | GUID | - |
| `SupplierCode` | string | 500 |
| `SupplierName` | string | 500 |

---

## Other Reference Endpoints

- `GET /CustomerTypes` - List customer types
- `GET /DeliveryMethods` - List delivery methods
- `GET /PaymentTerms` - List payment terms
- `GET /ProductBrands` - List product brands
- `GET /ProductGroups` - List product groups
- `GET /ProductPrices` - List product prices
- `GET /SellPriceTiers` - List sell price tiers (no pagination)
- `GET /ShippingCompanies` - List shipping companies
- `GET /StockCounts` - List stock counts
- `GET /RecostAdjustments` - List recost adjustments
- `GET /SalesInvoices` - List sales invoices
- `GET /SalesQuotes` - List sales quotes
- `GET /SalesOrderGroups` - List sales order groups

---

## Usage Notes

- These endpoints return lookup/reference data used by editable resources
- Use these to populate dropdowns, validate inputs, or sync reference data
- Most support standard pagination (default 200)
- Exceptions without pagination: Currencies, Companies, SellPriceTiers
