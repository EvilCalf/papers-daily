## 基本信息

- **标题**: Closing the Confidence-Faithfulness Gap in Large Language Models
- **作者**: Miranda Muqing Miao, Lyle Ungar
- **ArXiv ID**: 2603.25052v1
- **发布日期**: 2026-03-26
- **主分类**: cs.CL
- **分类**: cs.CL, cs.AI
- **摘要**: Large language models (LLMs) tend to verbalize confidence scores that are largely detached from their actual accuracy, yet the geometric relationship governing this behavior remain poorly understood. In this work, we present a mechanistic interpretability analysis of verbalized confidence, using linear probes and contrastive activation addition (CAA) steering to show that calibration and verbalized confidence signals are encoded linearly but are orthogonal to one another -- a finding consistent across three open-weight models and four datasets. Interestingly, when models are prompted to simultaneously reason through a problem and verbalize a confidence score, the reasoning process disrupts the verbalized confidence direction, exacerbating miscalibration. We term this the "Reasoning Contamination Effect." Leveraging this insight, we introduce a two-stage adaptive steering pipeline that reads the model's internal accuracy estimate and steers verbalized output to match it, substantially improving calibration alignment across all evaluated models.
- **PDF 链接**: https://arxiv.org/pdf/2603.25052v1
