# Inventory

> Verbatim transcription of [https://kssdata.com/docs/v1#group-inventory](https://kssdata.com/docs/v1#group-inventory) (retrieved 2026-08-19). Field names, parameters, enum values, and example responses are copied exactly from the KSS docs. Do not edit by hand — regenerate from source.


## GET /inventory

Doc anchor: [`#get-inventory`](https://kssdata.com/docs/v1#get-inventory)

**Badges:** Not available to Customer keys · Paginated

Returns warehouse inventory records filtered by supplier, product, location, and state. AvailableUnits = OnFloorInventory - PreSales - Allocations

> **Callout:** The NotAuthorized field signifies that all of this product is reserved for specific accounts. Refer to the Allocations endpoint for details

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `SupplierIDs` | query | `number[]` | optional | Comma-separated list of supplier IDs to filter by. |
| `ProductIDs` | query | `number[]` | optional | Comma-separated list of product IDs to filter by. |
| `LocationIDs` | query | `number[]` | optional | Comma-separated list of location IDs to filter by. |
| `States` | query | `string[]` | optional | Comma-separated list of state abbreviations to filter by. Example: "CA,NJ". |

**Pagination:** Supports Page and PageSize query parameters. Default page size: 50. Maximum page size: 500 — larger values are reduced to 500.

### Field Definitions

| Field | Description |
|---|---|
| `Inventory` | Sum of all other columns except Pre-Sales, Allocated, and Available. This number represents the total inventory owned. |
| `Loaded` | Total inventory that has been loaded onto trucks for delivery. |
| `Picked` | Total inventory that has been picked, but not yet Loaded. |
| `Delivered` | Total inventory that has been delivered, but is still on Load Sheets in the Loaded Status. |
| `Unsellable` | Total inventory in the warehouse that is not flagged as sellable. |
| `OnFloorInventory` | Total inventory in the warehouse that is sellable. |
| `PreSales` | Total inventory that is on future dated orders and not yet picked or loaded. |
| `Allocated` | Inventory that has been specifically "set aside" using allocations, and is therefore not universally available. |
| `AvailableUnits` | On Floor - Pre-Sales and Allocated. |
| `Received` | Total inventory that has been received and not yet put in on floor or unsellable. |
| `NotAuthorized` | If true this product is not generally available. Only specifically authorized accounts can purchase this product. |
| `PurchaseTransID` | The Purchase Transaction ID of the current FIFO layer that is being sold. The inventory values can be the sum of multiple purchase transactions. Not just the one that is being sold. |

### Example Response

**json**

```json
{
  "Data": [
    {
      "LocationID": 1,
      "ProductID": 5001,
      "OnFloorInventory": "1239.00",
      "PreSales": "110.00",
      "Allocated": "0.00",
      "NotAuthorized": false,
      "AvailableUnits": 1129,
      "PurchaseTransID": 7537244,
      "DOI": "5.60",
      "AvgDailySales90d": "201.49",
      "Inventory": "1239.00",
      "Received": "1500.00",
      "Loaded": "0.00",
      "Picked": "0.00",
      "Delivered": "261.00",
      "Unsellable": "0.00",
      "TimeUpdated": "2026-02-24T17:06:10.610Z"
    },
    {
      "LocationID": 1,
      "ProductID": 5002,
      "OnFloorInventory": "1939.00",
      "PreSales": "180.00",
      "Allocated": "0.00",
      "NotAuthorized": false,
      "AvailableUnits": 1759,
      "PurchaseTransID": 7537282,
      "DOI": "3.77",
      "AvgDailySales90d": "466.83",
      "Inventory": "1939.00",
      "Received": "2100.00",
      "Loaded": "0.00",
      "Picked": "0.00",
      "Delivered": "161.00",
      "Unsellable": "0.00",
      "TimeUpdated": "2026-02-24T17:06:10.610Z"
    }
  ],
  "Page": 1,
  "PageSize": 50
}
```

---

## GET /inventory/batches

Doc anchor: [`#get-inventory-batches`](https://kssdata.com/docs/v1#get-inventory-batches)

**Badges:** Not available to Customer keys · Paginated

Returns warehouse inventory broken out by batch, including batch codes, potency, and compliance dates. Filtered by supplier, product, location, state, and batch code.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `SupplierIDs` | query | `number[]` | optional | Comma-separated list of supplier IDs to filter by. |
| `ProductIDs` | query | `number[]` | optional | Comma-separated list of product IDs to filter by. |
| `LocationIDs` | query | `number[]` | optional | Comma-separated list of location IDs to filter by. |
| `States` | query | `string[]` | optional | Comma-separated list of state abbreviations to filter by. Example: "CA,NJ". |
| `BatchCodes` | query | `string[]` | optional | Comma-separated list of batch codes to filter by. Matches exactly. |

**Pagination:** Supports Page and PageSize query parameters. Default page size: 50. Maximum page size: 500 — larger values are reduced to 500.

### Example Response

**json**

```json
{
  "Data": [
    {
      "LocationID": 1,
      "ProductID": 5001,
      "SupplierID": 5,
      "State": "CA",
      "InventoryUnits": 1239,
      "PurchaseTransID": 7537244,
      "ExpirationDate": "2026-12-31",
      "COAURL": "https://cdn.e8.co/Kiva/COA/1234abcd.pdf",
      "BatchCode": "KIVA-240115-A",
      "Vintage": null,
      "UID": "1A4060300012345000000001",
      "Laboratory": "SC Labs",
      "BestByDate": "2026-11-30",
      "HarvestDate": null,
      "ManufactureDate": "2024-01-15",
      "PackDate": "2024-01-16",
      "COAExpirationDate": "2026-01-15",
      "PotencyType": "PerServing",
      "THCPotency": "5.00",
      "CBDPotency": "0.00",
      "TotalCannabinoids": "5.00",
      "LabelTHCPotency": "5.00",
      "LabelCBDPotency": "0.00",
      "LabelTotalCannabinoids": "5.00",
      "TimeCreated": "2024-01-16T08:00:00.000Z",
      "TimeUpdated": "2026-02-24T17:06:10.610Z"
    }
  ],
  "Page": 1,
  "PageSize": 50
}
```

---

## GET /retailerInventory

Doc anchor: [`#get-retailerInventory`](https://kssdata.com/docs/v1#get-retailerInventory)

**Badges:** Paginated

Returns retailer-level inventory records filtered by customer, supplier, product, and state.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `CustomerIDs` | query | `number[]` | optional | Comma-separated list of customer IDs to filter by. |
| `SupplierIDs` | query | `number[]` | optional | Comma-separated list of supplier IDs to filter by. |
| `ProductIDs` | query | `number[]` | optional | Comma-separated list of product IDs to filter by. |
| `States` | query | `string[]` | optional | Comma-separated list of state abbreviations to filter by. Example: "CA,NJ". |

**Pagination:** Supports Page and PageSize query parameters. Default page size: 50. Maximum page size: 500 — larger values are reduced to 500.

### Example Response

**json**

```json
{
  "Data": [
    {
      "ID": 1690421,
      "ProductID": 160,
      "CustomerID": 1,
      "LastInventoryDate": "2025-05-20T06:00:00.000Z",
      "Inventory": "20.00",
      "DailySales": "0.03",
      "TimeUpdated": "2025-06-02T21:31:05.941Z"
    },
    {
      "ID": 1706440,
      "ProductID": 161,
      "CustomerID": 1,
      "LastInventoryDate": "1999-12-31T07:00:00.000Z",
      "Inventory": "0.00",
      "DailySales": "0.03",
      "TimeUpdated": "2025-06-17T15:46:14.397Z"
    }
  ],
  "Page": 1,
  "PageSize": 50
}
```
