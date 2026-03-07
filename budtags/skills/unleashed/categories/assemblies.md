# Assemblies & Bill of Materials Category

**Assembly Endpoints**: 9
**Operations**: Full CRUD + Complete + Line management
**Limitation**: Does NOT support batch or serial numbers via API

---

## Assembly Endpoints

- `GET /Assemblies` - List assemblies (paginated)
- `GET /Assemblies/{guid}` - Get single assembly
- `POST /Assemblies` - Create assembly with lines
- `POST /Assemblies/{guid}/Lines` - Add lines to existing assembly
- `POST /Assemblies/{guid}/Complete` - Complete assembly
- `PUT /Assemblies/{guid}` - Update assembly and lines
- `PUT /Assemblies/{guid}/Lines/{lineGuid}` - Update single line
- `DELETE /Assemblies/{guid}` - Delete parked assembly
- `DELETE /Assemblies/{guid}/Lines/{lineGuid}` - Delete line

### Assembly Filters
| Filter | Type | Description |
|--------|------|-------------|
| `assemblyNumber` | string | Retrieve by number |
| `assemblyStatus` | string | Filter by status (Parked, Completed) |
| `customAssemblyStatus` | string | Custom status (overrides standard) |
| `startDate` | date | Assemblies dated after |
| `endDate` | date | Assemblies dated before |
| `modifiedSince` | date | Modified since |

### Key Fields

| Field | Type | Required |
|-------|------|----------|
| `Product` | object | Required (must be assembled product type) |
| `Quantity` | decimal | Required (>0 for completion) |
| `Warehouse` | object | Required (Guid or WarehouseCode) |
| `AssemblyLines` | array | Required (min 1 line to complete) |
| `AssemblyDate` | datetime | Optional |
| `Comments` | string | Optional |

Duration fields accept human-readable strings: "6h 38s", "8000m"

---

## Bill of Materials Endpoints

- `GET /BillOfMaterials` - List BOMs (paginated)
- `GET /BillOfMaterials/{guid}` - Get single BOM
- `POST /BillOfMaterials` - Create BOM
- `PUT /BillOfMaterials/{guid}` - Update BOM
- `DELETE /BillOfMaterials/{guid}` - Delete BOM

### BOM Fields

| Field | Type | Required |
|-------|------|----------|
| `Product` | object | Required (assembled product) |
| `Components` | array | Required (component products and quantities) |

---

## Important Notes

- Batch and serial numbers must be entered manually via web UI, not supported via API
- Only parked assemblies can be deleted
- Blank fields on PUT overwrite previous values
