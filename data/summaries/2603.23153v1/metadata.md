## 基本信息

- **标题**: VoDaSuRe: A Large-Scale Dataset Revealing Domain Shift in Volumetric Super-Resolution
- **作者**: August Leander Høeg, Sophia Wiinberg Bardenfleth, Hans Martin Kjer, Tim Bjørn Dyrby, Vedrana Andersen Dahl et al.
- **ArXiv ID**: 2603.23153v1
- **发布日期**: 2026-03-24
- **主分类**: cs.CV
- **分类**: cs.CV
- **摘要**: Recent advances in volumetric super-resolution (SR) have demonstrated strong performance in medical and scientific imaging, with transformer- and CNN-based approaches achieving impressive results even at extreme scaling factors. In this work, we show that much of this performance stems from training on downsampled data rather than real low-resolution scans. This reliance on downsampling is partly driven by the scarcity of paired high- and low-resolution 3D datasets. To address this, we introduce VoDaSuRe, a large-scale volumetric dataset containing paired high- and low-resolution scans. When training models on VoDaSuRe, we reveal a significant discrepancy: SR models trained on downsampled data produce substantially sharper predictions than those trained on real low-resolution scans, which smooth fine structures. Conversely, applying models trained on downsampled data to real scans preserves more structure but is inaccurate. Our findings suggest that current SR methods are overstated - when applied to real data, they do not recover structures lost in low-resolution scans and instead predict a smoothed average. We argue that progress in deep learning-based volumetric SR requires datasets with paired real scans of high complexity, such as VoDaSuRe. Our dataset and code are publicly available through: https://augusthoeg.github.io/VoDaSuRe/
- **PDF 链接**: https://arxiv.org/pdf/2603.23153v1
