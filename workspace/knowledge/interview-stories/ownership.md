# Interview Story: Ownership

## Situation
At Nestbotics, we needed to build an enterprise-level Retrieval-Augmented Generation (RAG) platform to parse and query thousands of complex layout documents (like financial sheets, manuals, and reports). The system was experiencing low accuracy because standard parsers scrambled columns and ignored visual elements. There was no clear blueprint for handling layout structures.

## Task
I took full ownership of designing, engineering, and launching the layout-aware extraction engine. My goal was to build a pipeline that preserved document structures, indexed them correctly into a vector database, and established a quantitative evaluation loop.

## Action
1.  **Research & Technology Selection:** Evaluated several parsing libraries, deciding on a hybrid model: `Docling Layout-Heron` for visual zoning (columns, headings, tables), `pdfplumber` for structured PDF content, and `Tesseract OCR` for image-based pages.
2.  **Pipeline Engineering:** Built a Python ingestion engine that processed pages, segmented them into layout-aware blocks, generated semantic embeddings, and loaded them with layout coordinate metadata into `ChromaDB`.
3.  **Benchmarking Loop:** Integrated the `RAGAS` framework, creating automated validation scripts to benchmark retrieval recall and generation correctness, eliminating subjective "vibe-checks."

## Result
*   Successfully delivered the core parsing platform on schedule.
*   Achieved a **30%** improvement in answer relevance score.
*   Processed and indexed over **1,000+** complex documents with verified RAGAS metrics (Faithfulness at 0.88, Answer Relevance at 0.91).
*   Established a scalable, reusable RAG platform architecture that other developers could easily write plugins for.
