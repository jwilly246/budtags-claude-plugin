[BudTags Skills Index]|root:./budtags/skills
|IMPORTANT:Prefer retrieval-led reasoning over pre-training-led reasoning
|CRITICAL:Read verify-alignment/patterns/backend-critical.md before ANY backend implementation
|CRITICAL:Read metrc-api/METRC_API_RULES.md before ANY Metrc work
|metrc-api:{README.md,METRC_API_RULES.md}
|metrc-api/categories:{packages.md,plants.md,plantbatches.md,harvests.md,transfers.md,sales.md,labtests.md,items.md,locations.md,strains.md,tags.md,facilities.md,employees.md,patients.md,webhooks.md}
|metrc-api/patterns:{license-types.md,authentication.md,pagination.md,batch-operations.md,error-handling.md,date-formats.md,transfer-workflows.md}
|metrc-api/scenarios:{create-packages-from-harvest.md,record-sales-receipt.md,check-in-incoming-transfer.md,move-plants-to-flowering.md,record-lab-test-results.md}
|verify-alignment:{README.md,SKILL.md}
|verify-alignment/patterns:{backend-critical.md,backend-style.md,backend-flash-messages.md,frontend-critical.md,frontend-data-fetching.md,frontend-typescript.md,integrations.md,database.md,websockets.md,git-workflow.md,php8-brevity.md}
|verify-alignment/scenarios:{controller-method.md,react-component.md,inertia-form.md,react-query-hook.md,migration.md}
|tanstack-query:{README.md,SKILL.md}
|tanstack-query/patterns:{01-installation-setup.md,02-core-concepts.md,03-important-defaults.md,04-query-keys.md,06-typescript.md,07-basic-queries.md,08-parallel-queries.md,09-dependent-queries.md,13-mutations.md,14-invalidation-refetching.md,15-optimistic-updates.md,16-infinite-queries.md,18-prefetching.md,20-cache-updates.md,26-testing.md}
|tanstack-table:{README.md,SKILL.md}
|tanstack-table/patterns:{02-core-concepts.md,03-column-definitions.md,07-sorting.md,08-filtering.md,09-pagination.md,10-row-selection.md,11-column-visibility.md,14-column-pinning.md,18-virtualization.md,24-budtags-integration.md}
|tanstack-virtual:{README.md,patterns/core-concepts.md,patterns/row-virtualizer.md,patterns/dynamic-sizing.md,patterns/table-virtualization.md}
|leaflink:{README.md,SKILL.md,ENTITY_TYPES.md}
|leaflink/categories:{orders.md,products.md,inventory.md,customers.md,companies.md}
|leaflink/patterns:{authentication.md,company-scoping.md,pagination.md,filtering.md,error-handling.md}
|leaflink/scenarios:{order-workflow.md,product-sync-workflow.md,inventory-workflow.md}
|quickbooks:{README.md,SKILL.md,ENTITY_TYPES.md}
|quickbooks/categories:{authentication.md,invoices.md,payments.md,customers.md,items.md,credit-memos.md}
|quickbooks/patterns:{authentication.md,token-refresh.md,multi-tenancy.md,error-handling.md}
|quickbooks/scenarios:{invoice-workflow.md,payment-workflow.md,metrc-sync-workflow.md}
|inertia:{README.md,SKILL.md}
|inertia/patterns:{07-forms-useform.md,08-form-helper-advanced.md,09-shared-data.md,10-partial-reloads.md,11-deferred-props.md,17-error-handling.md,25-budtags-integration.md}
|budtags-testing:SKILL.md
|inertia-react-development:SKILL.md
|tailwindcss-development:SKILL.md
|react-19:{patterns/*.md}
|quill:{README.md,categories/*.md}
|zpl:{commands/*.md}
|labelary-help:{docs/*.md}
|create-plan:SKILL.md
|decompose-plan:SKILL.md
|run-plan:SKILL.md
[License Restrictions]
|Cultivation:plants,plantbatches,harvests,packages|NO:sales
|Processing:packages,items,labtests,processingjob|NO:plants,sales
|Retail:sales,packages,patients,transfers|NO:plants,plantbatches
[Critical Patterns]
|OrgScope:Package::where('organization_id',$user->active_org_id)
|MetrcApi:$api->set_user(request()->user());$license=session('license');
|Flash:->with('message','text')|NOT:'success'
|Log:LogService::store()|NOT:Log::info()
