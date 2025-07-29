#core/llm_client.py
import requests
import json
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not logger.hasHandlers():
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

class LLMClient:
    def __init__(self, api_url="http://localhost:11434/api/chat", default_model="llama2:13b", stream=True):
        self.api_url = api_url
        self.default_model = default_model
        self.stream = stream
        logger.debug(f"[DEBUG] LLMClient initialized with api_url={api_url}, default_model={default_model}, stream={stream}")

    def call_model(self, model_name, messages):
        """Sends a prompt and message history to the Ollama server."""
        logger.info(f"[AI] Using model: {model_name}")
        response_parts = []

        try:
            res = requests.post(
                self.api_url,
                json={"model": model_name, "messages": messages, "stream": self.stream},
                timeout=60,
                stream=self.stream
            )
            res.raise_for_status()
            logger.debug("[DEBUG] POST request to Ollama successful, processing stream...")

            for line in res.iter_lines():
                if line:
                    decoded_line = line.decode("utf-8")
                    try:
                        obj = json.loads(decoded_line)
                        if "message" in obj and "content" in obj["message"]:
                            content = obj["message"]["content"]
                            response_parts.append(content)
                            logger.debug(f"[AI] Received chunk: {content[:30]}...")  # Log first 30 chars of chunk
                        elif obj.get("done", False):
                            logger.debug("[DEBUG] Received done signal from Ollama stream.")
                            break
                    except json.JSONDecodeError:
                        logger.warning("[WARN] Could not parse line from Ollama.")
        except requests.Timeout:
            logger.error("[ERROR] Timeout occurred from the model.")
            return "[O-ni] Timeout occurred from the model."
        except requests.RequestException as e:
            logger.error(f"[ERROR] Request error: {e}")
            return f"[O-ni] Request error: {str(e)}"
        except Exception as e:
            logger.error(f"[ERROR] Unknown error: {e}", exc_info=True)
            return f"[O-ni] Unknown error: {str(e)}"

        result = "".join(response_parts).strip() or "[O-ni] No response returned."
        logger.info(f"[AI] Model response length: {len(result)}")
        return result

    def build_prompt(self, system_prompt, history, user_input):
        """Builds a complete chat prompt for a user."""
        logger.debug("[DEBUG] Building prompt with system prompt, history length: %d, user input length: %d",
                     len(history), len(user_input))
        return [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": user_input}]