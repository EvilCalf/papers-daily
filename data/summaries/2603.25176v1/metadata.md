## 基本信息

- **标题**: Prompt Attack Detection with LLM-as-a-Judge and Mixture-of-Models
- **作者**: Hieu Xuan Le, Benjamin Goh, Quy Anh Tang
- **ArXiv ID**: 2603.25176v1
- **发布日期**: 2026-03-26
- **主分类**: cs.CL
- **分类**: cs.CL
- **摘要**: Prompt attacks, including jailbreaks and prompt injections, pose a critical security risk to Large Language Model (LLM) systems. In production, guardrails must mitigate these attacks under strict low-latency constraints, resulting in a deployment gap in which lightweight classifiers and rule-based systems struggle to generalize under distribution shift, while high-capacity LLM-based judges remain too slow or costly for live enforcement. In this work, we examine whether lightweight, general-purpose LLMs can reliably serve as security judges under real-world production constraints. Through careful prompt and output design, lightweight LLMs are guided through a structured reasoning process involving explicit intent decomposition, safety-signal verification, harm assessment, and self-reflection. We evaluate our method on a curated dataset combining benign queries from real-world chatbots with adversarial prompts generated via automated red teaming (ART), covering diverse and evolving patterns. Our results show that general-purpose LLMs, such as gemini-2.0-flash-lite-001, can serve as effective low-latency judges for live guardrails. This configuration is currently deployed in production as a centralized guardrail service for public service chatbots in Singapore. We additionally evaluate a Mixture-of-Models (MoM) setting to assess whether aggregating multiple LLM judges improves prompt-attack detection performance relative to single-model judges, with only modest gains observed.
- **PDF 链接**: https://arxiv.org/pdf/2603.25176v1
