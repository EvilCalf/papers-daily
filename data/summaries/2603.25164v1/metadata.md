## 基本信息

- **标题**: PIDP-Attack: Combining Prompt Injection with Database Poisoning Attacks on Retrieval-Augmented Generation Systems
- **作者**: Haozhen Wang, Haoyue Liu, Jionghao Zhu, Zhichao Wang, Yongxin Guo et al.
- **ArXiv ID**: 2603.25164v1
- **发布日期**: 2026-03-26
- **主分类**: cs.CR
- **分类**: cs.CR, cs.AI
- **摘要**: Large Language Models (LLMs) have demonstrated remarkable performance across a wide range of applications. However, their practical deployment is often hindered by issues such as outdated knowledge and the tendency to generate hallucinations. To address these limitations, Retrieval-Augmented Generation (RAG) systems have been introduced, enhancing LLMs with external, up-to-date knowledge sources. Despite their advantages, RAG systems remain vulnerable to adversarial attacks, with data poisoning emerging as a prominent threat. Existing poisoning-based attacks typically require prior knowledge of the user's specific queries, limiting their flexibility and real-world applicability. In this work, we propose PIDP-Attack, a novel compound attack that integrates prompt injection with database poisoning in RAG. By appending malicious characters to queries at inference time and injecting a limited number of poisoned passages into the retrieval database, our method can effectively manipulate LLM response to arbitrary query without prior knowledge of the user's actual query. Experimental evaluations across three benchmark datasets (Natural Questions, HotpotQA, MS-MARCO) and eight LLMs demonstrate that PIDP-Attack consistently outperforms the original PoisonedRAG. Specifically, our method improves attack success rates by 4% to 16% on open-domain QA tasks while maintaining high retrieval precision, proving that the compound attack strategy is both necessary and highly effective.
- **PDF 链接**: https://arxiv.org/pdf/2603.25164v1
