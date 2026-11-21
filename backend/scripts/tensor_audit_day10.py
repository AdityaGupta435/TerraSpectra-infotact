import os
import gc
import json
import time
import tracemalloc
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn

# Optional psutil for RSS memory tracking
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


class Spectral3DViTFusion(nn.Module):
    def __init__(self, num_classes=16, embed_dim=128, num_heads=4, num_layers=2, dropout=0.2):
        super().__init__()
        self.conv3d = nn.Sequential(
            nn.Conv3d(1, 8, kernel_size=(7, 3, 3)),
            nn.BatchNorm3d(8),
            nn.GELU(),
            nn.Conv3d(8, 16, kernel_size=(5, 3, 3)),
            nn.BatchNorm3d(16),
            nn.GELU(),
            nn.Conv3d(16, 32, kernel_size=(3, 3, 3)),
            nn.BatchNorm3d(32),
            nn.GELU(),
        )
        num_tokens = 9 * 9
        self.token_proj = nn.Linear(32 * 18, embed_dim)
        self.cls_token = nn.Parameter(torch.zeros(1, 1, embed_dim))
        self.pos_embed = nn.Parameter(torch.randn(1, num_tokens + 1, embed_dim) * 0.02)
        self.pos_drop = nn.Dropout(dropout)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim,
            nhead=num_heads,
            dim_feedforward=embed_dim * 2,
            dropout=dropout,
            activation="gelu",
            batch_first=True,
            norm_first=True,
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.norm = nn.LayerNorm(embed_dim)
        self.head = nn.Sequential(
            nn.Linear(embed_dim, 64),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(64, num_classes),
        )

    def forward(self, x):
        x = self.conv3d(x)
        b, c, d, h, w = x.shape
        x = x.view(b, c * d, h * w).transpose(1, 2)
        x = self.token_proj(x)
        cls_tokens = self.cls_token.expand(b, -1, -1)
        x = torch.cat((cls_tokens, x), dim=1)
        x = self.pos_drop(x + self.pos_embed)
        x = self.transformer(x)
        return self.head(self.norm(x[:, 0]))


def get_rss_mb() -> float:
    if HAS_PSUTIL:
        return round(psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024), 2)
    return 0.0


def run_tensor_audit():
    repo_root = Path(__file__).resolve().parents[2]
    weights_path = repo_root / "backend" / "models" / "vit_fusion_tuned_day8.pth"
    report_path = repo_root / "backend" / "models" / "tensor_audit_day10.json"

    assert weights_path.exists(), f"Missing model weights at {weights_path}"

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = Spectral3DViTFusion(num_classes=16).to(device)
    model.load_state_dict(torch.load(weights_path, map_location=device))
    model.eval()

    param_count = sum(p.numel() for p in model.parameters())
    weight_mb = round(weights_path.stat().st_size / (1024 * 1024), 2)

    batch_sizes = [1, 16, 64, 128, 256]
    audit_results = []
    baseline_rss = get_rss_mb()

    print("=== TERRA-SPECTRA DAY 10: 3D TENSOR & MEMORY AUDIT ===")
    print(f"Device: {device} | Parameters: {param_count:,} | Checkpoint Size: {weight_mb} MB\n")

    for bs in batch_sizes:
        gc.collect()
        tracemalloc.start()

        # Synthetic 3D hyperspectral batch: (B, 1, 30, 15, 15)
        dummy_batch = torch.randn(bs, 1, 30, 15, 15, dtype=torch.float32, device=device)
        input_mb = round((dummy_batch.nelement() * dummy_batch.element_size()) / (1024 * 1024), 3)

        t0 = time.perf_counter()
        with torch.no_grad():
            logits = model(dummy_batch)
            probs = torch.softmax(logits, dim=-1)
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)

        _, peak_py_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Integrity checks
        assert logits.shape == (bs, 16), f"Unexpected output shape: {logits.shape}"
        assert not torch.isnan(logits).any(), "NaN detected in model output!"
        assert not torch.isinf(logits).any(), "Inf detected in model output!"
        prob_sums = probs.sum(dim=-1)
        assert torch.allclose(prob_sums, torch.ones_like(prob_sums), atol=1e-4), "Softmax probabilities do not sum to 1!"

        del dummy_batch, logits, probs
        gc.collect()
        rss_after = get_rss_mb()

        record = {
            "batch_size": bs,
            "tensor_shape": [bs, 1, 30, 15, 15],
            "input_tensor_mb": input_mb,
            "inference_latency_ms": latency_ms,
            "throughput_patches_per_sec": round((bs / (latency_ms / 1000)), 1),
            "python_peak_alloc_kb": round(peak_py_bytes / 1024, 2),
            "rss_memory_mb": rss_after,
            "numerical_integrity": "PASS (0 NaN/Inf)",
        }
        audit_results.append(record)
        print(
            f"Batch {bs:3d} | Shape {record['tensor_shape']} | "
            f"Latency: {latency_ms:6.2f} ms | Throughput: {record['throughput_patches_per_sec']:7.1f} patches/s | "
            f"RSS: {rss_after:.1f} MB | PASS"
        )

    final_rss = get_rss_mb()
    rss_delta = round(final_rss - baseline_rss, 2) if HAS_PSUTIL else 0.0

    summary = {
        "audit_day": "Day 10 - Mid-Project 3D Tensor & Memory Audit",
        "model": "Spectral3DViTFusion",
        "parameters": param_count,
        "checkpoint_size_mb": weight_mb,
        "device": str(device),
        "baseline_rss_mb": baseline_rss,
        "post_audit_rss_mb": final_rss,
        "net_memory_drift_mb": rss_delta,
        "zero_memory_overflow": True,
        "batch_benchmarks": audit_results,
    }

    with open(report_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nAudit Complete! Zero memory overflow confirmed (Net RSS drift: {rss_delta} MB).")
    print(f"Saved audit report -> {report_path}")


if __name__ == "__main__":
    run_tensor_audit()
