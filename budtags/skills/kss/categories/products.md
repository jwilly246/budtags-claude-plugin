# Products

> Verbatim transcription of [https://kssdata.com/docs/v1#group-products](https://kssdata.com/docs/v1#group-products) (retrieved 2026-08-19). Field names, parameters, enum values, and example responses are copied exactly from the KSS docs. Do not edit by hand — regenerate from source.


## GET /productCategories

Doc anchor: [`#get-productCategories`](https://kssdata.com/docs/v1#get-productCategories)

**Badges:** Paginated

Returns all product categories ordered by sequence.

**Pagination:** Supports Page and PageSize query parameters. Default page size: 50. Maximum page size: 500 — larger values are reduced to 500.

### Example Response

**json**

```json
{
  "Data": [
    {
      "ProductCategoryID": 1,
      "CategoryName": "Chocolate",
      "Sequence": 1,
      "TimeUpdated": "2025-01-01T00:00:00.000Z"
    },
    {
      "ProductCategoryID": 2,
      "CategoryName": "Gummies",
      "Sequence": 2,
      "TimeUpdated": "2025-01-01T00:00:00.000Z"
    }
  ],
  "Page": 1,
  "PageSize": 50
}
```

---

## GET /products

Doc anchor: [`#get-products`](https://kssdata.com/docs/v1#get-products)

**Badges:** Paginated

Returns products filtered by supplier, state, product ID, and status.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `SupplierIDs` | query | `number[]` | optional | Comma-separated list of supplier IDs to filter by. |
| `ProductIDs` | query | `number[]` | optional | Comma-separated list of product IDs to filter by. When provided, status filtering is skipped. |
| `States` | query | `string[]` | optional | Comma-separated list of state abbreviations to filter by. Example: "CA,NJ". |
| `Statuses` | query | `number[]` | optional | Comma-separated list of product status IDs. Defaults to Active (1). Ignored when ProductIDs is provided.<br>Values: `0` = Discontinued, `1` = Active, `2` = Pre-order, `3` = Manufacture, `4` = Unavailable, `5` = Close Out |
| `SupplierProductNumbers` | query | `string[]` | optional | Comma-separated list of supplier product numbers to filter by. Matches exactly. |

**Pagination:** Supports Page and PageSize query parameters. Default page size: 50. Maximum page size: 500 — larger values are reduced to 500.

### Example Response

**json**

```json
{
  "Data": [
    {
      "ProductID": 160,
      "Supplier": "Kiva",
      "SupplierID": 5,
      "ProductName": "Bar Dark Chocolate",
      "BrandFamily": "Kiva Bars",
      "ProductTypeName": "Edible - Chocolate",
      "UnitNetWeight": "50g",
      "WholesaleUnitsPerCase": 20,
      "Description": "Our classic Dark Chocolate bar is uniquely complex with flavors of black coffee and dark cherry. Using a 57% sustainably sourced dark chocolate infused with pure, clean cold water hash, this bar is sure to delight any true chocolate lover.Kiva chocolates are crafted from sustainably sourced, premium cacao infused with pure, hand-crafted cold water hash. Since 2010, Kiva's mission has been to change how the world views and uses cannabis. By applying art and science to ensure a delicious, consistent experience every time, we continue to deliver on that mission today.",
      "Ingredients": "Semisweet Chocolate (Unsweetened Chocolate, Sugar, Cocoa Butter, Sunflower Lecithin, Vanilla), Cannabis Extract.",
      "ThumbnailImageURL": "https://cdn.e8.co/Kiva/S3Images/256a66c67e050f86201a863c2103a71d.png",
      "FullSizeImageURL": "https://cdn.e8.co/Kiva/S3Images/67d10e54dd3c94a702b78a722bdd1aa8.png",
      "Potency": "100mg THC",
      "PotencyTHC": null,
      "Blend": "Hybrid",
      "KSSMenuCategory": "Edibles/Ingestibles",
      "KSSLiveCategoryID": 1,
      "StatusID": 1,
      "TimeUpdated": "2026-02-12T19:51:57.510Z",
      "State": "CA",
      "IsSample": false,
      "ProductGroupID": 3,
      "BrandStyle": "Kiva Bar",
      "PackageID": 15,
      "PackageName": "20 Kiva Bar",
      "ProductTypeID": 57,
      "StrainName": null,
      "StrainID": null,
      "Flavor": "dark",
      "BrandID": 2624,
      "BrandName": "Kiva Bars Base",
      "SupplierProductNumber": "KIVA-BAR-DARK-50"
    },
    {
      "ProductID": 161,
      "Supplier": "Kiva",
      "SupplierID": 5,
      "ProductName": "Bar Milk Chocolate",
      "BrandFamily": "Kiva Bars",
      "ProductTypeName": "Edible - Chocolate",
      "UnitNetWeight": "50g",
      "WholesaleUnitsPerCase": 20,
      "Description": "Meticulously crafted from the purest ingredients, Kiva's classic milk chocolate bar has hints of brown butter and a silky, creamy finish. Like all Kiva chocolates, this bar is crafted from sustainably sourced, premium cacao infused with handmade, cold water cannabis hash. Ideal for those with a love for chocolate and a refined palate.Kiva chocolates are crafted from sustainably sourced, premium cacao infused with pure, hand-crafted cold water hash. Since 2010, Kiva's mission has been to change how the world views and uses cannabis. By applying art and science to ensure a delicious, consistent experience every time, we continue to deliver on that mission today.",
      "Ingredients": "Milk Chocolate (Sugar, Cocoa Butter, Milk, Unsweetened Chocolate, Sunflower Lecithin, Vanilla), Cannabis Extract.",
      "ThumbnailImageURL": "https://cdn.e8.co/Kiva/S3Images/79ad65dc9c579f53b2de75ea8b183194.png",
      "FullSizeImageURL": "https://cdn.e8.co/Kiva/S3Images/9ab227940b12546b120ed1a5386f759c.png",
      "Potency": "100mg THC",
      "PotencyTHC": null,
      "Blend": "Hybrid",
      "KSSMenuCategory": "Edibles/Ingestibles",
      "KSSLiveCategoryID": 1,
      "StatusID": 1,
      "TimeUpdated": "2026-02-12T19:51:57.510Z",
      "State": "CA",
      "IsSample": false,
      "ProductGroupID": 3,
      "BrandStyle": "Kiva Bar",
      "PackageID": 15,
      "PackageName": "20 Kiva Bar",
      "ProductTypeID": 57,
      "StrainName": null,
      "StrainID": null,
      "Flavor": "milk",
      "BrandID": 2624,
      "BrandName": "Kiva Bars Base",
      "SupplierProductNumber": "KIVA-BAR-MILK-50"
    }
  ],
  "Page": 1,
  "PageSize": 50
}
```

---

## GET /products/:productID

Doc anchor: [`#get-products--productID`](https://kssdata.com/docs/v1#get-products--productID)

Returns a single product by ID.

### Parameters

| Name | In | Type | Required | Description |
|---|---|---|---|---|
| `productID` | path | `number` | required | The ID of the product to retrieve. |

### Example Response

**json**

```json
{
  "Data": [
    {
      "ProductID": 160,
      "Supplier": "Kiva",
      "SupplierID": 5,
      "ProductName": "Bar Dark Chocolate",
      "BrandFamily": "Kiva Bars",
      "ProductTypeName": "Edible - Chocolate",
      "UnitNetWeight": "50g",
      "WholesaleUnitsPerCase": 20,
      "Description": "Our classic Dark Chocolate bar is uniquely complex with flavors of black coffee and dark cherry. Using a 57% sustainably sourced dark chocolate infused with pure, clean cold water hash, this bar is sure to delight any true chocolate lover.Kiva chocolates are crafted from sustainably sourced, premium cacao infused with pure, hand-crafted cold water hash. Since 2010, Kiva's mission has been to change how the world views and uses cannabis. By applying art and science to ensure a delicious, consistent experience every time, we continue to deliver on that mission today.",
      "Ingredients": "Semisweet Chocolate (Unsweetened Chocolate, Sugar, Cocoa Butter, Sunflower Lecithin, Vanilla), Cannabis Extract.",
      "ThumbnailImageURL": "https://cdn.e8.co/Kiva/S3Images/256a66c67e050f86201a863c2103a71d.png",
      "FullSizeImageURL": "https://cdn.e8.co/Kiva/S3Images/67d10e54dd3c94a702b78a722bdd1aa8.png",
      "Potency": "100mg THC",
      "PotencyTHC": null,
      "Blend": "Hybrid",
      "KSSMenuCategory": "Edibles/Ingestibles",
      "KSSLiveCategoryID": 1,
      "StatusID": 1,
      "TimeUpdated": "2026-02-12T19:51:57.510Z",
      "State": "CA",
      "IsSample": false,
      "ProductGroupID": 3,
      "BrandStyle": "Kiva Bar",
      "PackageID": 15,
      "PackageName": "20 Kiva Bar",
      "ProductTypeID": 57,
      "StrainName": null,
      "StrainID": null,
      "Flavor": "dark",
      "BrandID": 2624,
      "BrandName": "Kiva Bars Base",
      "SupplierProductNumber": "KIVA-BAR-DARK-50"
    }
  ]
}
```
