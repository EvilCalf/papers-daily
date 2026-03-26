## 基本信息

- **标题**: ReqFusion: A Multi-Provider Framework for Automated PEGS Analysis Across Software Domains
- **作者**: Muhammad Khalid, Manuel Oriol, Yilmaz Uygun
- **ArXiv ID**: 2603.23482v1
- **发布日期**: 2026-03-24
- **主分类**: cs.SE
- **分类**: cs.SE, cs.AI
- **摘要**: Requirements engineering is a vital, yet labor-intensive, stage in the software development process. This article introduces ReqFusion: an AI-enhanced system that automates the extraction, classification, and analysis of software requirements utilizing multiple Large Language Model (LLM) providers. The architecture of ReqFusion integrates OpenAI GPT, Anthropic Claude, and Groq models to extract functional and non-functional requirements from various documentation formats (PDF, DOCX, and PPTX) in academic, industrial, and tender proposal contexts. The system uses a domain-independent extraction method and generates requirements following the Project, Environment, Goal, and System (PEGS) approach introduced by Bertrand Meyer. The main idea is that, because the PEGS format is detailed, LLMs have more information and cues about the requirements, producing better results than a simple generic request. An ablation study confirms this hypothesis: PEGS-guided prompting achieves an F1 score of 0.88, compared to 0.71 for generic prompting under the same multi-provider configuration. The evaluation used 18 real-world documents to generate 226 requirements through automated classification, with 54.9% functional and 45.1% nonfunctional across academic, business, and technical domains. An extended evaluation on five projects with 1,050 requirements demonstrated significant improvements in extraction accuracy and a 78% reduction in analysis time compared to manual methods. The multi-provider architecture enhances reliability through model consensus and fallback mechanisms, while the PEGS-based approach ensures comprehensive coverage of all requirement categories.
- **PDF 链接**: https://arxiv.org/pdf/2603.23482v1
