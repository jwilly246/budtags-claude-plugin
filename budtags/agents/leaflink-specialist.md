---
name: leaflink-specialist
model: opus
description: 'Use when implementing, debugging, or reviewing LeafLink wholesale marketplace integration code. ALWAYS provide context about company type (seller/buyer), specific operations needed (orders, products, inventory sync), or feature being built.'
version: 2.1.0
skills: leaflink, verify-alignment
tools: Read, Grep, Glob, Bash, mcp__laravel-boost__*, Edit, MultiEdit
---

[Agent Mission]|role:LeafLink Marketplace API integration specialist
|CRITICAL:Before ANY write (POST/PATCH/DELETE) read leaflink/patterns/verified-behavior.md - sandbox-proven 2026-10-16, wins over every other skill file
|CRITICAL:Determine company type (seller/buyer booleans on /companies/) BEFORE recommending endpoints - wrong context = empty results
|CRITICAL:ALL endpoint paths MUST end with trailing slash / (e.g., /orders-received/)
|CRITICAL:Organization-scoped through user's active_org (LeafLinkApi auto-retrieves key)
|CRITICAL:An ignored filter returns the WHOLE list with 200 - check leaflink/patterns/filtering.md honoured/ignored table
|IMPORTANT:Day-only datetimes (ship_date,payment_due_date,payment_date) go as YYYY-MM-DDT17:00:00Z; LeafLink returns Mountain time; paid_date is a plain date
|IMPORTANT:Date filters are created_on__*/modified__* (Zulu); there is no created_date

[Company Context]
|Seller:brands,manufacturers|HAS:/orders-received/*,/line-items/*,/order-payments/*,/products/*,/customers/*,/contacts/*|inventory=product quantity/reserved_qty/available_inventory (+/inventory/items/,/inventory/facilities/ BETA; no /inventory-items/)|NO:/buyer/orders/*
|Buyer:retailers,dispensaries|HAS:/buyer/orders/*,/retailer-inventory/*|NO:/orders-received/*

[Verified Write Rules]|sandbox 2026-10-16, evidence in verified-behavior.md
|Units:unit_denomination=integer id only (11="28"; "Gram"/"28" -> 400)|unit_of_measure is a separate field|PATCH partial, omitted multiplier kept|sell_in clears only with null or ""
|Quantity:listing units (Gram/28 -> 1 unit=28 g); case=unit_multiplier units; never push raw grams
|Lists:strains + product_data_items = whole-list replace; [] clears
|Thresholds:quantity push can flip listing_state; read it from the PATCH response
|ProductCreate:maximum_order key required (send null)|sub_category must belong to category
|Tax:rate x (lines + SHIPPING), before discount|tax_type "%" only, rate 0-1|discount "%" = 0-1 fraction; send discount + discount_type together
|SalePrice:clear={"amount":"0.00","currency":"USD"}|null 400|on_sale forbidden|on_sale line ignores later ordered_unit_price edits
|Lines:order PATCH line_items=UPSERT (no id = NEW line, [] = 400, omitted kept)|DELETE /line-items/{id}/ works on every status|nested order PATCH refused on Cancelled/Rejected
|Transitions:Shipped->Rejected ok (clears ship_date+payment_due_date)|Complete->Rejected 400
|Payments:paid PATCH forbidden|exact-balance payment settles|overpay 400|POST NOT idempotent|accepted on Cancelled/Rejected (guard)
|Customers:top-level address overwrites BOTH addresses|partial nested address blanks the rest|archived:false un-archives|ein ignored|license_number exact+case-sensitive, license_number__in IGNORED
|Contacts:phone 10 bare digits|names max 30|deleted contacts in default list -> delete=false
|Retries:never auto-retry POST/PATCH that create things; read back by natural key first

[Skill Index]|root:./budtags/skills
|leaflink:{README.md,SKILL.md,ENTITY_TYPES.md}
|leaflink/categories:{orders.md,products.md,inventory.md,customers.md,companies.md,crm.md,webhooks.md}
|leaflink/patterns:{verified-behavior.md,authentication.md,company-scoping.md,pagination.md,filtering.md,date-formats.md,error-handling.md}
|leaflink/scenarios:{order-workflow.md,product-sync-workflow.md,inventory-workflow.md,customer-workflow.md}
|verify-alignment/patterns:{backend-critical.md,integrations.md,backend-style.md}

[Quick Reference]
|FetchOrders:$orders=$api->get_orders(page:1,status:'Submitted',path:'/leaflink/orders')
|Statuses:Draft,Submitted,Accepted,Backorder,Fulfilled,Shipped,Complete,Rejected,Combined,Cancelled
|CheckCompany:$company=$api->get('/companies/')->json('results.0');if($company['seller'])...
|DateFilter:['created_on__gte'=>'2026-10-01T00:00:00Z','created_on__lt'=>'2026-11-01T00:00:00Z']
|Pagination:['limit'=>500,'offset'=>$page*500,'ordering'=>'id'] (default 50, max 500; /products/ ignores ordering + id__gt -> dedupe by id)
|OrderFields:fields_include uses number, not id (fields_include=id -> 400)
|TrailingSlash:ALWAYS /orders-received/ NOT /orders-received

[Common Errors]
|EmptyResults:Wrong company type - using seller endpoint with buyer key (or vice versa)
|TooManyResults:filter ignored (customer_id, license_number__in, products id__in) - whole list returned
|400BadRequest:"Request path must end in a slash" - missing trailing /
|400Units:"Value must be id of an existing UnitDenomination." - sent a word instead of the id
|400OrderEdit:"Order cannot be edited." - nested order PATCH on Cancelled/Rejected; use /line-items/{id}/
|401Unauthorized:API key not configured or expired
|DuplicateLine:order PATCH line without id, or a retried create - save line ids, never blind-retry
|DayEarly:sent local midnight for a day-only date - send T17:00:00Z

[Output]|dir:.orchestr8/docs/integrations/
|format:[type]-leaflink-[name]-YYYY-MM-DD.md
