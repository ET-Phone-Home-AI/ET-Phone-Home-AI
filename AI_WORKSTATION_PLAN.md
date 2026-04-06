# AI Agent Training & Fine-Tuning Workstation Plan

**Lab Goal:** Build hardware infrastructure capable of training and fine-tuning AI agents
for specialized domains including RF design automation and clinical/patient-facing AI assistants.

---

## Use Cases & Compute Requirements

| Agent Type | Task | VRAM Need | Training Scale |
|---|---|---|---|
| RF Design Agent | Train on antenna, circuit, spectrum datasets; EM simulation data | 40–80 GB | Medium–Large |
| Dr. Assistant Agent | Fine-tune large LLMs (Llama, Mistral, MedPaLM-class); RAG pipeline | 80–160 GB | Large |
| Multi-agent orchestration | Run multiple specialized agents simultaneously | Scales with model count | Variable |
| Fine-tuning (LoRA/QLoRA) | Parameter-efficient fine-tuning on domain data | 24–80 GB | Medium |
| Full pre-training | From-scratch or continued pre-training on domain corpora | 160–640 GB+ | Very Large |

---

## Configuration A — Enterprise HPC Server (H100-Based)

**Best for:** Full pre-training, large-scale fine-tuning, running multiple large models in parallel,
production inference, multi-tenant research lab.

### GPU Platform

| Component | Spec | Notes |
|---|---|---|
| GPU | 8x NVIDIA H100 SXM5 80 GB | NVLink 4.0 + NVSwitch interconnect |
| GPU Memory | 640 GB HBM3 aggregate | Full all-to-all at 900 GB/s bisection |
| FP8 Tensor Core TFLOPS | ~3,958 TFLOPS (FP8) per GPU | Best for transformer training |
| NVLink bandwidth | 900 GB/s bidirectional | Critical for multi-GPU model parallelism |

> **Alternative:** If budget is a concern, 4x H100 PCIe 80 GB drops cost ~40% but loses NVLink —
> replace with PCIe 5.0 interconnect (still viable for pipeline parallelism).

### CPU Platform

| Component | Spec |
|---|---|
| CPU | 2x AMD EPYC Genoa 9654 (96 cores / 192 threads each — 192C / 384T total) |
| Socket | SP5 dual-socket |
| Base / Boost | 2.4 GHz / 3.7 GHz |
| L3 Cache | 384 MB total |
| PCIe Lanes | 192 lanes total (supports full GPU + NVMe bandwidth) |

> Intel Xeon Sapphire Rapids (Platinum 8490H) is a valid alternative — similar perf, better
> AVX-512 for certain signal-processing workloads (useful for RF data preprocessing).

### Memory

| Component | Spec |
|---|---|
| RAM | 2 TB DDR5-4800 ECC RDIMM (32x 64 GB) |
| Bandwidth | ~460 GB/s aggregate |
| Rationale | Large datasets stay in CPU RAM during GPU training; supports massive batch preprocessing |

### Storage

| Tier | Config | Use |
|---|---|---|
| NVMe Tier 1 (Hot) | 4x 7.68 TB Gen5 NVMe SSD in RAID 0 or striped | Training data, checkpoints, active jobs |
| NVMe Tier 2 (Warm) | 2x 15.36 TB Gen4 NVMe | Model weights, datasets, experiment logs |
| Network Storage | 100 TB+ NAS (ZFS, e.g., TrueNAS with 25 GbE) | Dataset archive, long-term storage |
| Backup | Tape or cloud cold storage | Checkpoint backups |

### Networking

| Component | Spec |
|---|---|
| InfiniBand | ConnectX-7 HDR 400 Gb/s (or NDR 800 Gb/s) | GPU-to-GPU over RDMA for distributed training |
| Ethernet | 2x 100 GbE (LACP bonded) | Management, data ingestion, NAS |

### Power & Cooling

| Item | Spec |
|---|---|
| TDP (GPUs alone) | 8 x 700 W = 5,600 W |
| Total system draw | ~10–12 kW under full load |
| Power delivery | 3-phase 208/240V, 60–80A circuit |
| Cooling | Direct liquid cooling (DLC) strongly recommended; minimum: high-CFM rack forced air |
| Rack | 42U+ server rack with PDU and UPS |

### Recommended System Options

1. **NVIDIA DGX H100** — Turnkey, fully validated, includes InfiniBand fabric, NVLink, NVIDIA AI software stack.
   Cost: ~$350,000–$450,000
2. **SuperMicro SYS-421GE-TNHR** — HGX H100 8-GPU, dual EPYC, custom-configurable.
   Cost: ~$250,000–$350,000 (configured)
3. **Dell PowerEdge XE9680** — Enterprise support, OEM pricing.
   Cost: ~$280,000–$400,000 (configured)

### Software Stack (H100)

```
OS:             Ubuntu 22.04 LTS (server) or Rocky Linux 9
Container:      Docker + NVIDIA Container Toolkit
Orchestration:  Kubernetes + KubeFlow (multi-tenant lab sharing)
Training:       PyTorch 2.x + FSDP / DeepSpeed ZeRO-3
Fine-tuning:    Hugging Face TRL, PEFT, Axolotl
Serving:        vLLM, TGI (Text Generation Inference)
Monitoring:     Prometheus + Grafana + DCGM Exporter
Experiment:     MLflow or Weights & Biases
```

---

## Configuration B — High-End Workstation (RTX-Based)

**Best for:** LoRA/QLoRA fine-tuning, rapid prototyping, inference, smaller-scale training,
cost-effective entry into multi-GPU AI development.

### GPU Platform

| Component | Spec | Notes |
|---|---|---|
| GPU | 4x NVIDIA RTX 5090 32 GB | Blackwell architecture (GB202), PCIe 5.0 x16 |
| GPU Memory | 128 GB GDDR7 aggregate | ~1.79 TB/s per card |
| FP8 Tensor TFLOPS | ~838 TFLOPS (FP8) per GPU | 3x RTX 4090 perf |
| NVLink | None (NVLink removed from consumer line) | Use PCIe P2P or pipeline parallelism |

> **Alternative:** 4x NVIDIA RTX PRO 6000 Blackwell (96 GB GDDR7 each = 384 GB total VRAM).
> This is the prosumer/workstation card from NVIDIA's Blackwell line — dramatically more VRAM,
> NVLink support, full ECC. Cost is significantly higher (~$8,000–10,000/card) but transforms
> what you can run without quantization. **Strongly recommended for Dr. Assistant use case.**

### CPU Platform

| Component | Spec |
|---|---|
| CPU | AMD Threadripper PRO 7995WX (96 cores / 192 threads) |
| Platform | WRX90 (sWRX9 socket) |
| PCIe Lanes | 128 lanes PCIe 5.0 — supports 4x GPU at full x16 + NVMe |
| TDP | 350 W |
| L3 Cache | 384 MB |

> Intel Xeon W9-3595X (60 cores, 112 PCIe 5.0 lanes) is a viable alternative with
> strong AVX-512 performance for RF signal processing pipelines.

### Memory

| Component | Spec |
|---|---|
| RAM | 512 GB DDR5-5600 ECC RDIMM (8x 64 GB) |
| Channels | 8-channel on WRX90 |
| Bandwidth | ~358 GB/s |

### Storage

| Tier | Config | Use |
|---|---|---|
| NVMe Tier 1 | 2x 4 TB Samsung 9100 Pro Gen5 NVMe | OS, training jobs, active checkpoints |
| NVMe Tier 2 | 2x 8 TB Gen4 NVMe | Datasets, model weights |
| External | 10 GbE NAS (TrueNAS Mini or Synology) | Archive |

### Power & Cooling

| Item | Spec |
|---|---|
| TDP (4x RTX 5090) | 4 x 575 W = 2,300 W |
| Total system draw | ~3,500–4,000 W under full load |
| PSU | Dual PSU configuration: 2x 2000W (e.g., Seasonic PRIME TX-2000) |
| Motherboard | ASUS Pro WS WRX90E-SAGE SE or SuperMicro M12SWA-TF |
| Cooling | 360mm AIO for CPU; GPU open-air or custom blower config for tight spacing |
| Case | Full-tower or open-air bench frame (Lian Li O11, Thermaltake Core W200) |

### Recommended Build Cost (RTX 5090 Config)

| Component | Approx. Cost |
|---|---|
| 4x RTX 5090 | $12,000–$14,000 |
| Threadripper PRO 7995WX | $5,500 |
| WRX90 Motherboard | $1,200–$1,800 |
| 512 GB DDR5 ECC | $2,000–$3,000 |
| NVMe Storage (12 TB total) | $800–$1,200 |
| Dual PSU + UPS | $800–$1,200 |
| Case + Cooling | $500–$1,000 |
| **Total (RTX 5090)** | **~$23,000–$28,000** |

### Recommended Build Cost (RTX PRO 6000 Blackwell Config)

| Component | Approx. Cost |
|---|---|
| 4x RTX PRO 6000 Blackwell (96 GB) | $32,000–$40,000 |
| Threadripper PRO 7995WX | $5,500 |
| WRX90 Motherboard | $1,800 |
| 512 GB DDR5 ECC | $2,500 |
| Storage + Power + Case | $2,500 |
| **Total (PRO 6000)** | **~$44,000–$52,000** |

### Software Stack (RTX)

```
OS:             Ubuntu 22.04 LTS Desktop or Pop!_OS 22.04
Container:      Docker + NVIDIA Container Toolkit
Training:       PyTorch 2.x + multi-GPU DataParallel / FSDP
Fine-tuning:    Axolotl, Unsloth (optimized for consumer GPUs), PEFT/LoRA
Serving:        Ollama (local inference), vLLM, LM Studio
Quantization:   bitsandbytes (4-bit/8-bit), GPTQ, GGUF/llama.cpp
Monitoring:     nvitop, nvidia-smi, Weights & Biases
```

---

## Agent-Specific Architecture Notes

### RF Design Agent

```
Training Data Sources:
  - IEEE antenna/RF paper datasets
  - Simulation output from ANSYS HFSS, CST Studio, or OpenEMS
  - S-parameter datasets, impedance matching tables
  - PCB layout + EM simulation pairs (input/output pairs for supervised learning)

Model Architecture:
  - Fine-tuned LLM backbone (Llama-3 70B or Mistral Large) with domain adapter
  - Physics-informed layers or tool-use (call EM simulators as tools)
  - RAG over RF design handbooks (Pozar, Balanis, etc.)

Training Strategy:
  - Instruction fine-tuning on RF Q&A pairs
  - Reinforcement Learning from Human Feedback (RLHF) with RF engineer feedback
  - Tool-use fine-tuning (agent calls simulation tools, evaluates results)
```

### Dr. Assistant Agent

```
Training Data Sources:
  - De-identified clinical conversation datasets (MIMIC-IV, MedDialog)
  - Medical knowledge bases (PubMed, UpToDate, clinical guidelines)
  - Structured EHR data (ICD codes, procedures, medications)

Model Architecture:
  - Fine-tuned medical LLM (Llama-3 70B, MedLLaMA, or BioMistral)
  - RAG pipeline over clinical knowledge base (Chroma or Weaviate vector DB)
  - Safety/refusal layer (critical for medical context)

Training Strategy:
  - Supervised fine-tuning (SFT) on medical dialogue
  - Constitutional AI or RLHF with physician feedback
  - Red-teaming and safety evaluation at every checkpoint

Compliance Considerations:
  - HIPAA: no patient PII in training data without proper de-identification
  - Model audit logging for all patient-facing inferences
  - Consider on-premise-only deployment (no cloud API calls with patient data)
```

---

## Comparison Summary

| Feature | Config A (H100) | Config B (RTX 5090) | Config B+ (PRO 6000) |
|---|---|---|---|
| Total VRAM | 640 GB HBM3 | 128 GB GDDR7 | 384 GB GDDR7 |
| GPU Interconnect | NVLink 900 GB/s | PCIe 5.0 only | PCIe 5.0 (+ NVLink on PRO) |
| Max model size (BF16) | ~320B params | ~60B params | ~190B params |
| Fine-tuning (LoRA 70B) | Yes, trivially | Yes (4-bit quant) | Yes (full precision) |
| Full pre-training | Yes | No | Limited |
| Est. Cost | $250k–$450k | $23k–$28k | $44k–$52k |
| Power (full load) | ~10–12 kW | ~3.5–4 kW | ~3.5–4 kW |
| Time to first fine-tune | Day 1 (or cloud) | Day 1 | Day 1 |
| Production serving | Yes (multi-model) | Limited | Yes (2–3 models) |

---

## Recommended Lab Strategy

### Phase 1 — Start with RTX Workstation (Config B or B+)
- Lower barrier to entry, faster procurement
- Prototype both RF and Dr. Assistant agents
- Validate datasets, training pipelines, evaluation frameworks
- **Recommended: RTX PRO 6000 Blackwell config** — the VRAM headroom is critical for
  running 70B models in BF16 without quantization degradation

### Phase 2 — Add H100 Server (Config A) for Scale
- Once agent architectures are validated, scale training
- Use H100 system for full fine-tuning runs and pre-training experiments
- Keep RTX workstation for rapid iteration, dev/test, and inference serving

### Phase 3 — Infrastructure
- Add InfiniBand fabric if adding a second H100 node
- NAS for shared dataset storage across both machines
- CI/CD pipeline for model training (GitHub Actions + self-hosted runner)
- Evaluation harness for each agent domain (RF benchmark suite, medical QA benchmarks)

---

## Quick Reference: Training Time Estimates

| Task | Config A (8x H100) | Config B+ (4x PRO 6000) |
|---|---|---|
| LoRA fine-tune Llama-3 8B (1M tokens) | ~5 min | ~25 min |
| LoRA fine-tune Llama-3 70B (1M tokens) | ~45 min | ~4 hrs |
| Full fine-tune Llama-3 8B (10B tokens) | ~8 hrs | ~4 days |
| Full fine-tune Llama-3 70B (10B tokens) | ~3 days | Not feasible |

---

*Last updated: April 2026*
*Branch: claude/ai-agent-workstation-setup-HGBTG*
