# Plant Batches Category

**Collection File**: `collections/metrc-plantbatches.postman_collection.json`
**Total Endpoints**: 20
**License Compatibility**: ⚠️ **CULTIVATION LICENSES ONLY** (AU-C-######)

---

## ⚠️ CRITICAL WARNING

**Plant batch endpoints are ONLY accessible to Cultivation licenses.**
Non-cultivation licenses will receive 401/403 errors.

---

## GET Endpoints (6 endpoints)

- `GET /plantbatches/v2/{id}` - Get plant batch by ID
- `GET /plantbatches/v2/active` - Get active plant batches
- `GET /plantbatches/v2/inactive` - Get inactive plant batches
- `GET /plantbatches/v2/types` - Get plant batch types (Clone, Seed, etc.)
- `GET /plantbatches/v2/waste` - Get plant batch waste records
- `GET /plantbatches/v2/waste/reasons` - Get waste reasons for plant batches

---

## POST Endpoints

### Batch Operations

- `POST /plantbatches/v2/createplantings` - Create plantings from batch
  - Use case: Plant seeds/clones, track as individual plants

- `POST /plantbatches/v2/createpackages` - Create packages from plant batch
  - Use case: Package clones for sale/transfer

- `POST /plantbatches/v2/packages/frommotherplant` - Create packages from mother plants
  - Use case: Create clone packages from mother plants

- `POST /plantbatches/v2/split` - Split plant batches
  - Use case: Separate batch into smaller groups

- `POST /plantbatches/v2/additives` - Record additives on plant batches
  - Use case: Log fertilizer/pesticide applications

---

## PUT Endpoints (7 endpoints)

- `PUT /plantbatches/v2/moveplantbatches` - Move plant batches to new location
- `PUT /plantbatches/v2/changegrowthphase` - Change growth phase
- `PUT /plantbatches/v2/destroy` - Destroy plant batches
- `PUT /plantbatches/v2/tag` - Replace plant batch tags
- `PUT /plantbatches/v2/rename` - Rename a plant batch
  - Use case: Correct naming errors or update batch naming convention
- `PUT /plantbatches/v2/strain` - Change plant batch strain
  - Use case: Correct strain assignment errors

---

## Related

- `categories/plants.md` - Individual plant management
- `patterns/license-types.md` - License compatibility details
