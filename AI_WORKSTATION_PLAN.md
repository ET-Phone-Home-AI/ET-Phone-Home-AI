# AI Agent Training & Fine-Tuning Workstation Plan

**Lab Goal:** Build desktop workstation infrastructure capable of training and fine-tuning large
AI agents for specialized domains — RF design automation and clinical/patient-facing AI assistants.

---

## Use Cases & Compute Requirements

| Agent Type | Task | VRAM Need | Training Scale |
|---|---|---|---|
| RF Design Agent | Train on antenna, circuit, spectrum datasets; EM simulation data | 40–80 GB | Medium–Large |
| Dr. Assistant Agent | Fine-tune large LLMs (Llama, Mistral, MedPaLM-class); RAG pipeline | 80–160 GB | Large |
| Multi-agent orchestration | Run multiple specialized agents simultaneously | Scales with model count | Variable |
| Fine-tuning (LoRA/QLoRA) | Parameter-efficient fine-tuning on domain data | 24–80 GB | Medium |
| Full fine-tune (ZeRO-3) | Full parameter training on domain corpora | 400–768 GB | Very Large |

---

## How Large a Model Can 8x RTX PRO 6000 Blackwell Handle?

**Total VRAM: 8 × 96 GB = 768 GB GDDR7**

| Task | Max Model Size | Notes |
|---|---|---|
| **Inference (BF16)** | ~350–380B params | Llama 3.1 405B fits in FP8 (405 GB) |
| **Inference (4-bit quantized)** | 1,500B+ | Beyond any public model today |
| **LoRA fine-tune (BF16 frozen base)** | ~350B | Base model frozen, only adapter gradients |
| **LoRA fine-tune (FP8 base)** | ~700B | FP8 base + BF16 adapters |
| **QLoRA (4-bit base + adapters)** | 700B+ | Maximum reach, minimal quality loss |
| **Full fine-tune (ZeRO-3 sharded)** | ~70B comfortably / ~120B aggressive | All params + optimizer states sharded across 8 GPUs |

**Practical answer for your agents:**
- RF Design Agent (70B fine-tune): **Full BF16 fine-tuning with room to spare**
- Dr. Assistant (70B–405B): **Full fine-tune at 70B; LoRA/QLoRA at 405B** — both fully viable
- Running multiple agents simultaneously: load 2–3 x 70B models in BF16 at once (~420–630 GB)

---

## Configuration A — Enterprise HPC Server (H100-Based)

**Best for:** Full pre-training, very large-scale training runs, multi-tenant research lab,
maximum throughput regardless of cost.

### GPU & CPU Platform

| Component | Spec | Notes |
|---|---|---|
| GPU | 8x NVIDIA H100 SXM5 80 GB | NVLink 4.0 + NVSwitch all-to-all |
| GPU Memory | 640 GB HBM3 | 900 GB/s bisection bandwidth |
| CPU | 2x AMD EPYC 9654 (96C each, 192C total) | Dual SP5, 192 PCIe 5.0 lanes |
| RAM | 2 TB DDR5-4800 ECC RDIMM | 32x 64 GB |
| Networking | ConnectX-7 HDR InfiniBand 400 Gb/s | GPU-to-GPU RDMA |
| Power | ~10–12 kW full load | 3-phase 208V, 60–80A circuit required |
| Form Factor | Rack-mounted server | Not desktop compatible |

### Turnkey System Options

| System | Notes | Est. Cost |
|---|---|---|
| **NVIDIA DGX H100** | Fully validated, includes SW stack | $350k–$450k |
| **SuperMicro SYS-421GE-TNHR** | HGX H100, configurable | $250k–$350k |
| **Dell PowerEdge XE9680** | Enterprise support, OEM pricing | $280k–$400k |

### Software Stack

```
OS:             Ubuntu 22.04 LTS / Rocky Linux 9
Container:      Docker + NVIDIA Container Toolkit
Training:       PyTorch 2.x + DeepSpeed ZeRO-3 / FSDP
Fine-tuning:    Hugging Face TRL, PEFT, Axolotl
Serving:        vLLM, TGI
Orchestration:  Kubernetes + KubeFlow
Monitoring:     Prometheus + Grafana + DCGM Exporter
```

---

## Configuration B — 8x RTX PRO 6000 Blackwell Desktop Tower ← RECOMMENDED

**Best for:** Large-scale fine-tuning up to 405B, running multiple 70B agents simultaneously,
Windows desktop experience, sits in your lab like a workstation PC. ~1/4 the cost of H100.

### Form Factor

This is a **tower workstation** — not a rack server. It sits on the floor next to your desk
exactly like a large desktop PC tower. It runs Windows 11 natively and uses standard peripherals
(monitor, keyboard, mouse). The ASUS ESC8000A-E11 is the target chassis.

```
┌─────────────────────────────┐
│   ASUS ESC8000A-E11 Tower   │  ← Looks like a large desktop PC tower
│   ~435mm W × 700mm H        │    Sits on your lab floor
│   × 900mm D                 │    Plugs into standard outlets (2x 20A circuits)
│                             │    Runs Windows 11 Pro for Workstations
│   [Power]  [USB]  [Display] │    Full monitor/keyboard/mouse support
└─────────────────────────────┘
```

### Complete Parts List

#### GPUs

| Item | Spec | Qty | Unit Cost | Total |
|---|---|---|---|---|
| NVIDIA RTX PRO 6000 Blackwell | 96 GB GDDR7, 300W TDP, PCIe 5.0 x16 | 8 | ~$8,000–$10,000 | **$64,000–$80,000** |
| NVLink 4.0 Bridge (2-slot) | Pairs GPUs 0-1, 2-3, 4-5, 6-7 | 4 | ~$100–$200 | ~$600 |

> **NVLink topology:** Cards are bridged in pairs. Within each pair: 900 GB/s bidirectional.
> Cross-pair communication uses PCIe 5.0 — fully handled by DeepSpeed/FSDP automatically.

#### Chassis & Motherboard

| Item | Spec | Cost |
|---|---|---|
| **ASUS ESC8000A-E11** | Tower/pedestal, dual EPYC SP5, 8x PCIe 5.0 x16 GPU slots, redundant 3000W PSU | ~$8,000–$12,000 |

> Includes: 24 DDR5 DIMM slots, 2x M.2 NVMe, 8x hot-swap drive bays, dual 10 GbE onboard,
> redundant 80+ Platinum PSUs, tool-less GPU installation, Windows driver support.

#### CPU

| Item | Spec | Qty | Unit Cost | Total |
|---|---|---|---|---|
| AMD EPYC 9454 | 48 cores / 96 threads, 2.75/3.8 GHz, 290W TDP, 256 MB L3, 128 PCIe 5.0 lanes | 2 | ~$2,000–$2,500 | **$4,000–$5,000** |

> Two EPYC CPUs = 256 total PCIe 5.0 lanes — supports all 8 GPUs at full x16 simultaneously
> with lanes left over for NVMe and NICs. 96 cores total handles data preprocessing in parallel
> with GPU training without any bottleneck.
>
> **Optional upgrade:** 2x EPYC 9654 (96C each = 192C total) for ~$12,000 — only needed if
> you plan heavy CPU-side simulation workloads alongside GPU training.

#### Memory

| Item | Spec | Qty | Unit Cost | Total |
|---|---|---|---|---|
| Micron / Samsung DDR5-4800 ECC RDIMM | 64 GB per stick | 12 | ~$300–$450 | **$3,600–$5,400** |
| **Total RAM** | **768 GB DDR5 ECC** | — | — | — |

> 768 GB RAM matches 768 GB GPU VRAM — ensures your CPU-side data pipeline never bottlenecks
> GPU feeding. For massive datasets (405B model + full training batch), scale to 1.5 TB (24 sticks).

#### Storage

| Tier | Item | Spec | Qty | Total |
|---|---|---|---|---|
| **Hot (Active Training)** | Samsung 9100 Pro or Micron 4600 | 4 TB Gen5 NVMe (~14 GB/s read) | 2 | ~$600–$900 |
| **Warm (Datasets/Weights)** | WD Black SN850X or Samsung 990 Pro | 8 TB Gen4 NVMe | 2 | ~$800–$1,200 |
| **Cold Archive** | Seagate Exos / WD Gold | 20 TB SATA HDD | 2 | ~$500–$700 |
| **Total** | | **~44 TB mixed** | | **~$1,900–$2,800** |

> Hot tier: OS, active training jobs, checkpoints (fast R/W critical during training)
> Warm tier: Model weight library, training datasets ready to load
> Cold tier: Dataset archive, completed model snapshots

#### Networking

| Item | Spec | Cost |
|---|---|---|
| Onboard dual 10 GbE | Included in ESC8000A-E11 | $0 |
| ASUS XG-C100C or Mellanox ConnectX-6 | 25 GbE PCIe NIC for NAS connection | ~$200–$400 |

#### Power & UPS

| Item | Spec | Cost |
|---|---|---|
| Chassis PSU (included) | 2x 1600W redundant (3000W total output), 80+ Platinum | Included |
| APC Smart-UPS SRT 3000VA | 3000VA / 2700W, 208/240V, runtime buffer | ~$2,000–$2,500 |

> **Power draw calculation:**
> - 8x RTX PRO 6000 @ 300W = 2,400W
> - 2x EPYC 9454 @ 290W = 580W
> - Motherboard + RAM + storage = ~200W
> - **Total full load: ~3,200W**
> - Requires 2x dedicated 20A 120V circuits OR 1x 20A 240V circuit
> - The UPS protects against power loss mid-training-run (checkpoints every 15 min recommended)

#### Operating System & Software Licenses

| Item | Cost |
|---|---|
| Windows 11 Pro for Workstations | ~$200–$310 |
| NVIDIA AI Enterprise (optional, includes optimized containers) | ~$4,500/yr or use open-source stack |

---

### Full Build Cost Summary

| Component | Est. Cost |
|---|---|
| 8x RTX PRO 6000 Blackwell 96 GB | $64,000–$80,000 |
| 4x NVLink 4.0 bridges | $600 |
| ASUS ESC8000A-E11 chassis + board | $8,000–$12,000 |
| 2x AMD EPYC 9454 (96 cores total) | $4,000–$5,000 |
| 768 GB DDR5-4800 ECC (12x 64 GB) | $3,600–$5,400 |
| NVMe + HDD storage (~44 TB) | $1,900–$2,800 |
| 25 GbE NIC | $300–$400 |
| APC UPS 3000VA | $2,000–$2,500 |
| Windows 11 Pro for Workstations | $300 |
| **TOTAL** | **$84,700–$109,000** |

---

### Software Stack (Windows + Linux dual-boot option)

```
Primary OS:       Windows 11 Pro for Workstations
                  (full GPU driver support, WSL2 for Linux tools)

Optional dual:    Ubuntu 22.04 LTS on separate NVMe (swap at boot)
                  Recommended for production training runs

GPU Drivers:      NVIDIA Studio Driver or Data Center Driver (Windows)
CUDA:             CUDA 12.x + cuDNN 9.x

Training stack:
  PyTorch 2.x        — core framework
  DeepSpeed ZeRO-3   — shards model across all 8 GPUs
  FSDP               — PyTorch native alternative to DeepSpeed
  Hugging Face TRL   — RLHF, SFT, reward model training
  PEFT / Axolotl     — LoRA, QLoRA, adapter training
  Unsloth            — 2x faster LoRA on RTX hardware

Inference / Serving:
  vLLM               — fast multi-GPU inference server
  Ollama             — easy local model running (Windows native)
  LM Studio          — GUI for running/testing models on Windows

Vector DB (for RAG):
  Chroma             — lightweight, runs locally
  Weaviate           — production-grade, Docker-based

Quantization:
  bitsandbytes       — 4-bit / 8-bit on NVIDIA GPUs
  GPTQ / AWQ         — post-training quantization
  llama.cpp (GGUF)   — CPU fallback / edge deployment

Experiment tracking:
  Weights & Biases   — training curves, checkpoints, comparisons
  MLflow             — open-source alternative

Monitoring:
  nvitop             — real-time GPU dashboard (Windows + Linux)
  NVIDIA DCGM        — GPU health, power, thermal telemetry
```

---

## Agent-Specific Architecture

### RF Design Agent

```
Training Data Sources:
  - IEEE antenna/RF paper datasets
  - Simulation output from ANSYS HFSS, CST Studio, or OpenEMS
  - S-parameter (Touchstone .s2p) datasets, impedance matching tables
  - PCB layout + EM simulation pairs (supervised input/output)
  - Datasheet corpus (component specs, application notes)

Model Architecture:
  - Fine-tuned LLM backbone (Llama-3 70B) with RF domain adapter
  - Tool-use fine-tuning: agent calls HFSS/OpenEMS as tools, evaluates output
  - RAG over RF handbooks (Pozar, Balanis, Collin) + datasheets

Training Strategy:
  - Phase 1: Instruction fine-tune on RF Q&A pairs (SFT)
  - Phase 2: Tool-use fine-tuning (function calling to simulators)
  - Phase 3: RLHF with RF engineer feedback on design quality
  - Hardware needed: 2–3 GPUs for training, rest for parallel inference
```

### Dr. Assistant Agent

```
Training Data Sources:
  - De-identified clinical conversations (MIMIC-IV, MedDialog)
  - Medical knowledge bases (PubMed abstracts, clinical guidelines)
  - Medical Q&A datasets (MedQA, PubMedQA, BioASQ)
  - Structured clinical data (ICD-10, SNOMED, RxNorm)

Model Architecture:
  - Fine-tuned medical LLM (Llama-3 70B, BioMistral, or MedLLaMA)
  - RAG pipeline: Weaviate vector DB over clinical knowledge base
  - Safety/refusal layer — evaluated by licensed physicians before deploy
  - Conversation memory: patient context across session turns

Training Strategy:
  - Phase 1: SFT on medical dialogue
  - Phase 2: Constitutional AI (rule-based safety constraints)
  - Phase 3: RLHF with physician reviewer feedback
  - Red-team at every major checkpoint before any patient-facing use

Compliance (Non-Negotiable):
  - HIPAA: all training data de-identified per Safe Harbor or Expert standard
  - All inference stays on-premise — zero patient data to cloud APIs
  - Full audit log of every model inference (who, when, what)
  - Model versioning: never overwrite a deployed model without backup
```

---

## Comparison: Config A (H100) vs Config B (8x PRO 6000 Tower)

| Feature | Config A — H100 Server | Config B — 8x PRO 6000 Tower |
|---|---|---|
| Total VRAM | 640 GB HBM3 | 768 GB GDDR7 |
| GPU Interconnect | NVLink NVSwitch 900 GB/s all-to-all | NVLink pairs + PCIe 5.0 cross-pair |
| Max model (BF16 inference) | ~320B | ~350–380B |
| Max model (LoRA fine-tune) | ~300B | ~350B |
| Full fine-tune capacity | Up to ~300B | Up to ~70–120B |
| Form factor | Rack server (server room) | **Desktop tower (lab floor)** |
| Windows compatible | Limited | **Yes, natively** |
| Looks like a desktop PC | No | **Yes** |
| Total cost | $250k–$450k | **$85k–$110k** |
| Power (full load) | ~10–12 kW (3-phase required) | ~3.2 kW (standard outlet) |
| Time to first fine-tune | Day 1 | Day 1 |
| RF Agent (70B fine-tune) | Yes | **Yes** |
| Dr. Assistant (70B fine-tune) | Yes | **Yes** |
| Run both agents simultaneously | Yes | **Yes (256 GB each with room left)** |

---

## Training Time Estimates (8x RTX PRO 6000 Blackwell)

| Task | 4x PRO 6000 | **8x PRO 6000** | 8x H100 |
|---|---|---|---|
| LoRA fine-tune 8B (1M tokens) | ~10 min | **~5 min** | ~2 min |
| LoRA fine-tune 70B (1M tokens) | ~4 hrs | **~2 hrs** | ~45 min |
| LoRA fine-tune 405B (1M tokens) | ~22 hrs | **~11 hrs** | ~3 hrs |
| Full fine-tune 8B (10B tokens) | ~4 days | **~2 days** | ~8 hrs |
| Full fine-tune 70B (10B tokens) | Not feasible | **~8 days** | ~3 days |
| Inference: 70B model, 100 req/s | Possible | **Comfortable** | Yes |
| Inference: 405B model, 100 req/s | Slow | **Viable** | Yes |

---

## Recommended Lab Strategy

### Phase 1 — Build Config B (8x RTX PRO 6000 Desktop Tower)
- Order ASUS ESC8000A-E11 + 8x RTX PRO 6000 Blackwell
- Install Windows 11 Pro for Workstations
- Set up CUDA, PyTorch, DeepSpeed, vLLM
- Start fine-tuning RF Agent and Dr. Assistant on 70B models
- **This machine handles everything you need for both agents**

### Phase 2 — Add NAS for Dataset Storage
- Synology RS2423+ or TrueNAS Mini X+ with 100+ TB capacity
- Connect via 25 GbE to the workstation
- Store all training datasets, model checkpoints, experiment history here
- Keeps the workstation NVMe free for active training jobs

### Phase 3 — Add H100 Server (Only If Needed)
- Only add if you need to: pre-train from scratch, train models > 120B from full weights,
  or run 10+ simultaneous agent instances at production scale
- The Config B tower will handle everything at research/prototype/lab scale
- Estimated trigger: when a single training run takes > 2 weeks consistently

---

## Quick Reference: What This Machine Can Do Right Now

```
✓  Fine-tune Llama 3.1 70B  — full BF16, no quantization, ~2 hrs per 1M tokens
✓  Fine-tune Llama 3.1 405B — via LoRA (FP8 base), ~11 hrs per 1M tokens
✓  Run RF Agent + Dr. Assistant simultaneously (both 70B, ~140 GB VRAM used)
✓  Vector database + RAG pipeline running on-premise
✓  HIPAA-compliant: zero cloud, all inference local
✓  Windows 11 desktop — use like a regular workstation
✓  Upgrade path: add second tower, link via 25 GbE for double capacity
```

---

*Last updated: April 2026*
*Branch: claude/ai-agent-workstation-setup-HGBTG*
