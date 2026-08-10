# Achievements: Performance & Optimization

This database contains quantifiable achievements related to software latency, performance, optimization, and throughput.

## Slashed API Request Latency (CloudStorage)
*   **Accomplishment:** Optimized database queries and backend workflows to reduce file retrieval and dashboard response latency by **40–50%**.
*   **How:** Analyzed SQL query plans, created indexes on parent folders to prevent table scans, and restructured asynchronous file upload events to prevent server thread blocking.
*   **Impact:** Enhanced usability for users browsing directories with large file structures.

## Slashed API Request Latency (PayHive)
*   **Accomplishment:** Reduced backend API query response times and transaction check latency by **35–45%**.
*   **How:** Cached user subscription plans in Redis, query selector tuning in Prisma (fetching only needed columns), and optimized relations lookup.
*   **Impact:** Fast page loadings for checking out subscriptions and subscription status verifications.

## Slashed Database Query Times (Billion Strategies)
*   **Accomplishment:** Boosted database query throughput and slashed order lookup times by **25–75%**.
*   **How:** Analyzed slow inventory and product log search queries using `EXPLAIN`, built composite B-Tree indexes, refactored nested SQL JOIN blocks, and setup an active Redis caching layer.
*   **Impact:** Allowed database to scale effortlessly under high peak order volumes during sales campaigns.
