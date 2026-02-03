"""MedGemma model loading and inference.

Handles loading the MedGemma 4B multimodal model with 4-bit quantization
via bitsandbytes, and provides inference methods for both image+text
(multimodal) and text-only generation.

The model is loaded once and shared across all agents.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

if TYPE_CHECKING:
    from PIL import Image

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """Configuration for MedGemma model loading."""

    model_id: str = "google/medgemma-4b-it"
    quantization_bits: int = 4
    max_new_tokens: int = 1024
    temperature: float = 0.3
    top_p: float = 0.9
    device_map: str = "auto"
    torch_dtype: str = "float16"
    trust_remote_code: bool = True


class MedGemmaModel:
    """Wrapper for MedGemma 4B model with quantized inference.

    Provides both multimodal (image+text) and text-only generation
    capabilities. Loads the model once and caches it for reuse
    across all agents in the pipeline.
    """

    def __init__(self, config: ModelConfig | None = None) -> None:
        self.config = config or ModelConfig()
        self._model: Any = None
        self._processor: Any = None
        self._loaded = False

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def load(self) -> None:
        """Load the model and processor with quantization.

        Requires CUDA-capable GPU with sufficient VRAM.
        """
        import torch
        from transformers import AutoModelForCausalLM, AutoProcessor, BitsAndBytesConfig

        logger.info("Loading MedGemma model: %s", self.config.model_id)

        dtype_map = {
            "float16": torch.float16,
            "bfloat16": torch.bfloat16,
            "float32": torch.float32,
        }
        torch_dtype = dtype_map.get(self.config.torch_dtype, torch.float16)

        quantization_config = None
        if self.config.quantization_bits == 4:
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch_dtype,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
            )
        elif self.config.quantization_bits == 8:
            quantization_config = BitsAndBytesConfig(load_in_8bit=True)

        self._processor = AutoProcessor.from_pretrained(
            self.config.model_id,
            trust_remote_code=self.config.trust_remote_code,
        )

        self._model = AutoModelForCausalLM.from_pretrained(
            self.config.model_id,
            quantization_config=quantization_config,
            device_map=self.config.device_map,
            torch_dtype=torch_dtype,
            trust_remote_code=self.config.trust_remote_code,
        )

        self._loaded = True
        logger.info("MedGemma model loaded successfully")

    def _ensure_loaded(self) -> None:
        """Verify model and processor are loaded, raise if not."""
        if not self._loaded or self._model is None or self._processor is None:
            raise RuntimeError("Model not loaded. Call load() first.")

    def generate_multimodal(
        self, image: Image.Image, prompt: str, system_prompt: str = "",
        max_new_tokens: int | None = None, temperature: float | None = None,
    ) -> str:
        """Generate text from an image + text prompt (for Agent 1).

        Args:
            image: PIL Image to analyze.
            prompt: Text prompt to guide analysis.
            system_prompt: Optional system-level instructions.
            max_new_tokens: Override default max tokens.
            temperature: Override default temperature.

        Returns:
            Generated text response.
        """
        self._ensure_loaded()

        import torch

        messages: list[dict[str, Any]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": prompt},
            ],
        })

        input_text = self._processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = self._processor(
            text=input_text, images=[image], return_tensors="pt"
        ).to(self._model.device)

        gen_kwargs = self._generation_kwargs(max_new_tokens, temperature)

        with torch.inference_mode():
            output_ids = self._model.generate(**inputs, **gen_kwargs)

        # Decode only the newly generated tokens
        input_len = inputs["input_ids"].shape[-1]
        generated = output_ids[0][input_len:]
        return self._processor.decode(generated, skip_special_tokens=True).strip()

    def generate_text(
        self, prompt: str, system_prompt: str = "",
        max_new_tokens: int | None = None, temperature: float | None = None,
    ) -> str:
        """Generate text from a text-only prompt (for Agents 2 and 3).

        Args:
            prompt: Text prompt for generation.
            system_prompt: Optional system-level instructions.
            max_new_tokens: Override default max tokens.
            temperature: Override default temperature.

        Returns:
            Generated text response.
        """
        self._ensure_loaded()

        import torch

        messages: list[dict[str, Any]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        input_text = self._processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = self._processor(
            text=input_text, return_tensors="pt"
        ).to(self._model.device)

        gen_kwargs = self._generation_kwargs(max_new_tokens, temperature)

        with torch.inference_mode():
            output_ids = self._model.generate(**inputs, **gen_kwargs)

        input_len = inputs["input_ids"].shape[-1]
        generated = output_ids[0][input_len:]
        return self._processor.decode(generated, skip_special_tokens=True).strip()

    def _generation_kwargs(
        self, max_new_tokens: int | None, temperature: float | None,
    ) -> dict[str, Any]:
        """Build generation kwargs from config + overrides."""
        temp = temperature if temperature is not None else self.config.temperature
        kwargs: dict[str, Any] = {
            "max_new_tokens": (
                max_new_tokens if max_new_tokens is not None
                else self.config.max_new_tokens
            ),
            "top_p": self.config.top_p,
            "do_sample": temp > 0,
        }
        if temp > 0:
            kwargs["temperature"] = temp
        return kwargs

    @classmethod
    def from_yaml(cls, config_path: str | Path) -> MedGemmaModel:
        """Create a MedGemmaModel from a YAML config file."""
        config_path = Path(config_path)
        with open(config_path) as f:
            raw = yaml.safe_load(f)

        model_cfg = raw.get("model", {})
        config = ModelConfig(
            model_id=model_cfg.get("model_id", ModelConfig.model_id),
            quantization_bits=model_cfg.get("quantization_bits", ModelConfig.quantization_bits),
            max_new_tokens=model_cfg.get("max_new_tokens", ModelConfig.max_new_tokens),
            temperature=model_cfg.get("temperature", ModelConfig.temperature),
            top_p=model_cfg.get("top_p", ModelConfig.top_p),
            device_map=model_cfg.get("device_map", ModelConfig.device_map),
            torch_dtype=model_cfg.get("torch_dtype", ModelConfig.torch_dtype),
            trust_remote_code=model_cfg.get("trust_remote_code", ModelConfig.trust_remote_code),
        )
        return cls(config)
