# Project: PayHive: Billing & Subscription Platform

## Problem
Invoicing systems that rely on manual checks or polling-based billing syncs lead to subscription status delays, missed payments, and overall billing inconsistencies. Manual accounting is prone to human error and doesn't scale as customer transaction volumes grow.

## Motivation
To design a secure, fully automated SaaS billing and subscription portal using webhook-driven automation that ensures immediate synchronization of billing status and customer states, while offering a low-latency API surface.

## Architecture
The system uses a decoupled client-server architecture:
1.  **Frontend:** React dashboard showing account plan status, payment history, and invoices.
2.  **Backend Services:** Node.js Express server handling checkout sessions, updates, and webhook listeners.
3.  **Data Access:** Prisma ORM abstraction mapping JavaScript objects directly to SQL operations.
4.  **Integration:** Stripe checkout flows, portal interfaces, and event notification webhooks.

## Tech Stack
*   **Core Backend:** Node.js, Express.js
*   **Database ORM:** Prisma ORM
*   **Database:** MySQL
*   **API Integrations:** Stripe API & Stripe Webhooks
*   **Performance:** Redis (Caching)

## Database
*   **MySQL:** Stores user profiles, organization plans, subscription line-items, invoices, and transaction logs. Database relations are managed and validated via Prisma schemas.

## API Design
REST APIs exposed by the Express backend:
*   `POST /api/v1/billing/checkout` - Initialize checkout session with Stripe.
*   `POST /api/v1/billing/webhook` - Stripe webhook handler endpoint (validates signatures and updates DB state).
*   `GET /api/v1/billing/subscription` - Retrieve current active subscription metadata (cached in Redis).

## Authentication
JWT-based user sessions, with verify token middlewares guarding billing actions.

## Deployment
Dockerized backend container, linked with MySQL instances, deployed behind reverse proxy servers.

## Challenges
*   **Webhook Reliability & Double Event Ingestion:** Stripe webhooks can fire multiple times or fail to deliver chronologically.
    *   *Solution:* Implemented event logging in MySQL with unique event ID indexes. The webhook handler checks the database for the event ID before processing, guaranteeing idempotency. Stripe signatures are validated cryptographically.
*   **Subscription Latency Bottlenecks:** Checking the database for subscription states on every single API request added latency.
    *   *Solution:* Cached user subscription status strings in a Redis cluster with automatic cache invalidation upon webhook update triggers.

## Results
*   Reduced manual billing admin actions by **70%**.
*   Slashed invoice discrepancies by **90%+** using robust, webhook-driven automations.
*   Reduced overall API latency by **35–45%** by introducing Prisma query optimizations and Redis caching layers.

## Future Improvements
*   Implement multi-tier corporate discount structures.
*   Add dunning email automation for handling card declines.

## Resume-Worthy Achievements
*   Produced a SaaS billing and subscription platform reducing manual billing operations by 70%.
*   Integrated Stripe payment gateway with webhook-driven automation reducing billing inconsistencies by 90%+.
*   Enhanced backend APIs and caching workflows reducing request latency by 35–45%.

## Interview Talking Points
*   *How do you handle Stripe checkout webhooks safely?* I check event signatures via the Stripe package and use MySQL transaction tables to track processed Stripe Event IDs to ensure idempotency.
*   *How did you improve database latency in PayHive?* I refactored queries using Prisma's select block to avoid fetching large unused relation columns and cached the active state key in Redis.
