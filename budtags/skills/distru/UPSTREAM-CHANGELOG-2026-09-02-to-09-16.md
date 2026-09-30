

## 2026-09-16

- Page size reduced for the following endpoints:

- GET /public/v1/adjustments

- GET /public/v1/assemblies

- GET /public/v1/batches

- GET /public/v1/companies

- GET /public/v1/credits

- GET /public/v1/invoices

- GET /public/v1/metrc/tags

- GET /public/v1/orders

- GET /public/v1/packages

- GET /public/v1/products

- GET /public/v1/returns

- GET /public/v1/strains

- GET /public/v1/test-results

- Page size is not client-controllable. Follow the next_page URL in each response rather
than assuming a fixed number of rows per page.

- Pagination is documented as one pattern: request a list endpoint with no page parameter,
then follow next_page until it is null. GET /public/v1/inventory no longer documents a
page selector; requests that still send one are unaffected.

## 2026-09-14

- The status field is now required when creating a purchase via POST /public/v1/purchases; a create request without it is rejected with a 400. It previously defaulted to PENDING when omitted. Updates are unchanged: omit status to leave it as is. This change was announced with four weeks of notice.

## 2026-09-09

- Price tier percent (request and response, including the PriceTierVersion snapshot) is now a decimal string with up to 3 decimal places instead of an integer. Price tier price now supports up to 5 decimal places instead of 2.

## 2026-09-05

- Added POST /public/v1/packages/import to import Metrc packages.

## 2026-09-04

- Added Package webhooks: a PACKAGE webhook fires when a package is created, edited, or deleted, and when its bins or lab test results change.

- Product webhooks now fire when a product's company-wide active or reserved quantity changes, with the before/after totals in changes (quantity_active, quantity_reserved, quantity_available).

- The GET /public/v1/metrc/... endpoints accept a license_number query param as a convenience alternative to license_id.

- Added GET /public/v1/metrc/strains listing the Metrc strains cached from your licenses.

- Added GET /public/v1/metrc/locations listing the Metrc locations cached from your licenses.

- Added GET /public/v1/metrc/packages and GET /public/v1/metrc/packages/{label} listing the Metrc packages cached from your licenses.

- Added GET /public/v1/metrc/transfers and GET /public/v1/metrc/transfers/{manifest_number} listing the Metrc transfers cached from your licenses.

## 2026-09-03

- Added POST /public/v1/companies/{id}/locations to create and update the locations of the companies in your CRM.

- Added POST /public/v1/locations to create and update your own company's locations.

- Added POST /public/v1/assemblies/create_test_sample to create and complete a test sample assembly from a Metrc package in one call.

- Added GET /public/v1/metrc/lab-test-batches listing a license's lab test batches grouped by Metrc item category, with the ones Metrc requires flagged.

## 2026-09-02

- Added GET /public/v1/charge-presets and GET /public/v1/charge-presets/{id}.

- Added POST /public/v1/charge-presets to create and update charge presets.

- Added DELETE /public/v1/charge-presets/{id}.

- Charges on orders, invoices, and purchases now carry a charge_preset field referencing the preset they were applied from.

- Charges sent to POST /public/v1/orders and POST /public/v1/purchases accept a charge_preset_id: the charge's name, type, and amounts are filled from the preset (with inline edits when the preset allows them), and the link is fixed once the charge exists. See the charges field on each endpoint.

- Creating an order or purchase now auto-applies charge presets whose auto-apply tags match the products, exactly like the Distru order forms.

- Added GET /public/v1/licenses and GET /public/v1/licenses/{id} returning your company's licenses with their Metrc sync health.

- Added POST /public/v1/companies/{id}/licenses to create and update the licenses of the companies in your CRM.

- Added GET /public/v1/license-types listing the license type values valid for your company's US state.

