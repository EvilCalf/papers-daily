## 基本信息

- **标题**: NeuroSeg Meets DINOv3: Transferring 2D Self-Supervised Visual Priors to 3D Neuron Segmentation via DINOv3 Initialization
- **作者**: Yik San Cheng, Runkai Zhao, Weidong Cai
- **ArXiv ID**: 2603.23104v1
- **发布日期**: 2026-03-24
- **主分类**: cs.CV
- **分类**: cs.CV
- **摘要**: 2D visual foundation models, such as DINOv3, a self-supervised model trained on large-scale natural images, have demonstrated strong zero-shot generalization, capturing both rich global context and fine-grained structural cues. However, an analogous 3D foundation model for downstream volumetric neuroimaging remains lacking, largely due to the challenges of 3D image acquisition and the scarcity of high-quality annotations. To address this gap, we propose to adapt the 2D visual representations learned by DINOv3 to a 3D biomedical segmentation model, enabling more data-efficient and morphologically faithful neuronal reconstruction. Specifically, we design an inflation-based adaptation strategy that inflates 2D filters into 3D operators, preserving semantic priors from DINOv3 while adapting to 3D neuronal volume patches. In addition, we introduce a topology-aware skeleton loss to explicitly enforce structural fidelity of graph-based neuronal arbor reconstruction. Extensive experiments on four neuronal imaging datasets, including two from BigNeuron and two public datasets, NeuroFly and CWMBS, demonstrate consistent improvements in reconstruction accuracy over SoTA methods, with average gains of 2.9% in Entire Structure Average, 2.8% in Different Structure Average, and 3.8% in Percentage of Different Structure. Code: https://github.com/yy0007/NeurINO.
- **PDF 链接**: https://arxiv.org/pdf/2603.23104v1
