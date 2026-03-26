## 基本信息

- **标题**: Mind the Hitch: Dynamic Calibration and Articulated Perception for Autonomous Trucks
- **作者**: Morui Zhu, Yongqi Zhu, Song Fu, Qing Yang
- **ArXiv ID**: 2603.23711v1
- **发布日期**: 2026-03-24
- **主分类**: cs.CV
- **分类**: cs.CV
- **摘要**: Autonomous trucking poses unique challenges due to articulated tractor-trailer geometry, and time-varying sensor poses caused by the fifth-wheel joint and trailer flex. Existing perception and calibration methods assume static baselines or rely on high-parallax and texture-rich scenes, limiting their reliability under real-world settings. We propose dCAP (dynamic Calibration and Articulated Perception), a vision-based framework that continuously estimates the 6-DoF (degree of freedom) relative pose between tractor and trailer cameras. dCAP employs a transformer with cross-view and temporal attention to robustly aggregate spatial cues while maintaining temporal consistency, enabling accurate perception under rapid articulation and occlusion. Integrated with BEVFormer, dCAP improves 3D object detection by replacing static calibration with dynamically predicted extrinsics. To facilitate evaluation, we introduce STT4AT, a CARLA-based benchmark simulating semi-trailer trucks with synchronized multi-sensor suites and time-varying inter-rig geometry across diverse environments. Experiments demonstrate that dCAP achieves stable, accurate perception while addressing the limitations of static calibration in autonomous trucking. The dataset, development kit, and source code will be publicly released.
- **PDF 链接**: https://arxiv.org/pdf/2603.23711v1
