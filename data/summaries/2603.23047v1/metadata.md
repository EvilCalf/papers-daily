## 基本信息

- **标题**: Parametric Knowledge and Retrieval Behavior in RAG Fine-Tuning for Electronic Design Automation
- **作者**: Julian Oestreich, Maximilian Bley, Frank Binder, Lydia Müller, Maksym Sydorenko et al.
- **ArXiv ID**: 2603.23047v1
- **发布日期**: 2026-03-24
- **主分类**: cs.CL
- **分类**: cs.CL, cs.AI, cs.CE
- **摘要**: Retrieval-Augmented Generation (RAG) fine-tuning has shown substantial improvements over vanilla RAG, yet most studies target document question answering and often rely on standard NLP metrics that can obscure factual differences. We evaluate RAG fine-tuning for long-form text generation in electronic design automation, adapting a 7B model under five context augmentation strategies with varying retrieval conditions. We introduce TriFEX, a human-validated, triple-based evaluation pipeline that attributes generated claims to their origin-user query, context and reference-and propose Parametric Knowledge Precision (PKP), which isolates internalized knowledge by filtering out claims leaked in the prompt. We show that ROUGE and BERTScore fail to detect factual differences that our triple-based evaluation reveals. Additionally, we demonstrate that an existing metric for knowledge internalization is retrieva-sensitive, with about 75% of its cross-condition variance driven by changes in the rate at which internal knowledge is expressed (PR), rather than by changes in its actual correctness (PKP). The fine-tuned 7B variants outperform a 72B baseline on most metrics, further showing generalization across conditions and on a related benchmark. These results underscore the limitations of available metrics in RAG evaluation and show that smaller models could be reasonably well adapted to specialized tasks for cost-efficient, on-premises deployment.
- **PDF 链接**: https://arxiv.org/pdf/2603.23047v1
