from pocketflow import *
from semantic_text_splitter import TextSplitter

from config import CHUNK_MAX_TOKENS
from llm import call_llm


# *CONCEPT LIST UPDATE
class BatchConceptUpdate(BatchFlow):
    def prep(self, shared):
        return [
            {"single_present_concept": concept}
            for concept in shared["present_concepts"]
        ]


class ConceptUpdateTypeSwitch(Node):
    def prep(self, shared):
        concept_dict = shared.get("concept_dict", {})
        single_present_concept = self.params["single_present_concept"]

        return single_present_concept, concept_dict

    def post(self, shared, prep_res, exec_res):
        single_present_concept, concept_dict = prep_res

        return "append" if (single_present_concept in concept_dict) else "add"


class ConceptAdd(Node):
    def prep(self, shared):
        pass

    def exec(self, inputs):
        pass

    def post(self, shared, prep_res, exec_res):
        pass


class ConceptAppend(Node):
    def prep(self, shared):
        pass

    def exec(self, inputs):
        pass

    def post(self, shared, prep_res, exec_res):
        pass


concept_update_type_switch_node = ConceptUpdateTypeSwitch()
concept_add_node = ConceptAdd()
concept_append_node = ConceptAppend()

concept_update_type_switch_node - "add" >> ConceptAdd()
concept_update_type_switch_node - "append" >> ConceptAppend()

concept_update = Flow(start=concept_update_type_switch_node)
batch_concept_update = BatchConceptUpdate(start=concept_update)


# *CONCEPT EXTRACTOR
class ConceptExtractor(BatchFlow):
    def prep(self, shared):
        notes = self.params["notes"]
        splitter = TextSplitter.from_tiktoken_model("gpt-3.5-turbo", CHUNK_MAX_TOKENS)
        return [{"chunk": chunk} for chunk in splitter.chunks(notes)]


class GetConceptListFromChunk(Node):
    def prep(self, shared):
        concept_dict = shared.get("concept_dict", {})
        concept_list = list(concept_dict.keys()) or "No extracted concepts yet"
        chunk = self.params["chunk"]
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
If you observe no concepts in the chunk, you may generate an empty list for present_concepts.
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


get_concept_list_node = GetConceptListFromChunk(max_retries=50)

get_concept_list_node >> batch_concept_update

concept_extractor_chunk_flow = Flow(start=get_concept_list_node)
concept_extractor_batch_flow = ConceptExtractor(start=concept_extractor_chunk_flow)


def extract_concepts(notes: str):
    concept_extractor_batch_flow.set_params({"notes": notes})
    concept_extractor_batch_flow.run(shared)
