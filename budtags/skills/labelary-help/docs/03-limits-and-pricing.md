<!-- Source: Labelary API Documentation -->
<!-- Section: Limits and Pricing -->
<!-- Generated: 2025-11-02 19:43:59 -->

# 3. Limits

As a shared service, the Labelary API incorporates a number of usage limits which ensure that no single user can negatively impact the workloads of other users. If the free plan limits are too restrictive for your intended use, you may want to consider upgrading to one of our premium plans.

## Usage Limits Table

| Limit | Free | Plus | Business | Error Response | Notes |
|-------|------|------|----------|----------------|-------|
| Requests per second | 3 | 6 | 10 | HTTP 429 (Too Many Requests) | See the FAQ for details |
| Requests per day | 5,000 | 20,000 | 40,000 | HTTP 429 (Too Many Requests) | See the FAQ for details |
| Labels per request | 50 | 50 | 50 | HTTP 413 (Payload Too Large) | See the FAQ for details |
| Request body size | 1 MB | 1 MB | 1 MB | HTTP 413 (Payload Too Large) | |
| Label dimensions | 15 inches | 15 inches | 15 inches | HTTP 400 (Bad Request) | |
| Embedded image dimensions | 2,000 pixels | 2,000 pixels | 2,000 pixels | HTTP 400 (Bad Request) | Affects e.g. ~DG and ~DY |
| Embedded object size | 2 MB | 2 MB | 2 MB | HTTP 400 (Bad Request) | Affects e.g. ~DU and ~DY |
| Printer memory contents | 2 MB | 2 MB | 2 MB | HTTP 400 (Bad Request) | See the FAQ for details |
| Output PNG image buffer | 10 MB | 10 MB | 10 MB | HTTP 400 (Bad Request) | See the FAQ for details |
| Image dimensions | 2,000 pixels | 2,000 pixels | 2,000 pixels | HTTP 400 (Bad Request) | Affects graphics API only |
| Image file size | 200 KB | 200 KB | 200 KB | HTTP 400 (Bad Request) | Affects graphics API only |
| Font file size | 200 KB | 200 KB | 200 KB | HTTP 400 (Bad Request) | Affects font API only |

# 4. Plans and Pricing

This Labelary API is **free for any use**, personal or commercial, and requires no sign-up or API key.

However, if your system is business-critical (or becomes business-critical), you may find that you need official support SLAs, system availability guarantees, data privacy commitments, or less restrictive usage limits. If this is the case, you have the option of upgrading to one of our premium plans.

From an implementation perspective, upgrading from the free plan to a premium plan is as simple as updating your API URL hostname and adding an API key to your API requests. Your private API hostname and API key are provided via email upon sign-up.

You can choose whether you'd like to be billed monthly or annually. Customers who choose to commit for a full year receive the 12th month free.

If you don't see a plan that fits your specific requirements, just email us and we'll see if we can create a custom plan for you.

## Plan Comparison

| Feature | Labelary Free | Labelary Plus | Labelary Business | Labelary On-Prem |
|---------|---------------|---------------|-------------------|------------------|
| **Price** | Free | $90/month | $228/month | Email Us |
| **Deployment Model** | SaaS | SaaS | SaaS | On-Premise |
| **Support** | None | Basic | Premium | Premium |
| **Availability SLA** | None | 99% | 99.9% | Custom |
| **Release Channel** | Beta | Stable | Stable | Stable |
| **Maximum Data Retention** | 60 days | Never | Never | Never |
| **Maximum Requests per Second** | 3 | 6 | 10 | No Limit |
| **Maximum Requests per Day** | 5,000 | 20,000 | 40,000 | No Limit |
| **API Key** | None | Provided via email | Provided via email | None |
| **API Server** | api.labelary.com | Provided via email | Provided via email | On-Premise Servers |