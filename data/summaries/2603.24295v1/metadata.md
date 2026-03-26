## 基本信息

- **标题**: RS-SSM: Refining Forgotten Specifics in State Space Model for Video Semantic Segmentation
- **作者**: Kai Zhu, Zhenyu Cui, Zehua Zang, Jiahuan Zhou
- **ArXiv ID**: 2603.24295v1
- **发布日期**: 2026-03-25
- **主分类**: cs.CV
- **分类**: cs.CV
- **摘要**: Recently, state space models have demonstrated efficient video segmentation through linear-complexity state space compression. However, Video Semantic Segmentation (VSS) requires pixel-level spatiotemporal modeling capabilities to maintain temporal consistency in segmentation of semantic objects. While state space models can preserve common semantic information during state space compression, the fixed-size state space inevitably forgets specific information, which limits the models' capability for pixel-level segmentation. To tackle the above issue, we proposed a Refining Specifics State Space Model approach (RS-SSM) for video semantic segmentation, which performs complementary refining of forgotten spatiotemporal specifics. Specifically, a Channel-wise Amplitude Perceptron (CwAP) is designed to extract and align the distribution characteristics of specific information in the state space. Besides, a Forgetting Gate Information Refiner (FGIR) is proposed to adaptively invert and refine the forgetting gate matrix in the state space model based on the specific information distribution. Consequently, our RS-SSM leverages the inverted forgetting gate to complementarily refine the specific information forgotten during state space compression, thereby enhancing the model's capability for spatiotemporal pixel-level segmentation. Extensive experiments on four VSS benchmarks demonstrate that our RS-SSM achieves state-of-the-art performance while maintaining high computational efficiency. The code is available at https://github.com/zhoujiahuan1991/CVPR2026-RS-SSM.
- **PDF 链接**: https://arxiv.org/pdf/2603.24295v1
