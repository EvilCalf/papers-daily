## 基本信息

- **标题**: Automatic Segmentation of 3D CT scans with SAM2 using a zero-shot approach
- **作者**: Miquel Lopez Escoriza, Pau Amargant Alvarez
- **ArXiv ID**: 2603.23116v1
- **发布日期**: 2026-03-24
- **主分类**: cs.CV
- **分类**: cs.CV
- **摘要**: Foundation models for image segmentation have shown strong generalization in natural images, yet their applicability to 3D medical imaging remains limited. In this work, we study the zero-shot use of Segment Anything Model 2 (SAM2) for automatic segmentation of volumetric CT data, without any fine-tuning or domain-specific training. We analyze how SAM2 should be applied to CT volumes and identify its main limitation: the lack of inherent volumetric awareness. To address this, we propose a set of inference-alone architectural and procedural modifications that adapt SAM2's video-based memory mechanism to 3D data by treating CT slices as ordered sequences. We conduct a systematic ablation study on a subset of 500 CT scans from the TotalSegmentator dataset to evaluate prompt strategies, memory propagation schemes and multi-pass refinement. Based on these findings, we select the best-performing configuration and report final results on a bigger sample of the TotalSegmentator dataset comprising 2,500 CT scans. Our results show that, even with frozen weights, SAM2 can produce coherent 3D segmentations when its inference pipeline is carefully structured, demonstrating the feasibility of a fully zero-shot approach for volumetric medical image segmentation.
- **PDF 链接**: https://arxiv.org/pdf/2603.23116v1
