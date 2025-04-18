import time
from typing import Final, final

import tiktoken
from openai.lib.azure import AzureOpenAI
from tiktoken import Encoding

from definitions import Embeddings


@final
class AzureOpenAIEmbeddings:
    """
    Utility class for the Azure OpenAI framework.
    """
    _MAX_TOKENS: Final[int] = 8192
    _TOKENIZER: Final[Encoding] = tiktoken.get_encoding("cl100k_base")

    @staticmethod
    def _split_text_into_chunks(text: str, max_tokens: int = _MAX_TOKENS) -> list[str]:
        """
        Splits the text into chunks that have a maximum number of tokens specified by max_tokens.
        :param text: The text to split.
        :param max_tokens: The maximum number of tokens in each chunk. The default value is 8192.
        :return: A list of text chunks.
        :raises RuntimeError: If an error occurs during tokenization.
        :raises ValueError: If the input text is empty or not a string.
        """
        chunks = []

        if not isinstance(text, str) or not text:
            raise ValueError("Input text must be a non-empty string.")

        try:
            start = 0
            tokens = AzureOpenAIEmbeddings._TOKENIZER.encode(text)

            while start < len(tokens):
                # Constrain the index.
                end = min(start + max_tokens, len(tokens))

                # Decode the tokens back into string text to form a chunk.
                chunk = AzureOpenAIEmbeddings._TOKENIZER.decode(tokens[start:end])

                # Add the chunk to the list of chunks.
                chunks.append(chunk)

                # Update the start index to the end of the last chunk to continue from there.
                start = end
        except Exception as exception:
            raise RuntimeError(f"Unable to split text into chunks: {exception}")

        return chunks

    @staticmethod
    def generate(client: AzureOpenAI, *, model: str, text: str, max_retries: int = 5) -> list[Embeddings]:
        """
        Generate embeddings for the text using the specified model.
        :param client: The Azure OpenAI client.
        :param model: The model to use.
        :param text: The text to generate embeddings for.
        :param max_retries: The maximum number of retries in case of a failed attempt. The default value is 5.
        :return: A list containing the embeddings for each chunk of text.
        :raises RuntimeError: If the maximum number of retries is reached while generating embeddings.
        :raises ValueError: If the input text is empty or not a string.
        """
        base_wait_time = 4  # Initial wait time for the exponential backoff strategy.
        chunks = AzureOpenAIEmbeddings._split_text_into_chunks(text, AzureOpenAIEmbeddings._MAX_TOKENS)
        embeddings = []

        for chunk in chunks:
            for attempt in range(max_retries):
                try:
                    response = client.embeddings.create(input=[chunk], model=model)
                    embeddings.append(response.data[0].embedding)
                    break
                except Exception as exception:
                    wait_time = base_wait_time * (2 ** attempt)
                    time.sleep(wait_time)

                    if attempt == max_retries - 1:
                        raise RuntimeError(f"Unable to generate embeddings: {exception}")

        return embeddings
