from pocketflow import *
from semantic_text_splitter import TextSplitter

from config import CHUNK_MAX_TOKENS
from llm import call_llm


class GetConceptListFromChunk(Node):
    def prep(self, shared):
        concept_list = shared.get("concept_list", "No extracted concepts yet")
        chunk = shared["chunk"]
        return chunk, concept_list

    def exec(self, inputs):
        chunk, concept_list = inputs
        prompt = f"""
Given chunk of notes:
```
{chunk}
```
Previously extracted concept names: {concept_list}
Analyse the chunk and give a list of concept names present in the chunk.
Each concept should be bite-sized, constituting ONE DISTINCT learning outcome which can be seen from the chunk.
Concept names should be succinct yet accurately describe the content of the concept.
If a concept overlaps with a previously extracted concept, use the EXACT SAME concept name to ensure that there are NO duplicate concepts.
Output in yaml:
```yaml
analysis: detailed step-by-step analysis of chunk
present_concepts: list of present concept names
```
        """
        resp = call_llm(prompt)
        yaml_str = resp.split("```yaml")[1].split("```")[0].strip()
        result = yaml.safe_load(yaml_str)

        assert isinstance(result, dict)
        assert "analysis" in result
        assert "present_concepts" in result
        assert isinstance(result["present_concepts"], list)
        result["present_concepts"] = map(
            lambda x: x.strip(), result["present_concepts"]
        )

        return result

    def post(self, shared, prep_res, exec_res):
        shared["present_concepts"] = exec_res["present_concepts"]


class BatchConceptUpdateTypeSwitch(BatchNode):
    def prep(self, shared):
        concept_list = shared.get("concept_list", [])
        return [(concept, concept_list) for concept in shared["present_concepts"]]

    def exec(self, item):
        return summary

    def post(self, shared, prep_res, exec_res_list):
        return "add"

    # TODO: 'add' if concept doesnt exist yet, 'update' if concept exists


get_concept_list_node = GetConceptListFromChunk(max_retries=50)
batch_concept_update_type_switch_node = BatchConceptUpdateTypeSwitch()

get_concept_list_node >> get_concept_list_node

concept_gen_flow = Flow(start=get_concept_list_node)


def split_txt_into_chunks(text: str):
    splitter = TextSplitter.from_tiktoken_model("gpt-3.5-turbo", CHUNK_MAX_TOKENS)
    return splitter.chunks(text)
