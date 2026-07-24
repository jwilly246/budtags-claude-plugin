# QuickBooks Entity Types Reference

TypeScript type definitions for all QuickBooks entities used in BudTags.

**Source:** `resources/js/Types/types-qbo.tsx`

---

> The file uses `export type X = {...}`, not `interface`. QuickBooks returns nearly every field as a **string** (including numeric-looking values like `Balance`, `TotalAmt`, `UnitPrice`), so the types are string-heavy on purpose. Cast to number in the UI when you need arithmetic. The large entities (`QBCustomer`, `Invoice`, `Company`) mirror the full QBO entity; the blocks below show the load-bearing subset - consult the source for the complete field list.

---

## Reference Helper Types

### QBRef

QuickBooks reference field. The API inconsistently returns refs as either a bare string ID or an object.

```typescript
export type QBRef = string | { value: string, name?: string };
```

Used by `CustomerRef`, `ItemRef`, `ParentRef`, `IncomeAccountRef`, etc. Always narrow before reading `.value`.

### OverdueLevel / OverdueStatus

Client-computed overdue classification for a customer (not a QBO field).

```typescript
export type OverdueLevel = 'none' | 'overdue' | 'severely_overdue';

export type OverdueStatus = {
    level: OverdueLevel,
    daysOverdue: number,
    amount: number,
};
```

---

## Core Entity Types

### QBCustomer

Customer entity with address and contact information. (~80 fields in source; key subset shown.)

```typescript
export type QBCustomer = {
    Id: string,
    SyncToken: string,
    MetaData: MetaData,
    GivenName?: string,
    MiddleName?: string,
    FamilyName?: string,
    FullyQualifiedName: string,
    CompanyName: string,
    DisplayName: string,
    Active: string,
    PrimaryPhone: Phone,
    AlternatePhone?: Phone | string,
    PrimaryEmailAddr: Email,
    Taxable?: string,
    BillAddr: QBAddress,
    ShipAddr: QBAddress,
    SalesTermRef: string,
    PaymentMethodRef: string,
    Balance: string,
    BalanceWithJobs: string,
    CurrencyRef: string,
    // ...full QBO Customer shape continues in source
};
```

**API Operations:** `get_customer(id)`, `get_customers()`, `get_all_customers()`, `get_customers_by_id(ids)`, `update_customer(customer)`

---

### Invoice

Invoice with line items, customer ref, totals, dates, and online-payment fields. (~100 fields in source; key subset shown.)

```typescript
export type Invoice = {
    Id: string,
    SyncToken: string,
    MetaData: MetaData,
    DocNumber: string,
    TxnDate: string,
    CustomerRef: QBRef,
    CustomerMemo: string,
    Line: QBOrderLineItem[],
    BillAddr: QBAddress,
    ShipAddr: QBAddress,
    SalesTermRef: string,
    DueDate: string,
    PrivateNote: string,
    TotalAmt: string,
    Balance: string,
    EmailStatus: string,
    BillEmail: Email,
    PaymentMethodRef: string,
    DepositToAccountRef: string,
    AllowOnlineCreditCardPayment: string,
    AllowOnlineACHPayment: string,
    InvoiceLink: string,
    // ...full QBO Invoice shape continues in source
};
```

**Key Fields:**
- `CustomerRef` - `QBRef` (string ID or `{value, name}`)
- `Line` - array of `QBOrderLineItem`
- `TotalAmt` / `Balance` - strings; parse for math
- `InvoiceLink` - QBO-hosted "Pay Online" URL; only populated when online payments are enabled on the invoice (see billing sync notes)

**API Operations:** `create_invoice(data)`, `update_invoice(invoice_id, data)`, `get_invoice(id)`, `get_invoices()`, `get_customer_invoices(customer_id)`, `get_overdue_invoices()`, `send_invoice(id, email)`, `download_invoice_pdf(id)`

---

### QBOrderLineItem

Line item within an invoice or credit memo. Intersected with `ItemMappingMeta` (from `./types`) for BudTags-side mapping metadata.

```typescript
export type QBOrderLineItem = {
    Id?: string,
    LineNum?: string,
    Description?: string,
    Amount?: string,
    LinkedTxn?: Transaction,
    DetailType?: string,
    SalesItemLineDetail?: SalesLineItemDetail,
    // ...other detail-type slots in source
} & ItemMappingMeta;

type SalesLineItemDetail = {
    ItemRef?: QBRef,
    ClassRef?: string,
    UnitPrice?: string,
    Qty?: string,
    TaxCodeRef?: string,
    ServiceDate?: string,
    // ...
};
```

**Key Fields:**
- `Amount` - line total (string)
- `DetailType` - usually `"SalesItemLineDetail"`
- `SalesItemLineDetail.ItemRef` - `QBRef`
- `SalesItemLineDetail.Qty` / `UnitPrice` - strings

---

### CreditMemo

Credit memo with remaining credit tracking.

```typescript
export type CreditMemo = {
    Id: string,
    SyncToken?: string,
    MetaData?: MetaData,
    DocNumber: string,
    TxnDate: string,
    CustomerRef: QBRef,
    RemainingCredit: string,
    Balance: string,
    TotalAmt: string,
    PrivateNote?: string,
    Line?: QBOrderLineItem[],
    CurrencyRef?: string,
    BillAddr?: QBAddress,
    PrintStatus?: string,
    EmailStatus?: string,
    domain?: string,
    status?: string,
    sparse?: string,
};
```

**API Operations:** `create_credit_memo(data)`, `get_credit_memos()`, `get_customer_credit_memos(customer_id)`, `get_customer_available_credits(customer_id)`, `apply_credit_to_invoice(...)`

---

### QuickBooksItem

Inventory/service item. Note the union types (`string | boolean`, `string | number`) reflecting QBO's inconsistent serialization.

```typescript
export type QuickBooksItem = {
    Id: string,
    Name: string,
    Type: string,
    ParentRef?: QBRef,
    FullyQualifiedName?: string,
    Sku?: string,
    Description?: string,
    Active: string | boolean,
    UnitPrice?: string,
    PurchaseCost?: string,
    QtyOnHand?: string | number,
    TrackQtyOnHand?: boolean,
    Taxable?: string | boolean,
    IncomeAccountRef?: QBRef,
    ExpenseAccountRef?: QBRef,
    AssetAccountRef?: QBRef,
};
```

**API Operations:** `create_item(data)`, `update_item(item_id, data)`, `update_item_quantity(item_id, qty)`, `get_items()`, `get_all_items()`, `get_items_cached(orgId)`, `delete_item(id)`, `sync_quantities_from_metrc(...)`

---

### Company

QuickBooks company information. (Key subset shown.)

```typescript
export type Company = {
    Id: string,
    SyncToken: string,
    MetaData: MetaData,
    CompanyName: string,
    LegalName: string,
    CompanyAddr: QBAddress,
    LegalAddr: QBAddress,
    CustomerCommunicationEmailAddr: Email,
    PrimaryPhone: string,
    CompanyStartDate: string,
    FiscalYearStartMonth: string,
    Country: string,
    Email: Email,
    WebAddr: string,
    SupportedLanguages: string,
    DefaultTimeZone: string,
    NameValue: NameValue[],
    // ...full QBO CompanyInfo shape continues in source
};

type NameValue = { Name: string, Value: string };
```

**API Operation:** `get_company_info()`

---

### QBPaymentMethod

Payment method reference (Cash, Check, Credit Card, etc.).

```typescript
export type QBPaymentMethod = {
    Id: string,
    Name: string,
    Active: string,
    Type: string,
};
```

**API Operations:** `get_payment_methods()`, `get_payment_method(id)`, `get_payment_methods_cached(orgId)`

---

### Account

Chart of Accounts entry.

```typescript
export type Account = {
    Id: string,
    Name: string,
    Active: string,
    AccountType: string,
    AccountSubType: string,
    CurrentBalance: string,
};
```

**API Operations:** `get_accounts()`, `get_all_accounts()`, `get_all_accounts_cached(orgId)`, `get_account(id)`, `get_deposit_accounts()` (Bank + Active only)

---

### Term

Payment term (net-15, net-30, etc.).

```typescript
export type Term = {
    Id: string,
    Name: string,
    DueDays: number | string,
    Active: boolean,
    Type?: string,
};
```

**API Operations:** `get_terms()`, `get_terms_cached(orgId)`

---

## Supporting Types

These are declared but not exported (used internally by the entity types above).

### QBAddress

```typescript
type QBAddress = {
    Id?: string,
    Line1: string,
    Line2?: string,
    Line3?: string,
    Line4?: string,
    Line5?: string,
    City: string,
    Country: string,
    CountryCode?: string,
    County?: string,
    CountrySubDivisionCode?: string,  // state code
    PostalCode: string,
    PostalCodeSuffix?: string,
    Lat?: string,
    Long?: string,
    Tag?: string,
    Note?: string,
};
```

### Phone

```typescript
type Phone = {
    Id?: string,
    DeviceType: string,
    CountryCode?: string,
    AreaCode?: string,
    ExchangeCode?: string,
    Extension?: string,
    FreeFormNumber: string,
    Default?: string,
    Tag?: string,
};
```

### Email

```typescript
type Email = {
    Id?: string,
    Address: string,
    Default?: string,
    Tag?: string,
};
```

### MetaData

```typescript
type MetaData = {
    CreatedByRef: string,
    CreateTime: string,
    LastModifiedByRef: string,
    LastUpdatedTime: string,
    LastChangedInQB: string,
    Synchronized: string,
};
```

`Transaction`, `TaxLine`, `TaxLineDetail`, `TransactionTaxInfo`, and `SalesLineItemDetail` are also declared internally for the invoice/line-item shapes.

---

## Billing Portal Types

These back the billing/overdue subsystem (see `patterns/billing-invoice-sync.md`). They are BudTags-native shapes, not raw QBO entities.

### QboInvoiceSnapshot

One cached invoice row, the shape `qbo:sync-invoices` writes into Redis and the billing page reads.

```typescript
export type QboInvoiceSnapshot = {
    qbo_invoice_id: string,
    qbo_customer_id: number,
    doc_number: string,
    total_amount: number,
    balance: number,
    due_date: string | null,
    txn_date: string | null,
    status: 'paid' | 'unpaid' | 'overdue' | 'voided',
    invoice_link?: string | null,
    synced_at: string,
};
```

The `status` union mirrors the PHP `InvoiceStatus` enum (`paid` / `unpaid` / `overdue` / `voided`).

### BillingStatus / FullBillingStatus

`BillingStatus` is used both by the billing settings page (full shape with invoices) and by the shared Inertia prop injected on every page (summary-only fields for banners). `FullBillingStatus` marks the billing-page fields required.

```typescript
export type BillingStatus = {
    // Billing page fields (present on /orgs/active/billing)
    total_owed?: number,
    invoice_count?: number,
    unpaid_count?: number,
    overdue_count?: number,
    payment_blocked?: boolean,
    payment_warning?: boolean,
    oldest_overdue_date?: string | null,
    invoices?: QboInvoiceSnapshot[],

    // Shared prop fields (present on every page via HandleInertiaRequests)
    is_overdue?: boolean,
    is_blocked?: boolean,
    days_overdue?: number,
    total_overdue?: number,
};

export type FullBillingStatus = Required<Pick<BillingStatus,
    'total_owed' | 'invoice_count' | 'unpaid_count' | 'overdue_count'
    | 'payment_blocked' | 'payment_warning' | 'oldest_overdue_date' | 'invoices'
>> & BillingStatus;
```

### InvoiceWithCustomerLicenses

Invoice enriched with the customer's license numbers for the QBO orders table.

```typescript
export type InvoiceWithCustomerLicenses = Invoice & {
    customer_licenses: string[],
};
```

---

## Type Imports

**Always import from `types-qbo.tsx` (never redefine):**

```typescript
import type {
    QBRef,
    QBCustomer,
    Invoice,
    QBOrderLineItem,
    CreditMemo,
    QuickBooksItem,
    Company,
    QBPaymentMethod,
    Account,
    Term,
    OverdueStatus,
    QboInvoiceSnapshot,
    BillingStatus,
    FullBillingStatus,
    InvoiceWithCustomerLicenses,
} from '@/Types/types-qbo';
```

> `Customer`, `OrderLineItem`, `PaymentMethod`, and `Address` are NOT exported names. Use `QBCustomer`, `QBOrderLineItem`, `QBPaymentMethod`, and `QBAddress` (internal).

---

## API Response Matching

QuickBooks uses PascalCase field names, preserved verbatim in these types. Remember that numeric-looking fields arrive as strings and refs arrive as `QBRef` (string OR object) - narrow before use.

**Example API Response:**
```json
{
    "Id": "123",
    "DisplayName": "Acme Dispensary",
    "PrimaryEmailAddr": { "Address": "acme@example.com" },
    "Balance": "1250.50"
}
```

**Maps directly to `QBCustomer` without transformation** (note `Balance` is a string).
