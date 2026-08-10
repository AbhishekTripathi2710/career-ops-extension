# Interview Story: Learning

## Situation
At Nestbotics, I was tasked with improving our document RAG pipeline. Although I understood basic RAG pipelines (chunking and vector search), I had no experience with visual layout analysis models or quantitative evaluation frameworks. The team needed a solution quickly to address customer complaints about incorrect answers.

## Task
To rapidly learn visual layout segmentation concepts, evaluate layout parsing libraries, and implement a testing framework (RAGAS) within two weeks to measure our progress.

## Action
1.  **Immersive Research:** Spent my first few days reading research papers on document layout analysis and analyzing libraries like LayoutParser and Docling.
2.  **Hands-on Prototyping:** Built small prototypes using `Docling Layout-Heron` to see how it parsed two-column PDFs and tables.
3.  **Implement Evaluation Loop:** Studied the RAGAS documentation, set up a test dataset of 50 sample questions, and wrote a Python evaluation script to calculate Faithfulness, Answer Relevance, and Context Precision.

## Result
*   Successfully integrated `Docling Layout-Heron` and `RAGAS` into our pipeline on time.
*   The layout-aware parsing approach boosted answer relevance scores by **30%**.
*   Our team now has a standardized, automated evaluation process for all future RAG changes, replacing subjective feedback with concrete metrics.
*   Learned how to quickly research, prototype, and implement new technologies under pressure.
