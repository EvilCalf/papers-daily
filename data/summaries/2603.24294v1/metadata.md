## 基本信息

- **标题**: VERIA: Verification-Centric Multimodal Instance Augmentation for Long-Tailed 3D Object Detection
- **作者**: Jumin Lee, Siyeong Lee, Namil Kim, Sung-Eui Yoon
- **ArXiv ID**: 2603.24294v1
- **发布日期**: 2026-03-25
- **主分类**: cs.CV
- **分类**: cs.CV
- **摘要**: Long-tail distributions in driving datasets pose a fundamental challenge for 3D perception, as rare classes exhibit substantial intra-class diversity yet available samples cover this variation space only sparsely. Existing instance augmentation methods based on copy-paste or asset libraries improve rare-class exposure but are often limited in fine-grained diversity and scene-context placement. We propose VERIA, an image-first multimodal augmentation framework that synthesizes synchronized RGB--LiDAR instances using off-the-shelf foundation models and curates them with sequential semantic and geometric verification. This verification-centric design tends to select instances that better match real LiDAR statistics while spanning a wider range of intra-class variation. Stage-wise yield decomposition provides a log-based diagnostic of pipeline reliability. On nuScenes and Lyft, VERIA improves rare-class 3D object detection in both LiDAR-only and multimodal settings. Our code is available at https://sgvr.kaist.ac.kr/VERIA/.
- **PDF 链接**: https://arxiv.org/pdf/2603.24294v1
