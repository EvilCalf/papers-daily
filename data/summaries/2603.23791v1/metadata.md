## 基本信息

- **标题**: The Cognitive Firewall:Securing Browser Based AI Agents Against Indirect Prompt Injection Via Hybrid Edge Cloud Defense
- **作者**: Qianlong Lan, Anuj Kaul
- **ArXiv ID**: 2603.23791v1
- **发布日期**: 2026-03-24
- **主分类**: cs.CR
- **分类**: cs.CR, cs.AI
- **摘要**: Deploying large language models (LLMs) as autonomous browser agents exposes a significant attack surface in the form of Indirect Prompt Injection (IPI). Cloud-based defenses can provide strong semantic analysis, but they introduce latency and raise privacy concerns. We present the Cognitive Firewall, a three-stage split-compute architecture that distributes security checks across the client and the cloud. The system consists of a local visual Sentinel, a cloud-based Deep Planner, and a deterministic Guard that enforces execution-time policies. Across 1,000 adversarial samples, edge-only defenses fail to detect 86.9% of semantic attacks. In contrast, the full hybrid architecture reduces the overall attack success rate (ASR) to below 1% (0.88% under static evaluation and 0.67% under adaptive evaluation), while maintaining deterministic constraints on side-effecting actions. By filtering presentation-layer attacks locally, the system avoids unnecessary cloud inference and achieves an approximately 17,000x latency advantage over cloud-only baselines. These results indicate that deterministic enforcement at the execution boundary can complement probabilistic language models, and that split-compute provides a practical foundation for securing interactive LLM agents.
- **PDF 链接**: https://arxiv.org/pdf/2603.23791v1
