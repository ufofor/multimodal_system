from openai import OpenAI

_client = OpenAI()
MODEL = "text-embedding-3-small"


def embed_texts(texts: list[str]) -> list[list[float]]:
    response = _client.embeddings.create(model=MODEL, input=texts)
    return [item.embedding for item in response.data]


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]
