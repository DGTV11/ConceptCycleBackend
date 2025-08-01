from tempfile import SpooledTemporaryFile

from llm import call_vlm


def vlm_process_image(b64_image):
    return call_vlm(
        """
# MISSION
You are a Sparse Priming Representation (SPR) writer. An SPR is a particular kind of use of language for advanced NLP, NLU, and NLG tasks, particularly useful for the latest generation of Large Language Models (LLMs). You will be given information by the USER which you are to render as an SPR.

# THEORY
LLMs are a kind of deep neural network. They have been demonstrated to embed knowledge, abilities, and concepts, ranging from reasoning to planning, and even to theory of mind. These are called latent abilities and latent content, collectively referred to as latent space. The latent space of an LLM can be activated with the correct series of words as inputs, which will create a useful internal state of the neural network. This is not unlike how the right shorthand cues can prime a human mind to think in a certain way. Like human minds, LLMs are associative, meaning you only need to use the correct associations to "prime" another model to think in the same way.

# METHODOLOGY
Render the input as a distilled list of succinct statements, assertions, associations, concepts, analogies, and metaphors. The idea is to capture as much, conceptually, as possible but with as few words as possible. Write it in a way that makes sense to you, as the future audience will be another language model, not a human.
""",  # *https://github.com/daveshap/SparsePrimingRepresentations
        b64_image,
    )


def process_file(
    file: SpooledTemporaryFile, content_type: str
):  # txt/md, images, pptx, word, pdf
    match content_type:
        case 'txt': #*applies for markdown obviously since its just txt
            # To read a FastAPI SpooledTemporaryFile (which is the underlying file object of an UploadFile) as text, the recommended approach is to use io.TextIOWrapper for proper encoding handling.
            #TODO: pass in file obj from input directly?
            pass
        case 'png':
            pass
        case 'jpeg':
            pass
        case 'pptx':
            pass
        case 'word':
            pass
        case 'pdf':
        case _:
            raise ValueError("Invalid content_type")
