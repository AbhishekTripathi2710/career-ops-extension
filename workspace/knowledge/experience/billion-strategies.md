# Experience: Billion Strategies

## Company
Billion Strategies - Remote

## Role
Full Stack Developer Intern

## Duration
January 2025 – May 2025

## Tech Stack
*   **Backend:** Node.js, Express.js, Python, SQL, REST APIs, API Integration
*   **Databases & Caching:** MySQL, Redis
*   **DevOps & Tools:** Git, GitHub, Postman, Shopify Admin, ShipEase API

## Products Worked On
*   **E-commerce Logistics & Order Orchestration Engine:** A backend system aggregating order placements from channels like Shopify and coordinating full-fillment via ShipEase.

## Major Features
*   **Order Sync ETL Pipeline:** An automated scheduled process capturing order payloads, validating records, and queuing them for shipping.
*   **High-Throughput Database Layer:** Optimizations to SQL indexes, caching behaviors, and connection pooling settings.

## Architecture
*   **Workflow Ingestion:** Shopify webhooks trigger an Express listener that pushes order files to an internal processing queue. A Python worker performs ETL transformations and outputs structured data into a MySQL store.
*   **Shipping Sync:** Express services synchronize inventory and shipping tickets with the ShipEase API asynchronously.

## Challenges
*   **Manual Order Entry Bottlenecks:** Customer support spent hours manually double-keying order details from Shopify to ShipEase.
    *   *Solution:* Engineered a fully automated ETL workflow connecting APIs directly.
*   **Slow Inventory Searches under Peak Traffic:** High read-query latency when syncing multiple warehouse inventory caches.
    *   *Solution:* Refactored complex nested SQL JOIN queries, built composite B-Tree indexes on keys, and introduced an active Redis caching layer.

## Impact
*   Automated 1,000+ daily order workflows, eliminating manual operations by 95%.
*   Boosted database query throughput and slashed system response times by 25–75%.

## Things Learned
*   Building resilient ETL pipelines with third-party webhooks and API limitations (Shopify rate limits).
*   Advanced query profile analysis using `EXPLAIN` to isolate database execution bottlenecks.
*   Integrating cache invalidation protocols in Redis.

## Interesting Bugs
*   *The Webhook Race Condition:* In multiple instances, updates to orders fired Shopify webhooks in rapid succession, resulting in concurrent database writes attempting to insert the same record, causing unique constraint violations.
    *   *Fix:* Added Redis-based distributed locking on the order ID, forcing serial execution of webhook handlers for the same resource.

## Metrics
*   **1,000+** daily order workflows automated.
*   **95%** reduction in manual entry tasks.
*   **25–75%** increase in database throughput.

## Leadership
*   Advocated for index tracking guidelines to prevent unindexed columns from reaching production environments.

## Ownership
*   Sole owner of the backend ETL worker pipeline sync between Shopify Admin and ShipEase.
*   Lead engineer on the SQL query refactoring initiative.
