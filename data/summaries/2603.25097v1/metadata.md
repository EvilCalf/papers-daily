## 基本信息

- **标题**: ElephantBroker: A Knowledge-Grounded Cognitive Runtime for Trustworthy AI Agents
- **作者**: Cristian Lupascu, Alexandru Lupascu
- **ArXiv ID**: 2603.25097v1
- **发布日期**: 2026-03-26
- **主分类**: cs.AI
- **分类**: cs.AI
- **摘要**: Large Language Model based agents increasingly operate in high stakes, multi turn settings where factual grounding is critical, yet their memory systems typically rely on flat key value stores or plain vector retrieval with no mechanism to track the provenance or trustworthiness of stored knowledge. We present ElephantBroker, an open source cognitive runtime that unifies a Neo4j knowledge graph with a Qdrant vector store through the Cognee SDK to provide durable, verifiable agent memory. The system implements a complete cognitive loop (store, retrieve, score, compose, protect, learn) comprising a hybrid five source retrieval pipeline, an eleven dimension competitive scoring engine for budget constrained context assembly, a four state evidence verification model, a five stage context lifecycle with goal aware assembly and continuous compaction, a six layer cheap first guard pipeline for safety enforcement, an AI firewall providing enforceable tool call interception and multi tier safety scanning, a nine stage consolidation engine that strengthens useful patterns while decaying noise, and a numeric authority model governing multi organization identity with hierarchical access control. Architectural validation through a comprehensive test suite of over 2,200 tests spanning unit, integration, and end to end levels confirms subsystem correctness. The modular design supports three deployment tiers, five profile presets with inheritance, multi gateway isolation, and a management dashboard for human oversight, enabling configurations from lightweight memory only agents to full cognitive runtimes with enterprise grade safety and auditability.
- **PDF 链接**: https://arxiv.org/pdf/2603.25097v1
