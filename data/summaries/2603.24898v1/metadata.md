## 基本信息

- **标题**: Sovereign AI at the Front Door of Care: A Physically Unidirectional Architecture for Secure Clinical Intelligence
- **作者**: Vasu Srinivasan, Dhriti Vasu
- **ArXiv ID**: 2603.24898v1
- **发布日期**: 2026-03-26
- **主分类**: cs.CR
- **分类**: cs.CR, cs.AI, cs.NI
- **摘要**: We present a Sovereign AI architecture for clinical triage in which all inference is performed on-device and inbound data is delivered via a physically unidirectional channel, implemented using receive-only broadcast infrastructure or certified hardware data diodes, with no return path to any external network. This design removes the network-mediated attack surface by construction, rather than attempting to secure it through software controls.   The system performs conversational symptom intake, integrates device-captured vitals, and produces structured, triage-aligned clinical records at the point of care. We formalize the security properties of receiver-side unidirectionality and show that the architecture is transport-agnostic across broadcast and diode-enforced deployments. We further analyze threat models, enforcement mechanisms, and deployment configurations, demonstrating how physical one-way data flow enables high-assurance operation in both resource-constrained and high-risk environments.   This work positions physically unidirectional channels as a foundational primitive for sovereign, on-device clinical intelligence at the front door of care.
- **PDF 链接**: https://arxiv.org/pdf/2603.24898v1
