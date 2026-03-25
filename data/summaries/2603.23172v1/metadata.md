## 基本信息

- **标题**: From Synthetic to Native: Benchmarking Multilingual Intent Classification in Logistics Customer Service
- **作者**: Haoyu He, Jinyu Zhuang, Haoran Chu, Shuhang Yu,  J et al.
- **ArXiv ID**: 2603.23172v1
- **发布日期**: 2026-03-24
- **主分类**: cs.CL
- **分类**: cs.CL
- **摘要**: Multilingual intent classification is central to customer-service systems on global logistics platforms, where models must process noisy user queries across languages and hierarchical label spaces. Yet most existing multilingual benchmarks rely on machine-translated text, which is typically cleaner and more standardized than native customer requests and can therefore overestimate real-world robustness. We present a public benchmark for hierarchical multilingual intent classification constructed from real logistics customer-service logs. The dataset contains approximately 30K de-identified, stand-alone user queries curated from 600K historical records through filtering, LLM-assisted quality control, and human verification, and is organized into a two-level taxonomy with 13 parent and 17 leaf intents. English, Spanish, and Arabic are included as seen languages, while Indonesian, Chinese, and additional test-only languages support zero-shot evaluation. To directly measure the gap between synthetic and real evaluation, we provide paired native and machine-translated test sets and benchmark multilingual encoders, embedding models, and small language models under flat and hierarchical protocols. Results show that translated test sets substantially overestimate performance on noisy native queries, especially for long-tail intents and cross-lingual transfer, underscoring the need for more realistic multilingual intent benchmarks.
- **PDF 链接**: https://arxiv.org/pdf/2603.23172v1
