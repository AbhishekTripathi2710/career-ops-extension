# Interview Story: Failure / Mistake

## Situation
During the early stage of building the document parsing pipeline at Nestbotics, I ran an initial test run over double-column PDF reports. The standard text extractor I was using read lines straight across the page, blindly merging paragraph A (column 1) with paragraph B (column 2).

## Task
The resulting vector chunks contained scrambled sentences containing fragments of completely different topics, resulting in poor semantic database retrieval and hallucinated answers from the LLM. I had failed to anticipate that spatial layout structure mattered as much as raw character sequences.

## Action
1.  **Acknowledge & Halt:** I flagged the layout parsing failure to the team, explaining why the simple text splitter pipeline was failing.
2.  **Research Visual Layouts:** Researched document layout analysis (DLA) models. I discovered that we needed visual boundary box detection to segment pages before running text extraction.
3.  **Refactor with Layout Models:** Rewrote the ingestion pipeline to integrate `Docling Layout-Heron`. The code was modified to detect layout areas first, sort text blocks vertically *within* column boundary boxes, and chunk them as separate, self-contained paragraphs.

## Result
*   Fixed the column scrambled reading issue completely.
*   The refactored layout-aware parser boosted RAG answers accuracy and retrieval relevance by **30%**.
*   Learned a critical engineering lesson: in AI and LLM development, data preprocessing and understanding data format structures is often 90% of the battle, and standard text tools are rarely enough for complex layouts.
