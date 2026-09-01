# Distru upstream API changelog (verbatim extract)

Pulled 2026-09-01 from https://apidocs.distru.dev/#changelog. This is DISTRU's
changelog (wire contract history), not Budtags coverage. The per-category
openapi-*.json snapshots were audited 2026-05 and predate everything from
2026-06 onward here; schemas/openapi-full-2026-09-01.json is the complete
live spec (113 paths). See categories/webhooks.md for the webhook contract.

# Changelog

## 2026-09-01

- Webhook payloads now carry three new top-level fields: `event` (`CREATE`, `UPDATE`, or `DELETE`), `changes` (the edited top-level fields with `before`/`after` values on updates; empty on creates, deletes, and nested-record-only updates), and `occurred_datetime` (when the change was recorded). See the Webhooks section for details.

- Webhooks about the same record are now always delivered in the order the changes happened.

## 2026-08-27

- PDF endpoints now accept `format=binary` to get the raw PDF in the response body, alongside `url` and `email`. `format` is now documented as required; omitting it still defaults to `binary` for backward compatibility.

## 2026-08-26

- Added GET `/public/v1/tasks` and GET `/public/v1/tasks/{id}`.

- Added POST `/public/v1/tasks` to create and update tasks.

- Added DELETE `/public/v1/tasks/{id}`.

- Added a `tasks` field to the order, invoice, purchase, contact, product, batch, assembly, return, and company models listing the tasks linked to each.

- All PDF download endpoints now accept `format=email` together with an `email_addresses` list to email the PDF to one or more recipients instead of downloading it.

## 2026-08-25

- Added DELETE `/public/v1/strains/{id}`.

- Added DELETE `/public/v1/vehicles/{id}`.

- Added DELETE `/public/v1/contacts/{id}`.

- Added DELETE `/public/v1/custom-fields/{id}`.

- Added DELETE `/public/v1/companies/{id}`.

- Added DELETE `/public/v1/products/{id}`.

- Added DELETE `/public/v1/batches/{id}`.

- Added DELETE `/public/v1/test-results/{id}`.

- Added DELETE `/public/v1/purchases/{id}`.

- Added DELETE `/public/v1/orders/{id}`.

- Added DELETE `/public/v1/invoices/{id}`.

- Added DELETE `/public/v1/assemblies/{id}`.

- POST `/public/v1/packages/{id}` now accepts `is_inactive` to inactivate or reactivate a package.

- Ability to get and set price tiers on sales order items.

## 2026-08-24

- Added a `status` filter to GET `/public/v1/assemblies`.

New endpoints:

- Added POST `/public/v1/payments/{id}/void`.

New response fields:

- compact `package` object: `metrc_id`, `quantity`, `quantity_active`, `location_id`, and `license_id`

- full `package` object: `product`

- full `product` object: `quantity_active`,`quantity_active_by_location`, `quantity_reserved` and `quantity_available`.

- full `batch` object: `product`, `quantity_active` and`quantity_active_by_location`.

New request fields:

- POST `/public/v1/orders`: `note` on line items; `tax_id` on charges.

- POST `/public/v1/products`: `treez_wholesale_price`, `leaflink_product_id`.

- POST `/public/v1/purchases`: `supplier_location_id`.

- POST `/public/v1/custom-fields` and `/public/v1/custom-fields/{id}`: `disabled_field_options`.

- POST `/public/v1/companies`: `qb_customer_id`, `qb_vendor_id`, `leaflink_customer_id`.

Behavior changes:

- All POST endpoints now support sparse updates.

- Added `include_packages_with_active_quantity_by_location` and `include_batches_with_active_quantity_by_location` query params to GET `/public/v1/products` and GET `/public/v1/products/{id}`. When set, each product in the response includes fields `packages_with_active_quantity_by_location` and `batches_with_active_quantity_by_location`.

Cross-cutting filters:

- Added an `ids` filter to all GET list endpoints, restricting the result to specific records by ID.

- Added a `custom_data` filter to all applicable GET list endpoints.

- Added an `owner_ids` filter to all GET endpoints that were missing it.

- Added `inserted_datetime` and `updated_datetime` (range) filters to all GET endpoints that were missing them.

Per-endpoint filters:

- GET `/public/v1/assemblies`:

- `inserted_datetime`

- `license_ids`

- `owner_ids`

- `status`

- `updated_datetime`

- `input_*`/`output_*` variants of `product_ids`, `package_ids`, `batch_ids`, `package_compliance_labels`, `package_batch_numbers`, `batch_batch_numbers`, `product_category_ids`, `product_subcategory_ids`, `product_group_ids`, `product_brand_ids`, `product_vendor_ids`, `product_strain_ids`, `product_tag_ids`, `product_skus`

- GET `/public/v1/batches`:

- `batch_numbers`

- `has_quantity_active`

- `product_brand_ids`

- `product_category_ids`

- `product_group_ids`

- `product_ids`

- `product_skus`

- `product_strain_ids`

- `product_subcategory_ids`

- `product_tag_ids`

- `product_vendor_ids`

- GET `/public/v1/packages`:

- `batch_number`

- `batch_numbers`

- `bin_ids`

- `compliance_label`

- `compliance_labels`

- `compliance_product_name`

- `compliance_product_names`

- `contains_remediated_material`

- `expiration_datetime`

- `finished_datetime`

- `harvest_date`

- `has_coa_attached`

- `has_quantity_active`

- `inactivated_datetime`

- `is_production_batch`

- `is_test_sample`

- `is_trade_sample`

- `lab_testing_state`

- `lab_testing_states`

- `license_ids`

- `owner_ids`

- `packaged_date`

- `product_brand_ids`

- `product_category_ids`

- `product_group_ids`

- `product_skus`

- `product_strain_ids`

- `product_subcategory_ids`

- `product_tag_ids`

- `product_vendor_ids`

- `unit_type_ids`

- GET `/public/v1/products`:

- `brand_ids`

- `category_ids`

- `has_quantity_active`

- `inventory_tracking_method`

- `is_active`

- `is_featured`

- `leaflink_product_ids`

- `menu_ids`

- `menu_visibility`

- `names`

- `owner_ids`

- `product_group_ids`

- `sku`

- `skus`

- `strain_ids`

- `strain_types`

- `subcategory_ids`

- `tag_ids`

- `unit_type_ids`

- `upc`

- `upcs`

- `vendor_ids`

- GET `/public/v1/orders`:

- `batch_batch_numbers`

- `batch_ids`

- `billing_location_ids`

- `biotrack_ids`

- `buyer_company_ids`

- `company_group_ids`

- `company_ids`

- `delivered_datetime`

- `leaflink_ids`

- `location_ids`

- `menu_ids`

- `metrc_transfer_ids`

- `order_number`

- `order_numbers`

- `owner_ids`

- `package_batch_numbers`

- `package_compliance_labels`

- `package_ids`

- `payment_statuses`

- `product_brand_ids`

- `product_category_ids`

- `product_group_ids`

- `product_ids`

- `product_skus`

- `product_strain_ids`

- `product_subcategory_ids`

- `product_tag_ids`

- `product_vendor_ids`

- `shipping_location_ids`

- `statuses`

- `total`

- GET `/public/v1/companies`:

- `category`

- `city`

- `company_group_ids`

- `has_outstanding_balance`

- `leaflink_customer_ids`

- `legal_business_name`

- `license_number`

- `name`

- `names`

- `outstanding_balance`

- `owner_ids`

- `qb_customer_ids`

- `qb_vendor_ids`

- `relationship_type_ids`

- `states`

- GET `/public/v1/purchases`:

- `batch_batch_numbers`

- `batch_ids`

- `biotrack_ids`

- `company_group_ids`

- `company_ids`

- `license_number`

- `location_ids`

- `metrc_transfer_ids`

- `owner_ids`

- `package_batch_numbers`

- `package_compliance_labels`

- `package_ids`

- `payment_statuses`

- `product_brand_ids`

- `product_category_ids`

- `product_group_ids`

- `product_ids`

- `product_skus`

- `product_strain_ids`

- `product_subcategory_ids`

- `product_tag_ids`

- `product_vendor_ids`

- `purchase_number`

- `purchase_numbers`

- `statuses`

- `total`

- GET `/public/v1/invoices`:

- `batch_batch_numbers`

- `batch_ids`

- `company_group_ids`

- `company_ids`

- `invoice_numbers`

- `is_voided`

- `order_ids`

- `order_numbers`

- `order_statuses`

- `owner_ids`

- `package_batch_numbers`

- `package_compliance_labels`

- `package_ids`

- `product_brand_ids`

- `product_category_ids`

- `product_group_ids`

- `product_ids`

- `product_skus`

- `product_strain_ids`

- `product_subcategory_ids`

- `product_tag_ids`

- `product_vendor_ids`

- `remaining_amount`

- `statuses`

- `total`

- `voided_datetime`

- GET `/public/v1/credits`:

- `amount`

- `company_ids`

- `invoice_ids`

- GET `/public/v1/payments`:

- `amount`

- `company_ids`

- `invoice_ids`

- `payment_method_ids`

- `purchase_ids`

- GET `/public/v1/returns`:

- `company_ids`

- `order_ids`

- `statuses`

- GET `/public/v1/contacts`:

- `company_ids`

- GET `/public/v1/adjustments`:

- `batch_ids`

- `location_ids`

- `product_ids`

- `updated_datetime`

- GET `/public/v1/strains`:

- `name`

- `types`

- GET `/public/v1/locations`:

- `license_number`

- `name`

- GET `/public/v1/price-tiers`:

- `product_ids`

- GET `/public/v1/menus`:

- `inserted_datetime`

- `updated_datetime`

- `visibilities`

- GET `/public/v1/test-results`:

- `batch_ids`

- `inserted_datetime`

- `metrc_ids`

- `package_ids`

- `product_ids`

- GET `/public/v1/inventory`:

- `product_brand_ids`

- `product_category_ids`

- `product_group_ids`

- `product_skus`

- `product_strain_ids`

- `product_subcategory_ids`

- `product_tag_ids`

- `product_vendor_ids`

## 2026-08-21

- POST `/public/v1/credits` now allows updating `owner_id`, `external_note` and `internal_note` on automatically-created credits (from a return, an invoice overpayment, or a QuickBooks Online payment), matching what the Distru UI allows on those fields. On a credit memo created in QuickBooks Online, `owner_id` is the only updatable field. Every other field still requires a manually-created (`USER` source) credit.

## 2026-08-19

- Added POST `/public/v1/assemblies` endpoint to create, update, and delete assemblies.

- Added POST `/public/v1/assemblies/split_package` endpoint.

- Added GET `/public/v1/metrc/tags` and GET `/public/v1/metrc/tags/{id}` endpoints.

- Added GET `/public/v1/metrc/items` endpoint.

- Extended POST `/public/v1/purchases` to accept `status` and to match a purchase to a compliance transfer

- Added `batch_number`, `status`, `metrc_item_id`, `metrc_location_id`, `metrc_notes`, `metrc_production_batch_number`, `copy_custom_data_from_input`, `use_same_item`, `is_donation`, `is_test_sample`, and `is_trade_sample` to assembly outputs.

- Added GET `/public/v1/price-tiers`, GET `/public/v1/price-tiers/{id}`, POST `/public/v1/price-tiers`, and DELETE `/public/v1/price-tiers/{id}` endpoints.

## 2026-08-18

- Added POST `/public/v1/packages/finish` endpoint.

- Added POST `/public/v1/packages/move` endpoint.

- Added `inserted_datetime` (the record's creation datetime) to the product, package, user, license, charge, order item and invoice item objects returned across the API.

## 2026-08-17

- Added GET/POST/DELETE `/public/v1/bins` endpoints.

- Added `bin_ids` to POST `/public/v1/batches` and POST `/public/v1/packages/:id` to set a record's bins.

- Added `bins` to the response of GET `/public/v1/batches`, GET `/public/v1/batches/:id`, POST `/public/v1/batches`, GET `/public/v1/packages` and POST `/public/v1/packages/:id`, present only when bin inventory tracking is enabled.

- Added POST `/public/v1/products/add-costs` endpoint.

- Added POST `/public/v1/batches/add-costs` endpoint.

- Added POST `/public/v1/packages/add-costs` endpoint.

## 2026-08-13

- Added GET `/public/v1/taxes` endpoint.

- Added GET `/public/v1/unit-types` endpoint.

- Added GET `/public/v1/official-product-categories` endpoint.

- Added GET/POST/DELETE `/public/v1/product-groups` endpoints.

- Added GET/POST/DELETE `/public/v1/product-categories` endpoints.

- Added GET/POST/DELETE `/public/v1/product-subcategories` endpoints.

- Added GET/POST/DELETE `/public/v1/company-groups` endpoints.

- Added GET/POST/DELETE `/public/v1/tags` endpoints.

- Added GET/POST/DELETE `/public/v1/cost-types` endpoints.

- Added GET/POST/DELETE `/public/v1/drivers` endpoints.

- Added GET `/public/v1/credits` endpoint.

- Added GET `/public/v1/credits/:id` endpoint.

- Added POST `/public/v1/credits` endpoint.

- Added DELETE `/public/v1/credits/:id` endpoint.

- Added POST `/public/v1/credits/:id/cancel` endpoint.

- Added `credit_uses` and `overpayment_credits` to the payment object returned by GET `/public/v1/payments` and GET `/public/v1/payments/:id`.

- Added `payments` to the response of GET `/public/v1/purchases`, GET `/public/v1/purchases/:id`, GET `/public/v1/invoices` and GET `/public/v1/invoices/:id`. Each element is the full payment object also returned by GET `/public/v1/payments`.

- On GET `/public/v1/credits` and GET `/public/v1/credits/:id`, a credit's `payment` (the originating invoice payment for overpayment or QuickBooks-linked credits) and each `credit_uses` entry's `payment` are that same full payment object.

## 2026-08-12

- Added GET `/public/v1/payment-terms` endpoint.

- Added `default_payment_term` to the response of GET `/public/v1/companies` and GET `/public/v1/companies/:id`.

- Added `default_payment_term_id` to POST `/public/v1/companies` for setting a company relationship's default payment term.

- Added `outstanding_balance` to the response of GET `/public/v1/companies` and GET `/public/v1/companies/:id`.

- Added 9 PDF download endpoints:

- GET `/public/v1/invoices/:id/pdf` — invoice PDF.

- GET `/public/v1/invoices/:id/test-results/pdf` — combined COA PDF for the invoice.

- GET `/public/v1/orders/:id/pdf` — sales order slip PDF.

- GET `/public/v1/orders/:id/test-results/pdf` — combined COA PDF for the order.

- GET `/public/v1/purchases/:id/pdf` — purchase order PDF.

- GET `/public/v1/assemblies/:id/pdf` — work order PDF.

- GET `/public/v1/test-results/:id/pdf` — single test result COA PDF.

- GET `/public/v1/batches/:id/primary-test-result/pdf` — batch primary test result COA PDF.

- GET `/public/v1/packages/:id/primary-test-result/pdf` — package primary test result COA PDF.

- Added `coa_url` to test result objects: a public, non-expiring URL to view or download the test result's COA PDF, or `null` when no file is attached. Included in GET `/public/v1/test-results` and GET `/public/v1/test-results/:id`, and in the nested `primary_test_result` object of GET `/public/v1/batches` and GET `/public/v1/packages`.

## 2026-08-03

- Added GET `/public/v1/payments` and GET `/public/v1/payments/:id` endpoints.

- Renamed `inserted_at` → `inserted_datetime` and `updated_at` → `updated_datetime`:

- GET `/public/v1/returns`.

- GET `/public/v1/returns/:id`.

- GET `/public/v1/adjustments`.

- GET `/public/v1/adjustments/:id`.

- GET `/public/v1/product-pos-mappings`.

- GET `/public/v1/product-pos-mappings/:id`.

## 2026-07-30

- Added `upsert_invoice`, `email_invoice` and `email_invoice_addresses` to POST `/public/v1/orders`.

## 2026-07-29
Read/write parity pass across the API — every field that can be set can now be read back, and related resources (owner, locations, notes, custom data, tags) are exposed consistently.

- Added `owner` (a full user object) to the response of the following endpoints:

- GET `/public/v1/products` and `/public/v1/products/:id`

- GET `/public/v1/purchases` and `/public/v1/purchases/:id`

- GET `/public/v1/companies` and `/public/v1/companies/:id`

- GET `/public/v1/contacts` and `/public/v1/contacts/:id` (previously only the owner's id was returned)

- Added `billing_location` to the response of POST `/public/v1/invoices`, GET `/public/v1/invoices` and GET `/public/v1/invoices/:id`.

- Added `billing_location` and `location` to the response of POST `/public/v1/purchases`, GET `/public/v1/purchases` and GET `/public/v1/purchases/:id`.

- Added `external_notes` and `internal_notes` to the response of POST `/public/v1/invoices`, GET `/public/v1/invoices` and GET `/public/v1/invoices/:id`.

- Added `description` to the response of GET `/public/v1/purchases` and GET `/public/v1/purchases/:id`.

- Added `blaze_payment_type` to the response of GET `/public/v1/orders` and GET `/public/v1/orders/:id`.

- Added the following fields to the response of GET `/public/v1/products` and GET `/public/v1/products/:id`:

- `upc`

- `is_featured`

- `wholesale_unit_price`

- `quantity_available_threshold_min`

- `quantity_available_threshold_max`

- `total_thc`

- `total_cbd`

- `total_cannabinoid_unit`

- `tags`

- Added `unit_cost` to the response of GET `/public/v1/adjustments` and GET `/public/v1/adjustments/:id`.

- Added `quickbooks_deposit_account_name` to the response of POST `/public/v1/invoices/:id/payments` and POST `/public/v1/purchases/:id/payments`.

- Added `owner_id`, `custom_data`, `external_notes` and `internal_notes` to POST `/public/v1/invoices`.

- Added `owner_id` and `custom_data` to POST `/public/v1/purchases`.

- Added `name` and `custom_data` to POST `/public/v1/batches`.

- Added `bill_of_materials` to the response of GET `/public/v1/products/:id` (always included) and GET `/public/v1/products` (included when the `include_bill_of_materials=true` query param is set). `cost_type.cost_per_unit` is only returned to callers with the `costs_permissions_view_cost_types_cost_per_unit` permission.

- POST `/public/v1/orders`: `due_datetime` is now optional. When omitted, the due date is derived from the customer's default payment term, then the company default order payment term, then falls back to the order date (COD).

## 2026-07-27

- Added GET `/public/v1/reports/sales-order-tax` endpoint.

- Added GET `/public/v1/reports/inventory-assets` endpoint.

- Added GET `/public/v1/reports/sales-order-history` endpoint.

- Added GET `/public/v1/reports/sales-order-item-history` endpoint.

- Added GET `/public/v1/reports/sales-by-company` endpoint.

- Added GET `/public/v1/reports/sales-by-product` endpoint.

- Added GET `/public/v1/reports/sales-by-user` endpoint.

- Added GET `/public/v1/reports/order-fulfillment` endpoint.

- Added GET `/public/v1/reports/purchase-order-history` endpoint.

- Added GET `/public/v1/reports/purchases-by-company` endpoint.

- Added GET `/public/v1/reports/purchases-by-product` endpoint.

- Added GET `/public/v1/reports/invoice-history` endpoint.

- Added GET `/public/v1/reports/cogs` endpoint.

- Added GET `/public/v1/reports/inventory-valuation` endpoint.

- Added GET `/public/v1/reports/inventory-transaction-history` endpoint.

- Added GET `/public/v1/reports/harvest-outputs` endpoint.

- Added GET `/public/v1/reports/plant-lifecycle` endpoint.

- Added GET `/public/v1/reports/cultivation-transaction-history` endpoint.

## 2026-06-29

- Added `gross_weight` and `gross_weight_unit_type` fields to GET and POST `/public/v1/products`.

## 2026-06-23

- Added `quickbooks_sync_enqueued` field to the response of POST `/public/v1/invoices/{id}/payments`.

## 2026-06-08

- Added GET/POST `/public/v1/custom-fields` endpoint

- Added GET/POST `/public/v1/vehicles` endpoint

- Added GET/POST `/public/v1/strains/:id` endpoint

- Added `license_number` and `inventory_source` to order responses

- Added `custom_data` to POST `/public/v1/orders` endpoint

## 2026-05-28

- Added ability to fetch by /id on most endpoints

## 2026-05-25

- Added GET `/public/v1/returns` endpoint

## 2026-05-17

- Added `company_id` filter parameter to GET `/public/v1/orders` endpoint

- Added GET `/public/v1/menus` endpoint

## 2026-05-11

- Added `lab_testing_state` field to GET `/public/v1/packages` endpoint

- Added support for non-admin users to use the API.

- Added permission checks to most controllers.

## 2026-05-06

- Added `menu_id` and `menu_name` filter parameters to GET `/public/v1/products` endpoint

## 2026-05-01

- Added `custom_data` field to POST `/public/v1/products` endpoint

## 2026-03-27

- Removed `POST /public/v1/products/{id}/images` endpoint

## 2026-03-10

- Added `POST /public/v1/products/{id}/images` endpoint

- Added `POST /public/v1/companies` endpoint

## 2026-02-13

- Added `batch_ids[]` query parameter to GET `/public/v1/batches` endpoint to filter batches by batch IDs.

## 2026-02-12

- Added the `completion_datetime` as a query parameter to GET `public/v1/adjustments`

- Added the `inserted_at` field to `public/v1/adjustments`

## 2026-02-10

- Added the `payment_terms_name` field to GET `public/v1/orders`

## 2026-01-23

- Added the `deleted_at` field and the `deleted` filter parameter to the following endpoints:

- GET `public/v1/batches` (breaking change: deleted batches are no longer returned by default)

- GET `public/v1/companies`

- GET `public/v1/contacts`

- GET `public/v1/locations`

- GET `public/v1/payment_methods`

- GET `public/v1/products` (breaking change: deleted products are no longer returned by default)

- GET `public/v1/users`

- Added `estimated_departure_datetime` and `estimate_arrival_datetime` to `metrc_transfer_template_transporter_info` field in POST `public/v1/orders`.

- Added automatic estimated departure / arrival calculations for transporters such that, if left blank,
the fields will be populated with the first departure estimate being the time that the template was
sent to Metrc, the drive time for each transporter being 1 hour, and the departure of the next
transporter being the arrival time of the previous transporter.

- Modified Destination estimated departure / arrival times to be the first departure and the last arrival
of the specified transporters.

## 2026-01-21

- Added the `manufactured_datetime` field to GET `public/v1/batches` and POST `public/v1/batches`.

- Added the `assembly_number` and `estimated_start_date` fields to GET `public/v1/assemblies`.

- Added the `reserved` field to GET `public/v1/inventory`.

## 2026-01-19

- Added the following endpoints:

- POST `public/v1/contacts`

- POST `public/v1/custom-fields`

- Added the following fields to `public/v1/adjustments`

- `compliance_unit_type`

- `unit_type`

- Added the `batch_ids` and `location_ids` filter parameters to GET `public/v1/inventory`.

- Added the `product_id` and `batch_number` filter parameters to GET `public/v1/batches`.

- Added the `product_name` filter parameter to GET `public/v1/products`.

- Added the `product_ids` filter parameter to GET `public/v1/packages`.

## 2025-10-24

- Added the following fields to `public/v1/products`

- `unit_net_weight_serving_size_unit_type`

- `unit_net_weight`

- `unit_serving_size`

## 2025-10-19

- Added `unit_cost` to the endpoint GET `public/v1/products`

## 2025-10-15

- Added the following fields to `public/v1/inventory`

- `total_cost_actual`

- `total_cost_default`

- `cost_per_unit_actual`

- `cost_per_unit_default`

## 2025-09-10

- Added `cost_per_unit_actual` and `cost_per_unit_default` to the following endpoints:

- GET `public/v1/assemblies`

- GET `public/v1/orders`

- GET `public/v1/orders/:id`

- GET `public/v1/invoices`

- GET `public/v1/invoices/:id`

- GET `public/v1/batches`

- GET `public/v1/packages`

- Added fields `total_cost_actual`, `total_cost_default` and attribute `include_costs` to the following endpoints:

- GET `public/v1/batches`

- GET `public/v1/packages`

## 2025-08-21

- Added `group` to GET `/public/v1/companies`

## 2025-08-20

- Added GET `/public/v1/product-pos-mappings` endpoint

- Added POST `/public/v1/product-pos-mappings` endpoint

- Added DELETE `/public/v1/product-pos-mappings/:id` endpoint

## 2025-08-19

- All GET endpoints now return eventually consistent data, with changes taking up to 1 second to propagate in responses

## 2025-07-01

- Added `description_markdown` to GET/POST `/public/v1/products`

## 2025-06-12

- Added `metrc_transfer_id` and `biotrack_id` to GET `/public/v1/orders`

## 2025-06-12

- Changed `cost` on GET `/public/v1/assemblies` to `total_cost_actual` in `ingredients`

- Added `total_cost_default` to GET `/public/v1/assemblies` in `ingredients`

- Added `total_cost_actual` to GET `/public/v1/assemblies` in `additional_costs`

- Added `total_cost_default` to GET `/public/v1/assemblies` in `additional_costs`

## 2025-06-09

- Added POST `/public/v1/file-attachments` endpoint for uploading files and attaching them to business entities (products, orders, purchases, etc.).

## 2025-05-27

- Added `biotrack_id` and `metrc_transfer_id` to POST `/public/v1/orders`

## 2025-05-22

- Added `external_name` to GET/POST `/public/v1/products`

## 2025-05-18

- Added `leaflink_order_number` to GET `/public/v1/orders`

## 2025-05-16

- Added GET `/public/v1/test-results`

- Added POST `/public/v1/test-results`

## 2025-05-15

- Added POST `/public/v1/stock_adjustments` endpoint.

## 2025-05-14

- Added `custom_data` to the response of the following endpoints:

- GET `/public/v1/assemblies`

- GET `/public/v1/batches`

- POST `/public/v1/batches`

- GET `/public/v1/companies`

- GET `/public/v1/contacts`

- GET `/public/v1/invoices`

- GET `/public/v1/invoices/:id`

- POST `/public/v1/invoices`

- GET `/public/v1/orders`

- GET `/public/v1/orders/:id`

- POST `/public/v1/orders`

- GET `/public/v1/packages`

- GET `/public/v1/products`

- POST `/public/v1/products`

- GET `/public/v1/purchases`

- POST `/public/v1/purchases`

## 2025-05-13

- Added GET `/public/v1/adjustments` endpoint.

## 2025-05-06

- Added `is_trade_sample` to GET `/public/v1/packages` endpoint.

## 2025-04-09

- Added the following fields to GET `/public/v1/companies` endpoint:

- `legal_business_name`

- `default_email`

- `phone_number`

- `invoice_email`

- `sales_order_email`

- `purchase_order_email`

- `order_shipment_email`

- `website`

- `default_sales_order_notes`

- `default_purchase_order_notes`

- `outstanding_balance_threshold`

- `owner_id`

## 2025-03-18

- Modified `unit_net_weight` and `unit_serving_size` in GET `/public/v1/products` endpoint: These fields can now be populated regardless of the product's unit type.

## 2025-03-11

- Added `total_cost_actual`, `total_cost_default` and `returned_quantity` to "items" in GET `/public/v1/invoices` endpoint.

- Added `total_cost_actual`, `total_cost_default` and `returned_quantity` to "items" in GET `/public/v1/invoices/:id` endpoint.

- Added `total_cost_actual`, `total_cost_default` and `returned_quantity` to "items" in GET `/public/v1/orders` endpoint.

- Added `total_cost_actual`, `total_cost_default` and `returned_quantity` to "items" in GET `/public/v1/orders/:id` endpoint.

## 2025-03-05

- Added GET `/public/v1/assemblies` endpoint.

## 2025-02-26

- Page size change from 50,000 to 5000 for the following endpoints:

- GET `/public/v1/batches`

- GET `/public/v1/companies`

- GET `/public/v1/contacts`

- GET `/public/v1/inventory`

- GET `/public/v1/packages`

- GET `/public/v1/products`

- GET `/public/v1/purchases`

## 2025-01-31

- Added POST `/public/v1/batches` endpoint.

- Added batch_number, product_id, owner_id and description to GET `/public/v1/batches` endpoint.

- Added title and phone_number to GET `/public/v1/contacts` endpoint.

## 2025-01-17

- Added `product_unit_quantity` to GET `/public/v1/packages` endpoint.

- Added `product_unit_type` to GET `/public/v1/packages` endpoint.

## 2025-01-15

- Added POST `/public/v1/purchases/:id/payments` endpoint.

- Added POST `/public/v1/invoices/:id/payments` endpoint.

## 2025-01-08

- Added GET `/public/v1/payment-methods` endpoint.

## 2024-12-26

- Added msrp, is_active, category.type and images.rank to GET `/public/v1/products`.

## 2024-12-24

- Added billing_location_id to POST `/public/v1/purchases` endpoint.

## 2024-11-06

- Field thc of type string in the Product object was replaced with total_thc field of type number.

- Field cbd of type string in the Product object was replaced with total_cbd field of type number.

- Added total_cannabinoid_unit field to Product object. Allowed values are either "MG" or "PERCENT".

## 2024-10-02

- Added GET `/public/v1/strains` endpoint.

- In endpoint GET /public/v1/companies, added fields category and relationship to the response.

      
      
      
    
  

