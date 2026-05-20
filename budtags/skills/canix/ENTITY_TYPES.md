# Canix Entity Types — TypeScript Reference

TypeScript type definitions for all Canix API v1.3.5 entities. Use these when building frontend components that consume Canix data.

---

## Core Types

```typescript
// Shared primitives
type CanixId = number;
type CanixTimestamp = string; // ISO 8601: "2018-11-06T08:00:00.000Z"
type CanixDate = string;     // "2021-06-07"

interface CanixAddress {
    street: string;
    street2?: string;
    city: string;
    county?: string;
    state: string;
    country?: string;
    postal_code: string;
}

interface CanixIdName {
    id: number;
    name: string;
}

interface CanixUser {
    id: number;
    name: string;
    email: string;
}

interface CanixRecordCount {
    count: number;
}
```

---

## Sales Domain

```typescript
interface CanixSalesOrder {
    id: CanixId;
    facility_id: CanixId;
    name: string;
    external_identifier?: string;
    status: CanixSalesOrderStatus;
    display_status?: string;
    customer: CanixCustomer;
    delivery_date: CanixTimestamp;
    delivery_fee?: number;
    payment_date?: CanixTimestamp;
    payment_terms?: string;
    local_tax_rate: number;
    state_tax_rate: number;
    other_tax_rate: number;
    subtotal?: number;
    total_cultivation_tax?: number;
    total_price?: number;
    total_paid?: number;
    credits?: number;
    discount?: number;
    remaining_balance?: number;
    internal_notes?: string;
    contents?: CanixSalesOrderItem[];
    payments?: CanixSalesOrderPayment[];
    sales_representative?: CanixUser;
    sales_order_credit?: CanixDiscount;
    invoice_url?: string;
    created_at: CanixTimestamp;
    updated_at: CanixTimestamp;
}

type CanixSalesOrderStatus =
    | 'created' | 'approved' | 'filled' | 'shipped'
    | 'rejected' | 'accepted' | 'archived' | 'requested' | 'canceled';

interface CanixSalesOrderItem {
    id: CanixId;
    weight: number;
    weight_unit: string | number;
    weight_unit_id?: number;
    weight_unit_name?: string;
    unit_price?: number;
    total_price: number;
    item: CanixSalesOrderItemRef;
    package_ids?: number[];
    discount?: CanixDiscount;
    updated_at: CanixTimestamp;
    order?: number;
}

interface CanixSalesOrderItemRef {
    id: CanixId;
    name: string;
    sku?: string;
}

interface CanixSalesOrderPayment {
    amount: number;
    date: CanixTimestamp;
}

interface CanixDiscount {
    type: 'fixed' | 'percentage';
    amount: number;
    reason?: string;
}

interface CanixSalesOrderRequestBody {
    customer_id: number;
    name: string;
    external_identifier?: string;
    status: string;
    delivery_date: string;
    delivery_fee?: number;
    payment_date?: string;
    payment_terms?: string;
    local_tax_rate: number;
    state_tax_rate: number;
    other_tax_rate: number;
    internal_notes?: string;
    sales_rep_email?: string;
    return_policy?: string;
    terms_and_conditions?: string;
    sales_order_credit?: CanixDiscount;
    contents?: CanixSalesOrderContentInput[];
    payments?: CanixPaymentInput[];
}

interface CanixSalesOrderContentInput {
    item_id?: number;
    non_cannabis_product_id?: number;
    total_price: number;
    weight: number;
    weight_unit: string;
    notes?: string;
    package_ids?: number[];
    discount?: CanixDiscount;
}

interface CanixPaymentInput {
    amount: number;
    date: string;
    reference_number?: string;
}
```

---

## Purchasing Domain

```typescript
interface CanixPurchaseOrder {
    id: CanixId;
    facility_id: CanixId;
    name: string;
    status: CanixPurchaseOrderStatus;
    vendor: CanixVendor;
    requested_delivery_date: CanixTimestamp;
    internal_notes?: string;
    payment_terms: string;
    payment_date?: CanixDate;
    delivery_fee?: number;
    local_tax_rate: number;
    state_tax_rate: number;
    other_tax_rate: number;
    subtotal?: number;
    total_price?: number;
    total_paid?: number;
    contents?: CanixPurchaseOrderItem[];
    payments?: CanixPurchaseOrderPayment[];
    created_at: CanixTimestamp;
    updated_at: CanixTimestamp;
}

type CanixPurchaseOrderStatus =
    | 'CREATED' | 'RELEASED' | 'REQUESTED' | 'PARTIALLY_RECEIVED'
    | 'RECEIVED' | 'PAID' | 'ARCHIVED';

interface CanixPurchaseOrderItem {
    id: CanixId;
    weight: number;
    weight_unit: string;
    total_price: number;
    item?: CanixItem;
    non_cannabis_product?: CanixNonCannabisProduct;
}

interface CanixPurchaseOrderPayment {
    amount: number;
    date: CanixDate;
}
```

---

## CRM Domain

```typescript
interface CanixCustomer {
    id: CanixId;
    contact_name?: string;
    company_name?: string;
    facility_license_number?: string;
    license_type?: string;
    customer_number?: string;
    license_expiration_date?: CanixDate;
    phone?: string;
    email?: string;
    territory?: string;
    address?: CanixAddress;
    notes?: string;
    outstanding_balance?: number;
    dba?: string;
    is_active?: boolean;
    updated_at: CanixTimestamp;
}

interface CanixCustomerExtended extends CanixCustomer {
    outstanding_balance: number;
}

interface CanixVendor {
    id: CanixId;
    name: string;
    is_active?: boolean;
    contact_name?: string;
    email?: string;
    phone?: string;
    license_number?: string;
    license_expiration_date?: CanixTimestamp;
    address?: string;
    address2?: string;
    city?: string;
    postal_code?: string;
    state?: string;
    country?: string;
    website_url?: string;
    notes?: string;
    min_lead_time?: { value: number; unit: string };
    updated_at: CanixTimestamp;
}
```

---

## Products Domain

```typescript
interface CanixItem {
    id: CanixId;
    name: string;
    is_active?: boolean;
    item_type?: string;
    brand?: CanixIdName;
    quantity_type?: string;
    sku?: string;
    current_standard_cost?: CanixItemStandardCost;
    accounting_inventory_type?: string;
    notes?: string;
    facility_id: CanixId;
    strain?: CanixStrain;
    type?: CanixItemType;
    sub_type?: CanixItemSubType;
    weight_unit?: string;
    unit_weight?: number;
    unit_weight_unit?: string;
    case_quantity?: string;
    case_quantity_unit?: string;
    unit_cbd_weight?: number;
    unit_cbd_weight_unit?: string;
    unit_thc_weight?: number;
    unit_thc_weight_unit?: string;
    unit_cbd_percent?: number;
    unit_thc_percent?: number;
    description?: string;
    serving_size?: number;
    number_of_doses?: number;
    public_ingredients?: string;
    supply_duration_days?: number;
    administration_method?: string;
    allergens?: string;
    transfer_source_license?: string;
    phenotype?: string;
    total_for_sale?: number;
    ordered?: number;
    backordered?: number;
    unordered?: number;
    bills_of_materials?: Array<{ url: string; name: string; package_weight: number; unit: string }>;
    sage_item?: { external_id: string; name: string };
    leaflink_item?: { external_id: string; name: string } | null;
    dutchie_product?: { external_id: string; name: string } | null;
    updated_at: CanixTimestamp;
}

interface CanixItemType {
    id: CanixId;
    name: string;
    quantity_type?: string;
    requires_strain?: boolean;
    requires_unit_volume?: boolean;
    requires_unit_weight?: boolean;
    requires_unit_thc_weight?: boolean;
    requires_unit_cbd_weight?: boolean;
    requires_unit_cbd_percent?: boolean;
    requires_unit_thc_percent?: boolean;
    requires_public_ingredients?: boolean;
    requires_administration_method?: boolean;
    requires_serving_size?: boolean;
    requires_supply_duration_days?: boolean;
    requires_number_of_doses?: boolean;
    updated_at: CanixTimestamp;
}

interface CanixItemSubType {
    id: CanixId;
    name: string;
    weight_unit: string;
    category?: CanixItemType;
    updated_at: CanixTimestamp;
}

interface CanixBrand {
    id: CanixId;
    name: string;
    updated_at: CanixTimestamp;
}

interface CanixItemStandardCost {
    id: CanixId;
    standard_cost_amount: number;
    standard_cost_currency: string;
    start_date: CanixDate;
    end_date?: CanixDate;
}

interface CanixNonCannabisProduct {
    id: CanixId;
    name: string;
    is_active?: boolean;
    facilities?: CanixFacility[];
    category?: CanixNonCannabisProductCategory;
    location?: CanixLocation;
    sku?: string;
    notes?: string;
    available_quantity?: number;
    weight_unit?: string;
    par?: number;
    current_standard_costing?: CanixItemStandardCost;
    submits_to_metrc?: boolean;
    additive_type?: string;
    product_trade_name?: string;
    epa_registration_name?: string;
    product_supplier?: string;
    application_device?: string;
    active_ingredients?: Array<{ name: string; percentage: number }>;
    updated_at: CanixTimestamp;
}

interface CanixNonCannabisProductCategory {
    id: CanixId;
    name: string;
    updated_at: CanixTimestamp;
}
```

---

## Cultivation Domain

```typescript
interface CanixStrain {
    id: CanixId;
    name: string;
    notes?: string;
    sku?: string;
    testing_status?: 'InHouse' | 'ThirdParty' | 'None' | 'NA';
    indica_percent?: number;
    sativa_percent?: number;
    cross_strains?: CanixCrossStrain[];
}

interface CanixCrossStrain {
    id: CanixId;
    name: string;
    notes?: string;
    sku?: string;
    testing_status?: string;
    indica_percent?: number;
    sativa_percent?: number;
}

interface CanixPlantBatch {
    id: CanixId;
    name: string;
    mature_count?: number;
    immature_count?: number;
    vegetative_count?: number;
    flowering_count?: number;
    destroyed_count?: number;
    source?: string;
    planted_date?: CanixTimestamp;
    notes?: string;
    strain?: CanixStrain;
    location?: CanixLocation;
    lot_id?: string;
    updated_at: CanixTimestamp;
}

interface CanixPlant {
    id: CanixId;
    tag: string;
    plant_batch?: CanixPlantBatch;
    weight?: number;
    weight_unit?: string;
    growth_phase?: string;
    state?: string;
    strain?: CanixStrain;
    location?: CanixLocation;
    planted_date?: CanixTimestamp;
    vegetative_date?: CanixTimestamp;
    flowering_date?: CanixTimestamp;
    harvested_date?: CanixTimestamp;
    destroyed_date?: CanixTimestamp;
    notes?: string;
    age_in_days?: number;
    harvest?: CanixHarvest;
    lot_id?: string;
    updated_at: CanixTimestamp;
}

interface CanixHarvest {
    id: CanixId;
    name: string;
    strain?: CanixStrain;
    drying_location?: CanixLocation;
    harvest_date?: CanixTimestamp;
    plant_count?: number;
    average_plant_weight?: number;
    waste_weight?: number;
    total_wet_weight?: number;
    total_packaged_weight?: number;
    finished_date?: CanixTimestamp;
    package_count?: number;
    notes?: string;
    lot_id?: string;
    updated_at: CanixTimestamp;
}
```

---

## Inventory Domain

```typescript
interface CanixPackage {
    id: CanixId;
    tag: string;
    is_active: boolean;
    status: string;
    item?: CanixItem;
    weight: number;
    original_weight?: number;
    weight_unit: string;
    packaged_date?: CanixDate;
    production_batch_date?: CanixDate;
    expiration_date?: CanixDate;
    received_date?: CanixDate;
    location?: CanixLocation;
    production_batch?: string;
    lot_id?: string;
    cultivation_tax?: number;
    available_for_sale?: boolean;
    cannabis_cogs?: number;
    non_cannabis_inventory_cogs?: number;
    cogs?: { labor: number; non_cannabis: number; cannabis: number; total: number };
    source_packages?: CanixSourcePackage[];
    destination_packages?: CanixDestinationPackage[];
    source_facility?: string;
    source_facility_name?: string;
    source_harvests?: string;
    notes?: string;
    brand?: CanixBrand;
    lab_test_url?: string;
    coa_url?: string | null;
    lab_test_info?: CanixLabTestInfo;
    tested_package_tag?: string;
    test_status?: string;
    test_date?: CanixDate;
    test_results?: CanixTestResults;
    updated_at: CanixTimestamp;
}

interface CanixSourcePackage {
    id: CanixId;
    tag: string;
    weight: number;
    weight_unit: string;
    item?: CanixIdName;
}

interface CanixDestinationPackage {
    id: CanixId;
    tag: string;
    weight: number;
    weight_unit: string;
    item?: CanixIdName;
}

interface CanixTestResultValue {
    value: number;
    measure: 'mg' | 'mg/g' | 'mg/serving' | 'percent';
}

interface CanixTestResults {
    thc?: CanixTestResultValue[];
    cbd?: CanixTestResultValue[];
    cbn?: CanixTestResultValue[];
    cbg?: CanixTestResultValue[];
    cbga?: CanixTestResultValue[];
    cbc?: CanixTestResultValue[];
    cbca?: CanixTestResultValue[];
    cbda?: CanixTestResultValue[];
    thca?: CanixTestResultValue[];
    delta_8_thc?: CanixTestResultValue[];
    delta_9_thc?: CanixTestResultValue[];
    delta_9_thca?: CanixTestResultValue[];
    delta_8_thca?: CanixTestResultValue[];
    thcv?: CanixTestResultValue[];
    thcva?: CanixTestResultValue[];
    total_cbd?: CanixTestResultValue[];
    total_cbg?: CanixTestResultValue[];
    total_delta_9_thc?: CanixTestResultValue[];
    total_thc?: CanixTestResultValue[];
    total_cannabinoid?: CanixTestResultValue[];
    test_status?: string;
    tested_package_tag?: string;
    test_date?: CanixDate;
    terpenes?: CanixTerpeneResults;
}

interface CanixTerpeneResults {
    measure: string;
    top_three: Record<string, string>;
    values: Record<string, string>; // 28+ individual terpenes
}

interface CanixLabTestInfo {
    testing_facility_name: string;
    testing_facility_license: string;
}

interface CanixLocation {
    id: CanixId;
    name: string;
    sqft?: number;
    num_lights?: number;
    parent_location?: CanixParentLocation;
    is_active?: boolean;
    updated_at: CanixTimestamp;
}

interface CanixParentLocation {
    id: CanixId;
    name: string;
    sqft?: number;
    num_lights?: number;
    is_active?: boolean;
    updated_at: CanixTimestamp;
}

interface CanixWeightUnit {
    id: CanixId;
    name: string;
    abbreviation: string;
}
```

---

## Manufacturing Domain

```typescript
interface CanixManuBatch {
    id: CanixId;
    name?: string;
    template_name?: string;
    status?: string;
    current_location?: string;
    start_date?: CanixDate;
    end_date?: CanixDate;
    created_at: CanixTimestamp;
    updated_at: CanixTimestamp;
    notes?: string;
    manufacturing_run_ids: number[];
}

interface CanixManuBatchRun {
    id: CanixId;
    facility_id: CanixId;
    name: string;
    status: 'OPEN' | 'SUBMITTED' | 'SUBMITTED_FOR_APPROVAL' | 'ERRORED';
    start_date?: CanixDate;
    end_date?: CanixDate;
    created_at: CanixTimestamp;
    updated_at: CanixTimestamp;
    location_id?: CanixId;
    bill_of_materials_id?: CanixId;
    manufacturing_batch_id: CanixId;
    order: number;
    notes?: string;
    total_cannabis_costs?: number;
    total_labor_costs?: number;
    total_nci_costs?: number;
    yield?: number;
    machine_info?: CanixMachineInfo;
    cannabis_inputs?: CanixCannabisInput[];
    non_cannabis_inputs?: CanixNonCannabisInput[];
    cannabis_outputs?: CanixCannabisOutput[];
    labors?: CanixLabor[];
    wastes?: CanixWaste[];
}

interface CanixMachineInfo {
    temperature?: number;
    temperature_unit?: 'Celcius' | 'Fahrenheit';
    solvent_id?: number;
    solvent_quantity?: number;
    solvent_weight_unit?: string;
    time_in_solvent_ms?: number;
    time_in_solvent_display_units?: 'Week' | 'Day' | 'Hour' | 'Minute' | 'Second';
}

interface CanixCannabisInput {
    package_id?: number;
    package_tag?: string;
    quantity: number;
    weight_unit: string;
    psi?: number;
    cost?: number;
}

interface CanixNonCannabisInput {
    non_cannabis_product_name: string;
    non_cannabis_product_id: number;
    lot?: string;
    lot_id?: number;
    quantity: number;
    weight_unit: string;
    cost?: number;
}

interface CanixCannabisOutput {
    package_id?: number;
    package_tag?: string;
    quantity: number;
    weight_unit: string;
}

interface CanixLabor {
    employee_name?: string;
    hours_worked: number;
    cost?: number;
}

interface CanixWaste {
    package_id: number;
    package_tag: string;
    quantity: number;
    weight_unit: string;
    reason?: string;
    date?: CanixDate;
    notes?: string;
}

interface CanixBillOfMaterials {
    id: CanixId;
    name: string;
    active_date?: CanixDate;
    expiration_date?: CanixDate;
    proportion_type: 'single_instance' | 'all_instances';
    last_updated_at?: CanixTimestamp;
    source_non_cannabis_products?: CanixBomNciSource[];
    source_cannabis_items?: CanixBomCannabisSource[];
    output_items?: CanixBomOutputItem[];
}

interface CanixBomNciSource {
    non_cannabis_product_id: number;
    name: string;
    quantity: number;
    weight_unit: string;
    application_setting: 'proportional' | 'fixed';
}

interface CanixBomCannabisSource {
    quantity: number;
    weight_unit: string;
    item?: CanixIdName | null;
    item_category?: CanixIdName | null;
    item_sub_category?: CanixIdName | null;
}

interface CanixBomOutputItem {
    name: string;
    item_id: number;
    quantity: number;
    weight_unit: string;
}
```

---

## Logistics & System Domain

```typescript
interface CanixTransfer {
    id: CanixId;
    name?: string;
    manifest_number?: string;
    is_active?: boolean;
    destinations?: CanixTransferDestination[];
    sales_order?: CanixSalesOrder;
    updated_at: CanixTimestamp;
}

interface CanixTransferDestination {
    id: CanixId;
    destination_facility?: string;
    transfer_type?: string;
    route?: string;
    departure_time?: CanixTimestamp;
    contents?: CanixPackageTransfer[];
    updated_at: CanixTimestamp;
}

interface CanixPackageTransfer {
    package: CanixPackage;
    status?: string;
    sale_price?: number;
    shipped_weight?: number;
    shipped_weight_unit?: string;
    received_weight?: number;
    received_weight_unit?: string;
    updated_at: CanixTimestamp;
}

interface CanixCompany {
    id: CanixId;
    name: string;
    created_at: CanixTimestamp;
    updated_at: CanixTimestamp;
}

interface CanixFacility {
    id: CanixId;
    name: string;
    license_number?: string;
    is_active?: boolean;
    address?: CanixAddress;
}

interface CanixSubmission {
    uuid: string;
    status: CanixSubmissionStatus;
    readable_name?: string;
    description?: string;
    error_message?: string;
    result?: Record<string, unknown> | null;
    created_at: CanixTimestamp;
    last_run_at?: CanixTimestamp | null;
}

type CanixSubmissionStatus =
    | 'CREATED' | 'PENDING_APPROVAL' | 'PENDING' | 'RETRYING'
    | 'FAILED' | 'SUCCESS' | 'DENIED' | 'ABORTED' | 'PARTIAL_FAILURE';

interface CanixAuditedAction {
    facility_id: CanixId;
    object_id: number;
    object_type: string;
    object_tag?: string;
    context: string[];
    description: string;
    submitted_date?: CanixTimestamp;
    approval_date?: CanixTimestamp;
    created_at: CanixTimestamp;
    updated_at: CanixTimestamp;
}
```
