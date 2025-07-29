from semantic_text_splitter import TextSplitter

from config import CHUNK_MAX_TOKENS


def split_txt_into_chunks(text: str):
    splitter = TextSplitter.from_tiktoken_model("gpt-3.5-turbo", CHUNK_MAX_TOKENS)
    return splitter.chunks(text)
