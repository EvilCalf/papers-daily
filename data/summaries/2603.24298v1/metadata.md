## 基本信息

- **标题**: SpinGQE: A Generative Quantum Eigensolver for Spin Hamiltonians
- **作者**: Alexander Holden, Moinul Hossain Rahat, Nii Osae Osae Dade
- **ArXiv ID**: 2603.24298v1
- **发布日期**: 2026-03-25
- **主分类**: quant-ph
- **分类**: quant-ph, cs.CL
- **摘要**: The ground state search problem is central to quantum computing, with applications spanning quantum chemistry, condensed matter physics, and optimization. The Variational Quantum Eigensolver (VQE) has shown promise for small systems but faces significant limitations. These include barren plateaus, restricted ansatz expressivity, and reliance on domain-specific structure. We present SpinGQE, an extension of the Generative Quantum Eigensolver (GQE) framework to spin Hamiltonians. Our approach reframes circuit design as a generative modeling task. We employ a transformer-based decoder to learn distributions over quantum circuits that produce low-energy states. Training is guided by a weighted mean-squared error loss between model logits and circuit energies evaluated at each gate subsequence. We validate our method on the four-qubit Heisenberg model, demonstrating successfulconvergencetonear-groundstates. Throughsystematichyperparameterexploration, we identify optimal configurations: smaller model architectures (12 layers, 8 attention heads), longer sequence lengths (12 gates), and carefully chosen operator pools yield the most reliable convergence. Our results show that generative approaches can effectively navigate complex energy landscapes without relying on problem-specific symmetries or structure. This provides a scalable alternative to traditional variational methods for general quantum systems. An open-source implementation is available at https://github.com/Mindbeam-AI/SpinGQE.
- **PDF 链接**: https://arxiv.org/pdf/2603.24298v1
