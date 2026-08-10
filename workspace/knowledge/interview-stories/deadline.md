# Interview Story: Tight Deadline

## Situation
During my internship at Billion Strategies, the logistics operations team was struggling to keep up with order volumes. They were manually syncing over 1,000+ daily orders from Shopify to our logistics partner (ShipEase), causing delays and errors. Management set a tight deadline of three weeks to automate this pipeline before an upcoming sales campaign.

## Task
To engineer, test, and deploy a secure, automated ETL pipeline from Shopify Admin to ShipEase APIs within 21 days, ensuring zero order dropouts.

## Action
1.  **Scope & Simplify:** Kept the scope focused on core operations. I built a robust Node.js webhook receiver to capture Shopify payloads and queue them, rather than building a complex administrative interface.
2.  **Iterative Engineering:** Created a Python ETL worker to parse the incoming payloads, sanitize addresses, format SKUs, and sync them with ShipEase. I set up comprehensive log tracking so any sync failure would be flagged immediately.
3.  **Stress Testing:** Conducted mock load runs in our sandbox environment to simulate order bursts, using Python scripts to fire concurrent webhook calls.

## Result
*   Deployed the pipeline in 18 days, three days ahead of schedule.
*   Automated **1,000+** daily order syncs, reducing manual entry operations by **95%**.
*   The system processed order bursts during the sales campaign with zero dropouts.
*   Learned to prioritize the core features under tight deadlines, delivering a robust integration that resolved a major operational bottleneck.
