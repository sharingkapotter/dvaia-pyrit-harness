"""Custom PyRIT target for the DVAIA Direct Injection endpoint."""
import httpx
from pyrit.models import Message, construct_response_from_request
from pyrit.prompt_target import PromptTarget


class DVAIADirectTarget(PromptTarget):
    """Sends a prompt to DVAIA's /api/chat endpoint and returns the model reply."""

    def __init__(self, *, endpoint="http://127.0.0.1:5000/api/chat",
                 model_id="openai:gpt-4o-mini", temperature=0.0):
        super().__init__()
        self._endpoint = endpoint
        self._model_id = model_id
        self._temperature = temperature

    async def _send_prompt_to_target_async(self, *, normalized_conversation: list[Message]) -> list[Message]:
        request_piece = normalized_conversation[-1].get_piece()
        prompt_text = request_piece.converted_value

        payload = {
            "prompt": prompt_text,
            "model_id": self._model_id,
            "llm_provider": "openai",
            "options": {"temperature": self._temperature, "top_p": 0.95, "max_tokens": 200},
        }

        async with httpx.AsyncClient(timeout=60) as client:
            http_response = await client.post(self._endpoint, json=payload)
            http_response.raise_for_status()
            data = http_response.json()

        reply_text = data.get("response", str(data))
        response = construct_response_from_request(request=request_piece, response_text_pieces=[reply_text])
        return [response]