## 基本信息

- **标题**: DVM: Real-Time Kernel Generation for Dynamic AI Models
- **作者**: Jingzhi Fang, Xiong Gao, Renwei Zhang, Zichun Ye, Lei Chen et al.
- **ArXiv ID**: 2603.24239v1
- **发布日期**: 2026-03-25
- **主分类**: cs.PL
- **分类**: cs.PL, cs.AI, cs.LG
- **摘要**: Dynamism is common in AI computation, e.g., the dynamic tensor shapes and the dynamic control flows in models. Due to the long compilation time, existing runtime compilation damages the model efficiency, while the offline compilers either suffer from the long compilation time and device memory footprint to cover all the possible execution instances of a dynamic model, or sacrifice optimization opportunities for usability. In this paper, we rethink the feasibility of runtime compilation for dynamic models and identify that the key for it to work is to speed up the compilation or hide the compilation overhead. To do this, we propose a real-time compiler, DVM. In DVM, we design a runtime operator compiler based on a bytecode virtual machine to perform effective and efficient compilation for each dynamic operator instance given its input. Specifically, instead of compiling programs into machine code, we encode the operator program into bytecode on the CPU and decode the bytecode into virtual instructions for direct execution on the NPU. Based on the runtime operator compiler, we further propose an operator fuser, which performs symbol-deduction-based fusion on static graphs and runtime fusion on dynamic graphs. Both pattern- and stacking-based fusion are supported to increase fusion opportunities. Evaluation on operators, subgraphs, and models shows that, compared with TorchInductor, PyTorch-eager and MindSpore-graph-O0, we are up to 11.77$\times$ better in terms of the operator/model efficiency and up to 5 orders of magnitude faster in terms of the maximum compilation time.
- **PDF 链接**: https://arxiv.org/pdf/2603.24239v1
