"""Thin LIVE service used only after explicit preflight authorization."""
from __future__ import annotations
from pathlib import Path
from .evidence import write_json
from .events import Event, EventLog
from .genblaze_adapter import (
    run_live_google_image,
    run_live_nvidia_image,
    run_live_openai_image,
    run_live_pollinations_image,
)
from .ledger import Ledger
from .models import Attempt, Opportunity, RunRecord
from .orchestrator import preflight
from .provenance import summarize_genblaze_result
from .source_audit import write_source_snapshot
from .audit_receipt import write_receipt
from .decision_certificate import build_certificate, write_certificate
from .submission import build_submission_package


def _write_live_evidence(
    *,
    root: Path,
    op: Opportunity,
    rights,
    economics,
    ledger: Ledger,
    result,
    proof: dict,
    provider: str,
    model: str,
) -> RunRecord:
    manifest = getattr(result, "manifest", None)
    if manifest is not None and hasattr(manifest, "model_dump_json"):
        (root / "generations" / "live-001").mkdir(parents=True, exist_ok=True)
        (root / "generations" / "live-001" / "genblaze-manifest.json").write_text(
            manifest.model_dump_json(indent=2) + "\n",
            encoding="utf-8",
        )
    attempt = Attempt(
        attempt=1,
        provider=provider,
        model=model,
        score=100.0 if proof.get("manifest_verified") is True else 0.0,
        passed=proof.get("manifest_verified") is True,
        cost=0.0,
        asset_path=str(proof.get("provider_url") or proof.get("durable_url") or ""),
        sha256=str(proof.get("asset_sha256") or ""),
        feedback=None if proof.get("manifest_verified") is True else "Native Genblaze manifest did not verify.",
    )
    record = RunRecord(
        opportunity_id=op.id,
        rights=rights,
        economics=economics,
        attempts=[attempt],
        accepted_attempt=1 if attempt.passed else None,
        evidence_dir=str(root),
        mode="LIVE",
    )
    write_certificate(
        root / "decision-certificate.json",
        build_certificate(
            op,
            rights,
            economics,
            budget_available=ledger.totals(op.currency)["available_paid_generation_budget"],
            mode="LIVE",
        ),
    )
    write_json(root / "run.json", record)
    build_submission_package(op, record, root)
    return record


def run_approved_openai_image(
    op: Opportunity,
    *,
    ledger: Ledger,
    evidence_root: str | Path,
    estimated_unit_cost: float,
    model: str = "dall-e-3",
    fallback_models: list[str] | None = None,
    timeout_seconds: int = 300,
    retry_mode: str = "conservative",
):
    """Run a real provider only after rights, economics and budget gates pass.

    `estimated_unit_cost` is an authorization ceiling input, not claimed actual spend.
    Actual provider charges must be reconciled separately into the ledger.
    """
    root = Path(evidence_root) / op.id
    events = EventLog(root / "events.jsonl")
    rights, economics, plan = preflight(
        op, ledger, root / "events.jsonl", estimated_unit_cost=estimated_unit_cost
    )
    write_json(root / "source" / "opportunity.json", op)
    write_source_snapshot(op, root / "source")
    write_json(root / "eligibility.json", rights)
    write_json(root / "economics.json", economics)
    write_json(root / "production-plan.json", plan)
    events.emit(Event(
        opportunity_id=op.id,
        kind="GENBLAZE_START",
        message="Real Genblaze execution authorized after all gates passed.",
        data={"model": model, "fallback_models": fallback_models or [], "timeout_seconds": timeout_seconds, "retry_mode": retry_mode},
    ))
    result = run_live_openai_image(
        pipeline_name=f"creative-bounty-{op.id}",
        prompt=plan.prompt,
        model=model,
        fallback_models=fallback_models,
        use_cache=True,
        timeout_seconds=timeout_seconds,
        retry_mode=retry_mode,
        structured_logging=True,
    )
    proof = summarize_genblaze_result(result)
    write_json(root / "generations" / "live-001" / "genblaze-proof.json", proof)
    _write_live_evidence(
        root=root,
        op=op,
        rights=rights,
        economics=economics,
        ledger=ledger,
        result=result,
        proof=proof,
        provider="openai-image",
        model=model,
    )
    events.emit(Event(
        opportunity_id=op.id,
        kind="B2_PROVENANCE",
        status="VERIFIED" if proof.get("manifest_verified") else "RECORDED",
        message="Durable B2 asset and native Genblaze provenance recorded.",
        data=proof,
    ))
    write_receipt(root, opportunity_id=op.id, mode="LIVE")
    return result, proof


def run_approved_google_image(
    op: Opportunity,
    *,
    ledger: Ledger,
    evidence_root: str | Path,
    estimated_unit_cost: float,
    model: str = "gemini-3.1-flash-lite-image",
    fallback_models: list[str] | None = None,
    timeout_seconds: int = 300,
    retry_mode: str = "disabled",
):
    """Run one real Google Imagen provider call after the existing gates pass."""
    root = Path(evidence_root) / op.id
    events = EventLog(root / "events.jsonl")
    rights, economics, plan = preflight(
        op, ledger, root / "events.jsonl", estimated_unit_cost=estimated_unit_cost
    )
    write_json(root / "source" / "opportunity.json", op)
    write_source_snapshot(op, root / "source")
    write_json(root / "eligibility.json", rights)
    write_json(root / "economics.json", economics)
    write_json(root / "production-plan.json", plan)
    events.emit(Event(
        opportunity_id=op.id,
        kind="GENBLAZE_START",
        message="Real Genblaze Google Imagen execution authorized after all gates passed.",
        data={
            "provider": "google-imagen",
            "model": model,
            "fallback_models": fallback_models or [],
            "timeout_seconds": timeout_seconds,
            "retry_mode": retry_mode,
        },
    ))
    result = run_live_google_image(
        pipeline_name=f"creative-bounty-{op.id}",
        prompt=plan.prompt,
        model=model,
        fallback_models=fallback_models,
        use_cache=True,
        timeout_seconds=timeout_seconds,
        retry_mode=retry_mode,
        structured_logging=True,
    )
    proof = summarize_genblaze_result(result)
    proof.update({
        "provider": "google-imagen",
        "model": model,
        "actual_provider_cost": "UNKNOWN",
        "credit_type": "Gemini API free tier; no billing enabled",
    })
    write_json(root / "generations" / "live-001" / "genblaze-proof.json", proof)
    _write_live_evidence(
        root=root,
        op=op,
        rights=rights,
        economics=economics,
        ledger=ledger,
        result=result,
        proof=proof,
        provider="google-imagen",
        model=model,
    )
    events.emit(Event(
        opportunity_id=op.id,
        kind="B2_PROVENANCE",
        status="VERIFIED" if proof.get("manifest_verified") else "RECORDED",
        message="Durable B2 asset and native Genblaze provenance recorded.",
        data=proof,
    ))
    write_receipt(root, opportunity_id=op.id, mode="LIVE")
    return result, proof


def run_approved_nvidia_image(
    op: Opportunity,
    *,
    ledger: Ledger,
    evidence_root: str | Path,
    estimated_unit_cost: float,
    model: str = "black-forest-labs/flux.1-schnell",
    fallback_models: list[str] | None = None,
    timeout_seconds: int = 300,
    retry_mode: str = "disabled",
):
    """Run one real NVIDIA NIM provider call after the existing gates pass."""
    root = Path(evidence_root) / op.id
    events = EventLog(root / "events.jsonl")
    rights, economics, plan = preflight(
        op, ledger, root / "events.jsonl", estimated_unit_cost=estimated_unit_cost
    )
    write_json(root / "source" / "opportunity.json", op)
    write_source_snapshot(op, root / "source")
    write_json(root / "eligibility.json", rights)
    write_json(root / "economics.json", economics)
    write_json(root / "production-plan.json", plan)
    events.emit(Event(
        opportunity_id=op.id,
        kind="GENBLAZE_START",
        message="Real Genblaze NVIDIA NIM execution authorized after all gates passed.",
        data={
            "provider": "nvidia-image",
            "model": model,
            "fallback_models": fallback_models or [],
            "timeout_seconds": timeout_seconds,
            "retry_mode": retry_mode,
        },
    ))
    result = run_live_nvidia_image(
        pipeline_name=f"creative-bounty-{op.id}",
        prompt=plan.prompt,
        model=model,
        fallback_models=fallback_models,
        use_cache=True,
        timeout_seconds=timeout_seconds,
        retry_mode=retry_mode,
        structured_logging=True,
    )
    proof = summarize_genblaze_result(result)
    proof.update({
        "provider": "nvidia-image",
        "model": model,
        "actual_provider_cost": "UNKNOWN",
        "credit_type": "NVIDIA-hosted NIM free development endpoint",
    })
    write_json(root / "generations" / "live-001" / "genblaze-proof.json", proof)
    _write_live_evidence(
        root=root,
        op=op,
        rights=rights,
        economics=economics,
        ledger=ledger,
        result=result,
        proof=proof,
        provider="nvidia-image",
        model=model,
    )
    events.emit(Event(
        opportunity_id=op.id,
        kind="B2_PROVENANCE",
        status="VERIFIED" if proof.get("manifest_verified") else "RECORDED",
        message="Durable B2 asset and native Genblaze provenance recorded.",
        data=proof,
    ))
    write_receipt(root, opportunity_id=op.id, mode="LIVE")
    return result, proof


def run_approved_pollinations_image(
    op: Opportunity,
    *,
    ledger: Ledger,
    evidence_root: str | Path,
    estimated_unit_cost: float,
    model: str = "flux",
    fallback_models: list[str] | None = None,
    timeout_seconds: int = 300,
    retry_mode: str = "disabled",
):
    """Run one real free Pollinations image provider call after the existing gates pass."""
    root = Path(evidence_root) / op.id
    events = EventLog(root / "events.jsonl")
    rights, economics, plan = preflight(
        op, ledger, root / "events.jsonl", estimated_unit_cost=estimated_unit_cost
    )
    write_json(root / "source" / "opportunity.json", op)
    write_source_snapshot(op, root / "source")
    write_json(root / "eligibility.json", rights)
    write_json(root / "economics.json", economics)
    write_json(root / "production-plan.json", plan)
    events.emit(Event(
        opportunity_id=op.id,
        kind="GENBLAZE_START",
        message="Real Genblaze Pollinations execution authorized after all gates passed.",
        data={
            "provider": "pollinations-image",
            "model": model,
            "fallback_models": fallback_models or [],
            "timeout_seconds": timeout_seconds,
            "retry_mode": retry_mode,
        },
    ))
    result = run_live_pollinations_image(
        pipeline_name=f"creative-bounty-{op.id}",
        prompt=plan.prompt,
        model=model,
        fallback_models=fallback_models,
        use_cache=True,
        timeout_seconds=timeout_seconds,
        retry_mode=retry_mode,
        structured_logging=True,
    )
    proof = summarize_genblaze_result(result)
    proof.update({
        "provider": "pollinations-image",
        "model": model,
        "actual_provider_cost": 0.0,
        "credit_type": "Public Pollinations image endpoint; no API key or billing account used",
    })
    write_json(root / "generations" / "live-001" / "genblaze-proof.json", proof)
    _write_live_evidence(
        root=root,
        op=op,
        rights=rights,
        economics=economics,
        ledger=ledger,
        result=result,
        proof=proof,
        provider="pollinations-image",
        model=model,
    )
    events.emit(Event(
        opportunity_id=op.id,
        kind="B2_PROVENANCE",
        status="VERIFIED" if proof.get("manifest_verified") else "RECORDED",
        message="Durable B2 asset and native Genblaze provenance recorded.",
        data=proof,
    ))
    write_receipt(root, opportunity_id=op.id, mode="LIVE")
    return result, proof
