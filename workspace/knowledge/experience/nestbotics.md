# Experience: Nestbotics

## Company
Nestbotics (Noida, India) - Onsite

## Role
Full Stack Developer

## Duration
January 2026 – Present

## Tech Stack
*   **Frontend:** React.js, TailwindCSS, WebSockets, HTML5, CSS3
*   **Backend:** Node.js, Express.js, REST APIs, Microservices, Authentication, JWT
*   **AI/ML:** LangChain, Retrieval-Augmented Generation (RAG), LLM Integration, Prompt Engineering, Semantic Search, Embedding Models, OCR Pipelines
*   **Databases:** ChromaDB, MySQL, MongoDB, FAISS
*   **DevOps & Tools:** Git, GitHub, Docker, Postman, CI/CD

## Products Worked On
*   **Enterprise AI Document Processing Platform:** A system designed to parse enterprise-grade files (PDFs, docs) while maintaining layout/structural relevance for RAG queries.
*   **Enterprise ERP/MRP Dashboards:** Admin portals for inventory management, manufacturing resources planning, and operations tracking.

## Major Features
*   **Layout-Aware Document Parser:** A component parsing PDFs utilizing visual models to preserve reading order, columns, and tables.
*   **Hybrid Document Pipeline:** Fully integrated OCR, metadata indexing, semantic retrieval, and vector search database uploads.
*   **Shared UI Component Library:** Reusable modular dashboard cards, graphs, and control boards for multiple enterprise views.
*   **End-to-End ERP Finance Module:** Full-stack modules tracking transactions and invoicing, built with React, Node.js/Express, and MySQL.

## Architecture
*   **Document Processor:** Utilizes Python-based ingestion microservices with `Docling Layout-Heron`, `pdfplumber`, and `Tesseract OCR` pushing chunks and embeddings to `ChromaDB`.
*   **Web Portal:** Decoupled architecture with a React.js client communicating via HTTP REST APIs and WebSockets to an Express.js server, which coordinates with AI microservices.

## Challenges
*   **Multi-Column layout scrambled reading orders:** Standard text extractors read text left-to-right across columns.
    *   *Solution:* Integrated visual segmentation models (Docling Layout-Heron) to extract layout bounding boxes and reconstruct columns sequentially.
*   **Evaluation subjectivity:** Verifying RAG updates was highly manual and subjective.
    *   *Solution:* Implemented the RAGAS framework to run automated benchmarks for correctness, faithfulness, and context retrieval precision.

## Impact
*   Improved answering precision and accuracy by 30% across 1,000+ complex corporate documents.
*   Accelerated feature release times for dashboard widgets by 40% using unified frontend UI packages.

## Things Learned
*   Building hybrid pipelines merging traditional parsing with layout visual intelligence models.
*   Applying standardized metrics (RAGAS) to benchmark LLM generation quality objectively.
*   Designing robust WebSocket systems for real-time extraction logs and UI status updates.

## Interesting Bugs
*   *The Page Scrambling Bug:* During initial test runs on double-column PDFs, headers and paragraphs merged, causing vector chunks to have half-sentences from column A and column B. This caused semantic retrieval to return completely unrelated chunks.
    *   *Fix:* Configured `Docling Layout-Heron` to detect bounding boxes first and chunk *within* each recognized text box instead of doing simple spatial string splitting.

## Metrics
*   **30%** improvement in answer relevance.
*   **1,000+** enterprise documents processed.
*   **10+** enterprise dashboards powered by shared UI elements.
*   **40%** faster feature delivery of dashboard views.

## Leadership
*   Led the design and end-to-end delivery of the Enterprise AI Document Processing Platform.
*   Mentored dashboard engineers on React UI component reuse and standard state management.

## Ownership
*   Complete ownership of the ingestion pipeline (OCR -> Layout Detection -> Vector Chunking).
*   Custodian of the custom RAG evaluation framework.
*   End-to-end design, implementation, and deployment of ERP financial modules (database, backend APIs, and frontend dashboard).
