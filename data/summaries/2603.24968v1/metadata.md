## 基本信息

- **标题**: Subject-Specific Low-Field MRI Synthesis via a Neural Operator
- **作者**: Ziqi Gao, Nicha Dvornek, Xiaoran Zhang, Gigi Galiana, Hemant Tagare et al.
- **ArXiv ID**: 2603.24968v1
- **发布日期**: 2026-03-26
- **主分类**: eess.IV
- **分类**: eess.IV, cs.AI
- **摘要**: Low-field (LF) magnetic resonance imaging (MRI) improves accessibility and reduces costs but generally has lower signal-to-noise ratios and degraded contrast compared to high field (HF) MRI, limiting its clinical utility. Simulating LF MRI from HF MRI enables virtual evaluation of novel imaging devices and development of LF algorithms. Existing low field simulators rely on noise injection and smoothing, which fail to capture the contrast degradation seen in LF acquisitions. To this end, we introduce an end-to-end LF-MRI synthesis framework that learns HF to LF image degradation directly from a small number of paired HF-LF MRIs. Specifically, we introduce a novel HF to LF coordinate-image decoupled neural operator (H2LO) to model the underlying degradation process, and tailor it to capture high-frequency noise textures and image structure. Experimental results in T1w and T2w MRI demonstrate that H2LO produces more faithful simulated low-field images than existing parameterized noise synthesis models and popular image-to-image translation models. Furthermore, it improves performance in downstream image enhancement tasks, showcasing its potential to enhance LF MRI diagnostic capabilities.
- **PDF 链接**: https://arxiv.org/pdf/2603.24968v1
