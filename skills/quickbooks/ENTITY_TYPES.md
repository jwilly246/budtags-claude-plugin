# QuickBooks Entity Types Reference

TypeScript type definitions for all QuickBooks entities used in BudTags.

**Source:** `resources/js/Types/types-qbo.tsx`

---

## Core Entity Types

### Customer

Customer entity with address and contact information.

```typescript
interface Customer {
    Id: string;
    DisplayName: string;
    CompanyName?: string;
    GivenName?: string;
    MiddleName?: string;
    FamilyName?: string;
    PrimaryPhone?: Phone;
    PrimaryEmailAddr?: Email;
    BillAddr?: Address;
    ShipAddr?: Address;
    Balance?: number;
    Active?: boolean;
    MetaData?: MetaData;
}
```

**Key Fields:**
- `Id` - QuickBooks customer ID
- `DisplayName` - Customer display name
- `CompanyName` - Company/business name
- `GivenName` / `FamilyName` - First/last name
- `PrimaryPhone` - Phone object
- `PrimaryEmailAddr` - Email object
- `BillAddr` / `ShipAddr` - Address objects
- `Balance` - Current account balance
- `Active` - Is customer active?

**API Operations:**
- `get_customer(id)`
- `get_customers()`
- `get_all_customers()`
- `update_customer(data)`

---

### Invoice

Invoice with line items, customer, totals, and dates.

```typescript
interface Invoice {
    Id: string;
    DocNumber: string;
    TxnDate: string;
    DueDate?: string;
    CustomerRef: {
        value: string;
        name: string;
    };
    Line: OrderLineItem[];
    TotalAmt: number;
    Balance: number;
    EmailStatus?: string;
    BillEmail?: Email;
    BillAddr?: Address;
    CustomerMemo?: {
        value: string;
    };
    PrivateNote?: string;
    SalesTermRef?: {
        value: string;
    };
    DepositToAccountRef?: {
        value: string;
    };
    MetaData?: MetaData;
}
```

**Key Fields:**
- `DocNumber` - Invoice number (e.g., "1001")
- `TxnDate` - Invoice date
- `DueDate` - Payment due date
- `CustomerRef` - Customer reference {value: ID, name: Name}
- `Line` - Array of line items
- `TotalAmt` - Total invoice amount
- `Balance` - Remaining balance (TotalAmt - payments)
- `EmailStatus` - "EmailSent" | "NotSet" | etc.

**API Operations:**
- `create_invoice(data)`
- `update_invoice(data)`
- `get_invoice(id)`
- `get_invoices()`
- `send_invoice(id, email)`
- `download_invoice_pdf(id)`

---

### OrderLineItem

Line item within an invoice or credit memo.

```typescript
interface OrderLineItem {
    Id?: string;
    LineNum?: number;
    Amount: number;
    Description?: string;
    DetailType: string;
    SalesItemLineDetail?: {
        ItemRef: {
            value: string;
            name: string;
        };
        Qty?: number;
        UnitPrice?: number;
        TaxCodeRef?: {
            value: string;
        };
    };
}
```

**Key Fields:**
- `Amount` - Line total (Qty × UnitPrice)
- `Description` - Line item description
- `DetailType` - Usually "SalesItemLineDetail"
- `SalesItemLineDetail.ItemRef` - Item reference
- `SalesItemLineDetail.Qty` - Quantity
- `SalesItemLineDetail.UnitPrice` - Unit price

**Usage:**
```typescript
const lineItem: OrderLineItem = {
    Amount: 250.00,
    Description: 'Premium Cannabis Flower - 1oz',
    DetailType: 'SalesItemLineDetail',
    SalesItemLineDetail: {
        ItemRef: {
            value: '456',
            name: 'Cannabis Flower 1oz'
        },
        Qty: 10,
        UnitPrice: 25.00
    }
};
```

---

### Company

QuickBooks company information.

```typescript
interface Company {
    CompanyName: string;
    LegalName?: string;
    CompanyAddr?: Address;
    CustomerCommunicationAddr?: Address;
    LegalAddr?: Address;
    PrimaryPhone?: Phone;
    CompanyStartDate?: string;
    FiscalYearStartMonth?: string;
    Country?: string;
    Email?: Email;
    WebAddr?: {
        URI: string;
    };
    SupportedLanguages?: string;
    NameValue?: Array<{
        Name: string;
        Value: string;
    }>;
    domain?: string;
    sparse?: boolean;
    Id?: string;
    SyncToken?: string;
    MetaData?: MetaData;
}
```

**Key Fields:**
- `CompanyName` - Company display name
- `LegalName` - Legal business name
- `CompanyAddr` - Company address
- `Email` - Company email
- `PrimaryPhone` - Company phone

**API Operation:**
- `get_company_info()`

---

### PaymentMethod

Payment method reference (Cash, Check, Credit Card, etc.).

```typescript
interface PaymentMethod {
    Id: string;
    Name: string;
    Active?: boolean;
    Type?: string;
}
```

**Common Payment Methods:**
- Cash (ID: "1")
- Check (ID: "2")
- Credit Card (ID: "3")
- Debit Card (ID: "4")

**API Operations:**
- `get_payment_methods()`
- `get_payment_method(id)`

---

### Account

Chart of Accounts entry.

```typescript
interface Account {
    Id: string;
    Name: string;
    AccountType: string;
    AccountSubType?: string;
    Active?: boolean;
    CurrentBalance?: number;
    Classification?: string;
    MetaData?: MetaData;
}
```

**Account Types:**
- `Bank` - Bank accounts
- `Income` - Income/revenue accounts
- `Expense` - Expense accounts
- `Asset` - Asset accounts
- `Liability` - Liability accounts
- `Equity` - Equity accounts

**API Operations:**
- `get_accounts()`
- `get_all_accounts()`
- `get_account(id)`
- `get_deposit_accounts()` - Bank accounts only

---

## Supporting Types

### Address

Physical address structure.

```typescript
interface Address {
    Line1?: string;
    Line2?: string;
    Line3?: string;
    Line4?: string;
    Line5?: string;
    City?: string;
    Country?: string;
    CountrySubDivisionCode?: string;  // State code
    PostalCode?: string;
    Lat?: string;
    Long?: string;
    Id?: string;
}
```

**Usage:**
```typescript
const address: Address = {
    Line1: '123 Main St',
    City: 'Los Angeles',
    CountrySubDivisionCode: 'CA',
    PostalCode: '90001'
};
```

---

### Phone

Phone number structure.

```typescript
interface Phone {
    FreeFormNumber: string;
}
```

**Usage:**
```typescript
const phone: Phone = {
    FreeFormNumber: '(555) 123-4567'
};
```

---

### Email

Email address structure.

```typescript
interface Email {
    Address: string;
}
```

**Usage:**
```typescript
const email: Email = {
    Address: 'customer@example.com'
};
```

---

### MetaData

Entity metadata (timestamps, version).

```typescript
interface MetaData {
    CreateTime: string;      // ISO 8601 timestamp
    LastUpdatedTime: string; // ISO 8601 timestamp
}
```

**Example:**
```typescript
{
    CreateTime: '2025-01-15T10:30:00-08:00',
    LastUpdatedTime: '2025-01-20T14:45:00-08:00'
}
```

---

## Usage Examples

### Creating Invoice with Typed Data

```typescript
import { Invoice, OrderLineItem } from '@/Types/types-qbo';

const lineItems: OrderLineItem[] = [
    {
        Amount: 250.00,
        Description: 'Premium Cannabis Flower - 1oz',
        DetailType: 'SalesItemLineDetail',
        SalesItemLineDetail: {
            ItemRef: { value: '456', name: 'Flower 1oz' },
            Qty: 10,
            UnitPrice: 25.00
        }
    }
];

const invoiceData = {
    customer_id: '123',
    txn_date: '2025-01-15',
    line_items: lineItems.map(item => ({
        item_id: item.SalesItemLineDetail.ItemRef.value,
        quantity: item.SalesItemLineDetail.Qty,
        unit_price: item.SalesItemLineDetail.UnitPrice,
        description: item.Description
    }))
};

// Submit to backend
router.post('/quickbooks/create-invoice', invoiceData);
```

---

### Using Customer Type in Component

```typescript
import { Customer } from '@/Types/types-qbo';

interface Props {
    customers: Customer[];
}

const CustomerList: React.FC<Props> = ({ customers }) => {
    return (
        <div>
            {customers.map(customer => (
                <div key={customer.Id}>
                    <h3>{customer.DisplayName}</h3>
                    <p>{customer.PrimaryEmailAddr?.Address}</p>
                    <p>{customer.PrimaryPhone?.FreeFormNumber}</p>
                    <p>Balance: ${customer.Balance?.toFixed(2)}</p>
                </div>
            ))}
        </div>
    );
};
```

---

## Type Imports

**Always import from types-qbo.tsx:**

```typescript
import {
    Customer,
    Invoice,
    Company,
    PaymentMethod,
    Account,
    OrderLineItem,
    Address,
    Phone,
    Email,
    MetaData
} from '@/Types/types-qbo';
```

**Never duplicate type definitions** - always use the centralized types file.

---

## API Response Matching

All QuickBooks API responses match these TypeScript types exactly. QuickBooks uses PascalCase for all field names, which is preserved in our types.

**Example API Response:**
```json
{
    "Id": "123",
    "DisplayName": "Acme Dispensary",
    "PrimaryEmailAddr": {
        "Address": "acme@example.com"
    },
    "Balance": 1250.50
}
```

**Maps directly to Customer type without transformation.**

---

## Next Steps

- **[OPERATIONS_CATALOG.md](OPERATIONS_CATALOG.md)** - See which operations return which types
- **[CODE_EXAMPLES.md](CODE_EXAMPLES.md)** - Real code examples using these types
- **[WORKFLOWS/](WORKFLOWS/)** - Workflow guides with type usage examples
