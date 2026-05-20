# Cultivation — Strains, Plant Batches, Plants, Harvests

Cultivation endpoints cover the grow-side of cannabis operations. Strains support CRUD; plant batches, plants, and harvests are read-only.

**Note for BudTags integration**: Plant batches, plants, and harvests overlap with Metrc data. These are typically skipped during import since Metrc is the source of truth for seed-to-sale tracking.

## Strain Endpoints (4 operations)

| Method | Path | Operation | Notes |
|--------|------|-----------|-------|
| GET | `/strains` | List active strains | Supports `facility_id` |
| POST | `/strains` | Create strain | ⚠️ WRITE |
| GET | `/strains/{id}` | Get single strain | Includes cross_strains |
| PUT | `/strains/{id}` | Update strain | ⚠️ WRITE (fewer fields than create) |

## Plant Batch Endpoints (2 operations)

| Method | Path | Operation | Notes |
|--------|------|-----------|-------|
| GET | `/plant_batches` | List active plant batches | Paginated, filterable |
| GET | `/plant_batches/{id}` | Get single plant batch | Counts, strain, location |

## Plant Endpoints (3 operations)

| Method | Path | Operation | Notes |
|--------|------|-----------|-------|
| GET | `/plants` | List active plants | Paginated, filterable |
| GET | `/plants/count` | Get total plant count | Supports `where` filter |
| GET | `/plants/{id}` | Get single plant | Full lifecycle data |

## Harvest Endpoints (2 operations)

| Method | Path | Operation | Notes |
|--------|------|-----------|-------|
| GET | `/harvests` | List active harvests | Paginated, filterable |
| GET | `/harvests/{id}` | Get single harvest | Weights, counts |

## Strain Schema

```json
{
  "id": 1,
  "name": "Lemon Skunk",
  "notes": "Terpenes .63%",
  "sku": "BIOJJ",
  "testing_status": "InHouse",
  "indica_percent": 45.0,
  "sativa_percent": 55.0,
  "cross_strains": [
    { "id": 2, "name": "Skunk #1", "notes": "...", "sku": "SK1", "testing_status": "ThirdParty", "indica_percent": 60.0, "sativa_percent": 40.0 }
  ]
}
```

### Key Strain Fields

- **`testing_status`** — One of: `InHouse`, `ThirdParty`, `None`, `NA`
- **`indica_percent`** / **`sativa_percent`** — Genetic percentages
- **`cross_strains`** — Array of related strains (same schema minus cross_strains)

## CreateStrainRequestBody

**Required fields**: `name` only.

```json
{
  "name": "Blue Dream",
  "facility_id": 123,
  "description": "A sativa-dominant hybrid",
  "genetics": "Blueberry x Haze",
  "active": true,
  "sku": "BD-001",
  "notes": "High-yield strain",
  "cbd_level": 0.5,
  "thc_level": 18.5,
  "indica_percent": 40.0,
  "sativa_percent": 60.0,
  "testing_status": "Tested",
  "cross_strain_ids": [456, 789]
}
```

**`facility_id`**: Must be a facility with standalone, CA METRC standalone, or METRC standalone integration.
**`cross_strain_ids`**: All cross strains must belong to the same facility.

## UpdateStrainRequestBody (Slimmer)

**Note**: The update body has fewer fields than create — no THC/CBD levels, no cross strains, no facility.

```json
{
  "name": "Blue Dream",
  "description": "A sativa-dominant hybrid",
  "genetics": "Blueberry x Haze",
  "active": true
}
```

## PlantBatch Schema

```json
{
  "id": 123,
  "name": "1A4FF0000000022000000719",
  "mature_count": 21,
  "immature_count": 2,
  "vegetative_count": 23,
  "flowering_count": 25,
  "destroyed_count": 5,
  "source": "Clone",
  "planted_date": "2018-11-06T08:00:00.000Z",
  "notes": "nice batch!",
  "strain": { ... },
  "location": { ... },
  "lot_id": "LOT-001",
  "updated_at": "2018-11-06T08:00:00.000Z"
}
```

## Plant Schema

```json
{
  "id": 123,
  "tag": "1A4FF0000000022000000719",
  "plant_batch": { ... },
  "weight": 2,
  "weight_unit": "Grams",
  "growth_phase": "Flowering",
  "state": "Tracked",
  "strain": { ... },
  "location": { ... },
  "planted_date": "2018-11-06T08:00:00.000Z",
  "vegetative_date": "2015-12-23T07:00:00.000Z",
  "flowering_date": "2016-04-18T06:00:00.000Z",
  "harvested_date": "2018-04-18T06:00:00.000Z",
  "destroyed_date": null,
  "notes": "nice plant!",
  "age_in_days": 2039,
  "harvest": { ... },
  "lot_id": "LOT-001",
  "updated_at": "2018-11-06T08:00:00.000Z"
}
```

### Plant Lifecycle Dates

| Field | Phase | Description |
|-------|-------|-------------|
| `planted_date` | Initial | When plant was planted |
| `vegetative_date` | Veg | When entered vegetative phase |
| `flowering_date` | Flower | When entered flowering phase |
| `harvested_date` | Harvest | When harvested |
| `destroyed_date` | End | When destroyed (nullable) |

## Harvest Schema

```json
{
  "id": 123,
  "name": "Offline Manicure",
  "strain": { ... },
  "drying_location": { ... },
  "harvest_date": "2018-11-06T08:00:00.000Z",
  "plant_count": 3,
  "average_plant_weight": 107.7,
  "waste_weight": 100,
  "total_wet_weight": 100,
  "total_packaged_weight": 100,
  "finished_date": "2018-11-06T08:00:00.000Z",
  "package_count": 100,
  "notes": "nice harvest!",
  "lot_id": "LOT-001",
  "updated_at": "2018-11-06T08:00:00.000Z"
}
```

## BudTags Mapping

### Strains
| Canix Field | BudTags Field | Model |
|-------------|---------------|-------|
| `id` | `canix_id` | Strain |
| `name` | `name` | Strain |
| `indica_percent` | `indica_percent` | Strain |
| `sativa_percent` | `sativa_percent` | Strain |

### Plants/Batches/Harvests — SKIPPED
These overlap with Metrc data stored in Redis. Metrc is the source of truth.

---

**See:** `categories/products-items.md` for items that reference strains
**See:** `patterns/facility-scoping.md` for facility_id filtering on strains
