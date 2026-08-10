# Interview Story: Bug Debugging

## Situation
At Billion Strategies, we automated e-commerce order ingestion via Shopify webhooks. During a flash sale event, our logging system reported multiple duplicate order entries in MySQL and random unique constraint database errors, which halted our processing queue.

## Task
To isolate and fix this webhook concurrency bug to prevent duplicate orders and ensure the system could handle high traffic without crashing.

## Action
1.  **Analyze Logs:** Checked the database logs and discovered that Shopify was firing multiple webhooks for the same order in rapid succession (e.g., when a user updated their shipping details immediately after purchase).
2.  **Identify Race Condition:** Because the webhook handlers ran concurrently, the first request had not finished writing to the database before the second request checked for the order's existence. Both requests attempted to insert the same record, causing a database collision.
3.  **Implement Locking System:** Integrated Redis into our middleware to act as a distributed lock. When a webhook arrived, the handler attempted to acquire a lock using the order ID as a key. If the lock was held, subsequent requests would wait or be safely discarded if they were duplicate events.
4.  **Add Idempotency Keys:** Implemented database-level transaction logging with unique indexes on Stripe and Shopify event IDs to ensure we only processed each event once.

## Result
*   Fixed the race condition completely, resolving the duplicate order and database collision issues.
*   The system processed all subsequent high-traffic events without any order duplication or unique constraint errors.
*   Learned the importance of designing APIs to be idempotent and using distributed locks to manage concurrency in high-volume, event-driven architectures.
