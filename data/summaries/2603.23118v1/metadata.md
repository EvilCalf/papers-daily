## 基本信息

- **标题**: SMSP: A Plug-and-Play Strategy of Multi-Scale Perception for MLLMs to Perceive Visual Illusions
- **作者**: Jinzhe Tu, Ruilei Guo, Zihan Guo, Junxiao Yang, Shiyao Cui et al.
- **ArXiv ID**: 2603.23118v1
- **发布日期**: 2026-03-24
- **主分类**: cs.CV
- **分类**: cs.CV, cs.MM
- **摘要**: Recent works have shown that Multimodal Large Language Models (MLLMs) are highly vulnerable to hidden-pattern visual illusions, where the hidden content is imperceptible to models but obvious to humans. This deficiency highlights a perceptual misalignment between current MLLMs and humans, and also introduces potential safety concerns. To systematically investigate this failure, we introduce IlluChar, a comprehensive and challenging illusion dataset, and uncover a key underlying mechanism for the models' failure: high-frequency attention bias, where the models are easily distracted by high-frequency background textures in illusion images, causing them to overlook hidden patterns. To address the issue, we propose the Strategy of Multi-Scale Perception (SMSP), a plug-and-play framework that aligns with human visual perceptual strategies. By suppressing distracting high-frequency backgrounds, SMSP generates images closer to human perception. Our experiments demonstrate that SMSP significantly improves the performance of all evaluated MLLMs on illusion images, for instance, increasing the accuracy of Qwen3-VL-8B-Instruct from 13.0% to 84.0%. Our work provides novel insights into MLLMs' visual perception, and offers a practical and robust solution to enhance it. Our code is publicly available at https://github.com/Tujz2023/SMSP.
- **PDF 链接**: https://arxiv.org/pdf/2603.23118v1
