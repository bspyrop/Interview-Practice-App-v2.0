import tiktoken

PRICING_PER_1M = {
    "gpt-4.1": {"input": 3.00, "output": 12.00, "cached_input": 0.75},
    "gpt-4.1-mini": {"input": 0.80, "output": 3.20, "cached_input": 0.20},
}

# def count_tokens_openai(model: str, text: str) -> int:
#     encoding = tiktoken.encoding_for_model(model)
#     tokens = encoding.encode(text)
#     return len(tokens)

def count_tokens(text: str, model_for_encoding: str = "gpt-4.1") -> int:
    # tiktoken encoding names sometimes differ; cl100k_base is a safe default for many OpenAI models
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text or ""))

def estimate_cost_usd(model: str, input_tokens: int, output_tokens: int, cached_input_tokens: int = 0) -> float:
    p = PRICING_PER_1M[model]
    billable_input = max(0, input_tokens - cached_input_tokens)
    cost = (billable_input / 1_000_000) * p["input"] + (output_tokens / 1_000_000) * p["output"]
    if cached_input_tokens > 0:
        cost += (cached_input_tokens / 1_000_000) * p["cached_input"]
    return cost