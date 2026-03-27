## 基本信息

- **标题**: SafeMath: Inference-time Safety improves Math Accuracy
- **作者**: Sagnik Basu, Subhrajit Mitra, Aman Juneja, Somnath Banerjee, Rima Hazra et al.
- **ArXiv ID**: 2603.25201v1
- **发布日期**: 2026-03-26
- **主分类**: cs.CL
- **分类**: cs.CL, cs.CY
- **摘要**: Recent research points toward LLMs being manipulated through adversarial and seemingly benign inputs, resulting in harmful, biased, or policy-violating outputs. In this paper, we study an underexplored issue concerning harmful and toxic mathematical word problems. We show that math questions, particularly those framed as natural language narratives, can serve as a subtle medium for propagating biased, unethical, or psychologically harmful content, with heightened risks in educational settings involving children. To support a systematic study of this phenomenon, we introduce ToxicGSM, a dataset of 1.9k arithmetic problems in which harmful or sensitive context is embedded while preserving mathematically well-defined reasoning tasks. Using this dataset, we audit the behaviour of existing LLMs and analyse the trade-offs between safety enforcement and mathematical correctness. We further propose SafeMath -- a safety alignment technique that reduces harmful outputs while maintaining, and in some cases improving, mathematical reasoning performance. Our results highlight the importance of disentangling linguistic harm from math reasoning and demonstrate that effective safety alignment need not come at the cost of accuracy. We release the source code and dataset at https://github.com/Swagnick99/SafeMath/tree/main.
- **PDF 链接**: https://arxiv.org/pdf/2603.25201v1
