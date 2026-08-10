# Project: Enterprise Layout-Aware RAG Platform

## Problem
Standard Retrieval-Augmented Generation (RAG) pipelines extract raw text sequentially from documents. This breaks layout patterns (like double columns, visual sidebars, headers, and footers), leading to fragmented sentence splits. The resulting vector search matches text chunks that lack context or are visually disjointed, which causes the LLM to synthesize hallucinations or fail to retrieve the right answers entirely.

## Motivation
To build an enterprise-grade document intelligence system that reads and queries PDFs similarly to a human—understanding the visual structure first (capturing layouts, tables, reading orders) before converting them into semantic vector chunks for advanced querying.

## Architecture
The system follows a pipeline architecture:
1.  **Ingestion:** Python-based document uploads.
2.  **Layout Parsing:** `Docling Layout-Heron` predicts structural zones (headings, columns, tables).
3.  **OCR Processing:** OCR is applied selectively via `Tesseract OCR` and `pdfplumber` for text within isolated structural zones to prevent merging text across different columns.
4.  **Vector Indexing:** Structurally-tagged chunks are vectorized using sentence embedding models and saved to `ChromaDB`.
5.  **LLM Generation:** Queries search the vector database and retrieve layout-aware context to formulate highly relevant prompts for `Llama 3`.
6.  **Continuous Evaluation:** Automated tests evaluate pipeline performance using `RAGAS`.

## Tech Stack
*   **Core:** Python, LangChain
*   **Layout Parser:** Docling Layout-Heron
*   **OCR & Text Extractors:** Tesseract OCR, pdfplumber
*   **Vector DB:** ChromaDB
*   **LLM Model:** Llama 3
*   **RAG Evaluation:** RAGAS

## Database
*   **ChromaDB:** Local vector database storing 384-dimensional dense vectors representing layout-aligned text chunks, along with metadata (document source, page number, bounding box coords, header parent).

## API Design
An internal Python service exposing REST endpoints:
*   `POST /api/v1/documents/upload` - Upload PDF and trigger async layout parser.
*   `POST /api/v1/query` - Perform semantic search, augment prompt, and return Llama 3 generation.
*   `GET /api/v1/evaluation/report` - Get RAGAS metrics report (faithfulness, answer relevance).

## Authentication
Token-based authentication simulating enterprise IAM endpoints.

## Deployment
Docker container orchestration with CPU/GPU bindings.

## Challenges
*   **Table Extraction:** Extracting tabular data without losing rows and column alignments.
    *   *Solution:* Integrated `pdfplumber` tables detector for native digital PDFs, fallback to `Docling Layout-Heron` visual table segmenters for scanned documents, converting table cells into structured HTML representation before embedding.
*   **OCR Speed & Resource Limits:** Processing large enterprise files (1,000+ docs) sequentially was slow.
    *   *Solution:* Implemented multi-processing queues in Python, scaling extraction workers to run page parsing in parallel.

## Results
*   **30%** increase in RAG answer relevance.
*   Successful processing and indexing of **1,000+** corporate files.
*   High scores across RAGAS benchmark indicators: Faithfulness (0.88), Answer Relevance (0.91), Context Recall (0.86).
*   Published a popular technical blog outlining Layout-Aware RAG paradigms.

## Future Improvements
*   Support multimodal querying where the visual snapshot of tables/images is passed to a Vision-LLM instead of text serialization.
*   Adding support for hybrid vector search (combining dense vector search with BM25 keyword matching).

## Resume-Worthy Achievements
*   Architected a production-grade Layout-Aware RAG pipeline for enterprise documents using OCR, semantic retrieval, vector search, and LLMs.
*   Engineered a hybrid document parsing pipeline with Docling Layout-Heron, Tesseract OCR, and pdfplumber for structured information extraction.
*   Implemented an automated RAG evaluation framework with RAGAS to benchmark faithfulness, retrieval quality, and hallucination rates.
*   Published a technical blog on enterprise Layout-Aware RAG architecture, implementation, and evaluation.

## Interview Talking Points
*   *Why did you use Docling Layout-Heron over simple LangChain text splitters?* Plain splitters destroy layout context. A paragraph on column 1 will merge with column 2. Layout-Heron reconstructs the reading order correctly.
*   *How did you measure the system's accuracy?* Rather than relying on vibe-checks, I integrated the RAGAS framework which outputs concrete metrics like Faithfulness and Context Precision against a golden dataset.
