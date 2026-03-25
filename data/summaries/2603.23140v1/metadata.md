## 基本信息

- **标题**: DAK-UCB: Diversity-Aware Prompt Routing for LLMs and Generative Models
- **作者**: Donya Jafari, Farzan Farnia
- **ArXiv ID**: 2603.23140v1
- **发布日期**: 2026-03-24
- **主分类**: cs.LG
- **分类**: cs.LG
- **摘要**: The expansion of generative AI and LLM services underscores the growing need for adaptive mechanisms to select an appropriate available model to respond to a user's prompts. Recent works have proposed offline and online learning formulations to identify the optimal generative AI model for an input prompt, based solely on maximizing prompt-based fidelity evaluation scores, e.g., CLIP-Score in text-to-image generation. However, such fidelity-based selection methods overlook the diversity of generated outputs, and hence, they can fail to address potential diversity shortcomings in the generated responses. In this paper, we introduce the Diversity-Aware Kernelized Upper Confidence Bound (DAK-UCB) method as a contextual bandit algorithm for the online selection of generative models with diversity considerations. The proposed DAK-UCB method incorporates both fidelity and diversity-related metrics into the selection process. We design this framework based on prompt-aware diversity score functions that decompose to a two-sample-based expectation over prompt-output pairs in the previous generation rounds. Specifically, we illustrate the application of our framework using joint kernel distance and kernel entropy measures. Our experimental results demonstrate the effectiveness of DAK-UCB in promoting diversity-aware model selection while maintaining fidelity in the generations for a sequence of prompts. The code is available at https://github.com/Donya-Jafari/DAK-UCB.
- **PDF 链接**: https://arxiv.org/pdf/2603.23140v1
