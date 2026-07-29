"""Fail-closed LIVE Genblaze integration.

No function here decides whether spending is allowed. Callers must pass rights,
budget and production-plan gates before invoking a provider.

The adapter intentionally mirrors the current documented Genblaze primitives:
Pipeline, Modality, StepCache, ObjectStorageSink, fallback_models, provider
RetryPolicy and optional LoggingTracer.
"""
from __future__ import annotations
import base64
from importlib.metadata import PackageNotFoundError, version
import os
import re
import tempfile
from urllib.parse import quote
import urllib.request
from pathlib import Path

GENBLAZE_PACKAGES = ("genblaze-core", "genblaze-s3", "genblaze-openai", "google-genai", "genblaze-nvidia")


def installed_versions() -> dict[str, str]:
    versions = {}
    for package in GENBLAZE_PACKAGES:
        try:
            versions[package] = version(package)
        except PackageNotFoundError:
            versions[package] = "not-installed"
    return versions


def live_ready(provider: str = "openai") -> tuple[bool, list[str]]:
    missing=[]
    for key in ("B2_KEY_ID", "B2_APP_KEY", "B2_BUCKET"):
        if not os.getenv(key):
            missing.append(key)
    provider_keys = {
        "openai": ("OPENAI_API_KEY",),
        "google": ("GOOGLE_API_KEY", "GEMINI_API_KEY", "GOOGLE_GENAI_API_KEY", "GOOGLE_APPLICATION_CREDENTIALS"),
        "nvidia": ("NVIDIA_API_KEY", "NVIDIA_NIM_API_KEY"),
        "pollinations": (),
    }
    api_keys = provider_keys.get(provider, ())
    if api_keys and not any(os.getenv(key) for key in api_keys):
        missing.append(" or ".join(api_keys))
    try:
        from genblaze_core.pipeline.pipeline import Pipeline  # noqa:F401
        from genblaze_core.models.enums import Modality  # noqa:F401
        from genblaze_core.pipeline.cache import StepCache  # noqa:F401
        from genblaze_core.observability.tracer import LoggingTracer  # noqa:F401
        from genblaze_core.providers.retry import RetryPolicy  # noqa:F401
        from genblaze_core.storage.sink import ObjectStorageSink, KeyStrategy  # noqa:F401
        from genblaze_s3 import S3StorageBackend  # noqa:F401
        if provider == "openai":
            from genblaze_openai import DalleProvider  # noqa:F401
        if provider == "google":
            from google import genai  # noqa:F401
        if provider == "nvidia":
            from genblaze_nvidia import NvidiaImageProvider  # noqa:F401
    except ImportError:
        missing.append("Genblaze provider/storage packages")
    return not missing, missing


def build_b2_sink(*, content_addressable: bool = False):
    from genblaze_core.storage.sink import ObjectStorageSink, KeyStrategy
    strategy = KeyStrategy.CONTENT_ADDRESSABLE if content_addressable else KeyStrategy.HIERARCHICAL
    return ObjectStorageSink(
        build_b2_backend(),
        key_strategy=strategy,
    )


def build_b2_backend():
    from genblaze_s3 import S3StorageBackend
    try:
        return S3StorageBackend.for_backblaze(
            os.environ["B2_BUCKET"],
            region=os.getenv("B2_REGION"),
        )
    except Exception as exc:
        match = re.search(r"region='([^']+)'", str(exc))
        if not match:
            raise
        return S3StorageBackend.for_backblaze(
            os.environ["B2_BUCKET"],
            region=match.group(1),
        )


def run_live_openai_image(
    *,
    pipeline_name: str,
    prompt: str,
    model: str = "dall-e-3",
    fallback_models: list[str] | None = None,
    use_cache: bool = True,
    content_addressable: bool = False,
    timeout_seconds: int = 300,
    retry_mode: str = "conservative",
    structured_logging: bool = True,
):
    """Execute one real image step and persist its manifest + asset to B2.

    No cost is inferred here. The caller is responsible for preflight budget
    authorization and later reconciliation of actual provider charges.

    retry_mode: "conservative" (recommended for cost control), "aggressive",
    or "disabled", matching documented Genblaze RetryPolicy constructors.
    """
    ready, missing = live_ready("openai")
    if not ready:
        raise RuntimeError("LIVE mode unavailable: " + ", ".join(missing))
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")
    if retry_mode not in {"conservative", "aggressive", "disabled"}:
        raise ValueError("retry_mode must be conservative, aggressive, or disabled")

    from genblaze_core.pipeline.pipeline import Pipeline
    from genblaze_core.models.enums import Modality
    from genblaze_core.pipeline.cache import StepCache
    from genblaze_core.providers.retry import RetryPolicy
    from genblaze_openai import DalleProvider

    retry_factory = getattr(RetryPolicy, retry_mode)
    provider = DalleProvider(retry_policy=retry_factory())

    tracer = None
    if structured_logging:
        from genblaze_core.observability.tracer import LoggingTracer
        tracer = LoggingTracer()

    pipeline = Pipeline(pipeline_name, tracer=tracer) if tracer is not None else Pipeline(pipeline_name)
    if use_cache:
        pipeline = pipeline.cache(StepCache(".genblaze-cache/"))

    step_kwargs = dict(model=model, prompt=prompt, modality=Modality.IMAGE)
    if fallback_models:
        step_kwargs["fallback_models"] = fallback_models

    return pipeline.step(provider, **step_kwargs).run(
        sink=build_b2_sink(content_addressable=content_addressable),
        timeout=timeout_seconds,
    )


def run_live_pollinations_image(
    *,
    pipeline_name: str,
    prompt: str,
    model: str = "flux",
    fallback_models: list[str] | None = None,
    use_cache: bool = True,
    content_addressable: bool = False,
    timeout_seconds: int = 300,
    retry_mode: str = "disabled",
    structured_logging: bool = True,
):
    """Execute one free public Pollinations image step and persist through B2."""
    ready, missing = live_ready("pollinations")
    if not ready:
        raise RuntimeError("LIVE mode unavailable: " + ", ".join(missing))
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")
    if retry_mode not in {"conservative", "aggressive", "disabled"}:
        raise ValueError("retry_mode must be conservative, aggressive, or disabled")

    from genblaze_core.pipeline.pipeline import Pipeline
    from genblaze_core.models.enums import Modality
    from genblaze_core.pipeline.cache import StepCache
    from genblaze_core.providers.retry import RetryPolicy
    from genblaze_core._utils import local_file_url
    from genblaze_core.models.asset import Asset
    from genblaze_core.providers.base import BaseProvider

    class PollinationsImageProvider(BaseProvider):
        name = "pollinations-image"

        def submit(self, step, config=None):
            width = int(step.params.get("width", 1024))
            height = int(step.params.get("height", 1024))
            seed = int(step.params.get("seed", 20260729))
            safe = "true" if step.params.get("safe", True) else "false"
            nologo = "true" if step.params.get("nologo", True) else "false"
            prompt_path = quote(step.prompt or "", safe="")
            return (
                f"https://image.pollinations.ai/prompt/{prompt_path}"
                f"?width={width}&height={height}&seed={seed}&model={quote(step.model)}"
                f"&nologo={nologo}&safe={safe}"
            )

        def poll(self, prediction_id, config=None):
            return True

        def fetch_output(self, prediction_id, step):
            req = urllib.request.Request(
                prediction_id,
                headers={"User-Agent": "creative-bounty-devpost-proof/1.0"},
            )
            with urllib.request.urlopen(req, timeout=timeout_seconds) as response:
                data = response.read()
                media_type = response.headers.get("content-type") or "image/jpeg"
            if not data or not media_type.startswith("image/"):
                raise RuntimeError(f"Pollinations returned non-image response: {media_type}")
            suffix = ".png" if "png" in media_type else ".jpg"
            fd, tmp = tempfile.mkstemp(suffix=suffix)
            os.close(fd)
            out_path = Path(tmp)
            out_path.write_bytes(data)
            step.assets.append(Asset(url=local_file_url(out_path.resolve()), media_type=media_type))
            return step

    retry_factory = getattr(RetryPolicy, retry_mode)
    provider = PollinationsImageProvider(retry_policy=retry_factory())

    tracer = None
    if structured_logging:
        from genblaze_core.observability.tracer import LoggingTracer
        tracer = LoggingTracer()

    pipeline = Pipeline(pipeline_name, tracer=tracer) if tracer is not None else Pipeline(pipeline_name)
    if use_cache:
        pipeline = pipeline.cache(StepCache(".genblaze-cache/"))

    step_kwargs = dict(model=model, prompt=prompt, modality=Modality.IMAGE)
    if fallback_models:
        step_kwargs["fallback_models"] = fallback_models

    return pipeline.step(provider, **step_kwargs).run(
        sink=build_b2_sink(content_addressable=content_addressable),
        timeout=timeout_seconds,
    )


def run_live_google_image(
    *,
    pipeline_name: str,
    prompt: str,
    model: str = "gemini-3.1-flash-lite-image",
    fallback_models: list[str] | None = None,
    use_cache: bool = True,
    content_addressable: bool = False,
    timeout_seconds: int = 300,
    retry_mode: str = "disabled",
    structured_logging: bool = True,
):
    """Execute one real Google Imagen step and persist its manifest + asset to B2."""
    ready, missing = live_ready("google")
    if not ready:
        raise RuntimeError("LIVE mode unavailable: " + ", ".join(missing))
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")
    if retry_mode not in {"conservative", "aggressive", "disabled"}:
        raise ValueError("retry_mode must be conservative, aggressive, or disabled")

    from genblaze_core.pipeline.pipeline import Pipeline
    from genblaze_core.models.enums import Modality
    from genblaze_core.pipeline.cache import StepCache
    from genblaze_core.providers.retry import RetryPolicy
    from genblaze_core._utils import local_file_url
    from genblaze_core.models.asset import Asset
    from genblaze_core.providers.base import BaseProvider
    from google import genai

    class GeminiImageProvider(BaseProvider):
        name = "google-gemini-image"

        def __init__(self, *, retry_policy=None):
            super().__init__(retry_policy=retry_policy)
            self._client = genai.Client(
                api_key=(
                    os.getenv("GEMINI_API_KEY")
                    or os.getenv("GOOGLE_API_KEY")
                    or os.getenv("GOOGLE_GENAI_API_KEY")
                )
            )

        def submit(self, step, config=None):
            from google.genai import types

            response = self._client.models.generate_images(
                model=step.model,
                prompt=step.prompt or "",
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio=step.params.get("aspect_ratio", "1:1"),
                    image_size=step.params.get("image_size", "1K"),
                    output_mime_type="image/jpeg",
                ),
            )
            return response

        def poll(self, prediction_id, config=None):
            return True

        def fetch_output(self, prediction_id, step):
            response = prediction_id
            generated_images = getattr(response, "generated_images", None) or []
            if not generated_images or getattr(generated_images[0], "image", None) is None:
                raise RuntimeError("Gemini image generation returned no generated image")
            output_image = generated_images[0].image
            image_bytes = getattr(output_image, "image_bytes", None)
            if not image_bytes:
                raise RuntimeError("Gemini image generation returned empty image bytes")
            fd, tmp = tempfile.mkstemp(suffix=".jpg")
            os.close(fd)
            out_path = Path(tmp)
            out_path.write_bytes(image_bytes)
            step.assets.append(Asset(url=local_file_url(out_path.resolve()), media_type="image/jpeg"))
            return step

    retry_factory = getattr(RetryPolicy, retry_mode)
    provider = GeminiImageProvider(retry_policy=retry_factory())

    tracer = None
    if structured_logging:
        from genblaze_core.observability.tracer import LoggingTracer
        tracer = LoggingTracer()

    pipeline_kwargs = {"preflight": False}
    pipeline = (
        Pipeline(pipeline_name, tracer=tracer, **pipeline_kwargs)
        if tracer is not None
        else Pipeline(pipeline_name, **pipeline_kwargs)
    )
    if use_cache:
        pipeline = pipeline.cache(StepCache(".genblaze-cache/"))

    step_kwargs = dict(model=model, prompt=prompt, modality=Modality.IMAGE)
    if fallback_models:
        step_kwargs["fallback_models"] = fallback_models

    return pipeline.step(provider, **step_kwargs).run(
        sink=build_b2_sink(content_addressable=content_addressable),
        timeout=timeout_seconds,
    )


def run_live_nvidia_image(
    *,
    pipeline_name: str,
    prompt: str,
    model: str = "black-forest-labs/flux.1-schnell",
    fallback_models: list[str] | None = None,
    use_cache: bool = True,
    content_addressable: bool = False,
    timeout_seconds: int = 300,
    retry_mode: str = "disabled",
    structured_logging: bool = True,
):
    """Execute one real NVIDIA NIM image step and persist its manifest + asset to B2."""
    ready, missing = live_ready("nvidia")
    if not ready:
        raise RuntimeError("LIVE mode unavailable: " + ", ".join(missing))
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")
    if retry_mode not in {"conservative", "aggressive", "disabled"}:
        raise ValueError("retry_mode must be conservative, aggressive, or disabled")

    from genblaze_core.pipeline.pipeline import Pipeline
    from genblaze_core.models.enums import Modality
    from genblaze_core.pipeline.cache import StepCache
    from genblaze_core.providers.retry import RetryPolicy
    from genblaze_nvidia import NvidiaImageProvider

    retry_factory = getattr(RetryPolicy, retry_mode)
    provider = NvidiaImageProvider(
        retry_policy=retry_factory(),
        http_timeout=float(timeout_seconds),
        nvcf_timeout=float(timeout_seconds),
    )

    tracer = None
    if structured_logging:
        from genblaze_core.observability.tracer import LoggingTracer
        tracer = LoggingTracer()

    pipeline = Pipeline(pipeline_name, tracer=tracer) if tracer is not None else Pipeline(pipeline_name)
    if use_cache:
        pipeline = pipeline.cache(StepCache(".genblaze-cache/"))

    step_kwargs = dict(model=model, prompt=prompt, modality=Modality.IMAGE)
    if fallback_models:
        step_kwargs["fallback_models"] = fallback_models

    return pipeline.step(provider, **step_kwargs).run(
        sink=build_b2_sink(content_addressable=content_addressable),
        timeout=timeout_seconds,
    )
