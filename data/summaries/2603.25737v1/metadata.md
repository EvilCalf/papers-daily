## 基本信息

- **标题**: Training the Knowledge Base through Evidence Distillation and Write-Back Enrichment
- **作者**: Yuxing Lu, Xukai Zhao, Wei Wu, Jinzhuo Wang
- **ArXiv ID**: 2603.25737v1
- **发布日期**: 2026-03-26
- **主分类**: cs.AI
- **分类**: cs.AI, cs.CL, cs.IR
- **摘要**: The knowledge base in a retrieval-augmented generation (RAG) system is typically assembled once and never revised, even though the facts a query requires are often fragmented across documents and buried in irrelevant content. We argue that the knowledge base should be treated as a trainable component and propose WriteBack-RAG, a framework that uses labeled examples to identify where retrieval succeeds, isolate the relevant documents, and distill them into compact knowledge units that are indexed alongside the original corpus. Because the method modifies only the corpus, it can be applied once as an offline preprocessing step and combined with any RAG pipeline. Across four RAG methods, six benchmarks, and two LLM backbones, WriteBack-RAG improves every evaluated setting, with gains averaging +2.14%. Cross-method transfer experiments further show that the distilled knowledge benefits RAG pipelines other than the one used to produce it, confirming that the improvement resides in the corpus itself.
- **PDF 链接**: https://arxiv.org/pdf/2603.25737v1
