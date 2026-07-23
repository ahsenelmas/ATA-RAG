import os
from dataclasses import dataclass

import httpx
from dotenv import load_dotenv
from langsmith import traceable


load_dotenv()


class LLMConfigurationError(RuntimeError):
    """Raised when required LLM settings are missing."""


class LLMRequestError(RuntimeError):
    """Raised when the LLM provider request fails."""


@dataclass(slots=True)
class LLMSettings:
    base_url: str
    api_key: str
    model: str
    timeout_seconds: float = 60.0
    temperature: float = 0.1
    max_tokens: int = 700

    @classmethod
    def from_environment(cls) -> "LLMSettings":
        base_url = os.getenv(
            "LLM_BASE_URL",
            "",
        ).strip()

        api_key = os.getenv(
            "LLM_API_KEY",
            "",
        ).strip()

        model = os.getenv(
            "LLM_MODEL",
            "",
        ).strip()

        if not base_url:
            raise LLMConfigurationError(
                "LLM_BASE_URL is not configured."
            )

        if not model:
            raise LLMConfigurationError(
                "LLM_MODEL is not configured."
            )

        return cls(
            base_url=base_url.rstrip("/"),
            api_key=api_key,
            model=model,
            timeout_seconds=float(
                os.getenv(
                    "LLM_TIMEOUT_SECONDS",
                    "60",
                )
            ),
            temperature=float(
                os.getenv(
                    "LLM_TEMPERATURE",
                    "0.1",
                )
            ),
            max_tokens=int(
                os.getenv(
                    "LLM_MAX_TOKENS",
                    "700",
                )
            ),
        )


class LLMService:
    def __init__(
        self,
        settings: LLMSettings | None = None,
    ) -> None:
        self.settings = (
            settings
            or LLMSettings.from_environment()
        )

    @traceable(
        name="generate_grounded_answer",
        run_type="llm",
        tags=[
            "ata-rag",
            "groq",
            "grounded-answer",
        ],
    )
    def generate_answer(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        endpoint = (
            f"{self.settings.base_url}"
            "/chat/completions"
        )

        headers = {
            "Content-Type": "application/json",
        }

        if self.settings.api_key:
            headers["Authorization"] = (
                f"Bearer {self.settings.api_key}"
            )

        payload = {
            "model": self.settings.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            "temperature": (
                self.settings.temperature
            ),
            "max_tokens": (
                self.settings.max_tokens
            ),
        }

        try:
            with httpx.Client(
                timeout=self.settings.timeout_seconds,
            ) as client:
                response = client.post(
                    endpoint,
                    headers=headers,
                    json=payload,
                )

                response.raise_for_status()

        except httpx.HTTPStatusError as error:
            response_text = (
                error.response.text[:1000]
            )

            raise LLMRequestError(
                "LLM provider returned "
                f"HTTP {error.response.status_code}: "
                f"{response_text}"
            ) from error

        except httpx.TimeoutException as error:
            raise LLMRequestError(
                "The LLM provider request timed out."
            ) from error

        except httpx.HTTPError as error:
            raise LLMRequestError(
                f"LLM request failed: {error}"
            ) from error

        try:
            data = response.json()

            answer = data["choices"][0][
                "message"
            ]["content"]

        except (
            KeyError,
            IndexError,
            TypeError,
            ValueError,
        ) as error:
            raise LLMRequestError(
                "Unexpected LLM response structure."
            ) from error

        cleaned_answer = str(answer).strip()

        if not cleaned_answer:
            raise LLMRequestError(
                "The LLM returned an empty answer."
            )

        return cleaned_answer
