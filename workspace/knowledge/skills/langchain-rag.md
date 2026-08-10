# Skill: LangChain & Retrieval-Augmented Generation (RAG)

## What do you know?
*   Setting up structured LLM chains, agents, and custom tools utilizing LangChain frameworks.
*   Document processing workflows: layout-aware chunking, overlap calculations, metadata insertion, and visual document segmenting (Docling Layout-Heron).
*   Vector search dynamics, semantic similarity ranking, and distance metrics (cosine, inner product, L2).
*   Automated quantitative evaluations of RAG pipelines using RAGAS (measuring faithfulness, correctness, hallucination metrics).

## Where have you used it?
*   **Nestbotics:** Architected the layout-aware RAG processing engine and evaluations framework.
*   **Projects:** Designed and published the Enterprise Layout-Aware RAG Platform.

## Confidence Level
*   **Advanced / Expert (9/10)** - Extensive hands-on experience structuring, evaluating, and improving non-trivial corporate RAG setups.

## Projects
*   [Enterprise Layout-Aware RAG Platform](file:///C:/Users/Abhishek%20Tripathi/Desktop/Ops/career-ops/workspace/knowledge/projects/layout-aware-rag.md)

## Interview Topics
*   **The Chunking Strategy Trade-off:** How chunk sizes and overlap tokens affect vector database indexing, matching precision, and LLM context limits.
*   **Evaluation Paradigms:** Explaining the difference between Faithfulness (is the answer based on context?) and Answer Relevance (does it answer the prompt?) in RAGAS.
*   **Layout-Aware Parsers:** Why traditional text-extractors fail on double-column PDFs and how visual parsing (Docling) resolves it.

## Things you're currently learning?
*   Graph RAG implementations (using Neo4j) to build structured relationship maps from raw text before semantic retrieval.
*   Applying reranker models (e.g. Cohere Rerank, BGE-Reranker) to filter initial vector results before prompting the LLM.
