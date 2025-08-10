import base64
from io import BytesIO

import fitz
from docx import Document
from pptx import Presentation

from llm import call_vlm


def vlm_process_image(b64_image, img_type):
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
        img_type,
    )


def process_file(
    file: bytes, filename: str, content_type: str
):  # txt/md, images, pptx, word, pdf
    match content_type:
        case "txt":  # *applies for markdown obviously since its just txt
            # To read a FastAPI SpooledTemporaryFile (which is the underlying file object of an UploadFile) as text, the recommended approach is to use io.TextIOWrapper for proper encoding handling.
            return file.decode("utf-8")
        case "png":
            return call_vlm(base64.b64encode(file).decode("utf-8"), "png")
        case "jpeg":
            return call_vlm(base64.b64encode(file).decode("utf-8"), "jpeg")
        case "pptx":
            slides = Presentation(BytesIO(file)).slides

            slides_notes = ""
            for slide in slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        slides_notes += shape.text + "\n"
                    if hasattr(shape, "image"):
                        slides_notes += (
                            "\n"
                            + "===IMAGE START==="
                            + call_vlm(
                                shape.image.blob,
                                shape.image.content_type.replace("image/", ""),
                            )
                            + "===IMAGE END==="
                            + "\n"
                        )

            return slides_notes
        case "docx":
            doc = Document(BytesIO(file))
            docx_notes = ""

            for para in doc.paragraphs:
                for run in para.runs:
                    if run.text:
                        docx_notes += run.text

                    drawing_elems = run._element.findall(
                        ".//w:drawing", namespaces=run._element.nsmap
                    )
                    for drawing in drawing_elems:
                        namespaces = drawing.nsmap.copy() if drawing.nsmap else {}
                        if "a" not in namespaces:
                            namespaces["a"] = (
                                "http://schemas.openxmlformats.org/drawingml/2006/main"
                            )

                        blip = drawing.find(".//a:blip", namespaces=namespaces)
                        if blip is not None:
                            embed_rid = blip.get(qn("r:embed"))
                            image_part = doc.part.related_parts[embed_rid]

                            blob = image_part.blob
                            content_type = image_part.content_type  # e.g. image/png

                            docx_notes += (
                                "\n===IMAGE START===\n"
                                + call_vlm(blob, content_type.replace("image/", ""))
                                + "\n===IMAGE END===\n"
                            )

                docx_notes += "\n"

            return docx_notes
        case "pdf":
            doc = fitz.open("pdf", file)
            pdf_notes = ""
            for page in doc:
                pdf_notes += page.get_text("text") + "\n"

                for img_index, img in enumerate(page.get_images(full=True)):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    blob = base_image["image"]
                    b64_blob = base64.b64encode(blob).decode("utf-8")
                    ext = base_image["ext"]
                    pdf_notes += (
                        "\n===IMAGE START===\n"
                        + call_vlm(b64_blob, ext)
                        + "\n===IMAGE END===\n"
                    )
            return pdf_notes
        case _:
            raise ValueError("Invalid content_type")
