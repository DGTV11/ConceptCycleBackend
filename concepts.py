import yaml
from pocketflow import *
from semantic_text_splitter import TextSplitter

from config import CHUNK_MAX_TOKENS
from llm import call_llm


# *CONCEPT LIST UPDATE
class BatchConceptUpdate(BatchFlow):
    def prep(self, shared):
        concepts = [
            {"single_present_concept": concept}
            for concept in shared["present_concepts"]
        ]

        print(concepts)

        return concepts


class ConceptUpdateTypeSwitch(Node):
    def prep(self, shared):
        concept_dict = shared["concept_dict"]
        single_present_concept = self.params["single_present_concept"]

        return single_present_concept, concept_dict

    def post(self, shared, prep_res, exec_res):
        single_present_concept, concept_dict = prep_res

        return "append" if (single_present_concept in concept_dict) else "add"


# *https://github.com/daveshap/SparsePrimingRepresentations
class ConceptAdd(Node):
    def prep(self, shared):
        single_present_concept = self.params["single_present_concept"]
        chunk = self.params["chunk"]

        return single_present_concept, chunk

    def exec(self, inputs):
        single_present_concept, chunk = inputs
        prompt = f"""
Given chunk of notes:
```
{chunk}
```
Target concept name: {single_present_concept}
Analyse the chunk to pick out which part of the chunk is relevant to the target concept (e.g. make possible learning outcome from target concept name then pick out content which satisfies the learning outcome).
You will then give distilled succinct statements, assertions, associations, concepts, analogies, and metaphors. 
The idea is to capture as much, conceptually, as possible but with as few words as possible. 
Write it in a way that makes sense to you, as the future audience will be another language model, not a human.
Output in yaml:
```yaml
analysis: detailed step-by-step analysis of chunk (ONE string)
extracted_concept_info: extracted info relevant to the target concept (ONE string)
```
        """
        resp = call_llm(prompt)
        yaml_str = resp.split("```yaml")[1].split("```")[0].strip()
        result = yaml.safe_load(yaml_str)

        assert isinstance(result, dict)
        assert "analysis" in result
        assert "extracted_concept_info" in result
        assert isinstance(result["extracted_concept_info"], str)

        return result

    def post(self, shared, prep_res, exec_res):
        single_present_concept, chunk = prep_res

        shared["concept_dict"][single_present_concept] = exec_res[
            "extracted_concept_info"
        ]


class ConceptAppend(Node):
    def prep(self, shared):
        single_present_concept = self.params["single_present_concept"]
        chunk = self.params["chunk"]
        current_extracted_concept_info = shared["concept_dict"][single_present_concept]

        return single_present_concept, chunk, current_extracted_concept_info

    def exec(self, inputs):
        single_present_concept, chunk, current_extracted_concept_info = inputs
        prompt = f"""
Given chunk of notes:
```
{chunk}
```
Target concept name: {single_present_concept}
Current extracted concept info:
```
{current_extracted_concept_info}
```
Analyse the chunk to pick out which part of the chunk is relevant to the target concept (e.g. make possible learning outcome from target concept name then pick out content which satisfies the learning outcome).
You will then give distilled succinct statements, assertions, associations, concepts, analogies, and metaphors to be appended to the extracted concept info. 
The idea is to capture as much, conceptually, as possible but with as few words as possible. 
Write it in a way that makes sense to you, as the future audience will be another language model, not a human.
Ensure that no already present information is appended to the extracted concept info.
Output in yaml:
```yaml
analysis: detailed step-by-step analysis of chunk (ONE string)
extracted_concept_info: extracted info relevant to the target concept (ONE string)
```
        """
        resp = call_llm(prompt)
        yaml_str = resp.split("```yaml")[1].split("```")[0].strip()
        result = yaml.safe_load(yaml_str)

        assert isinstance(result, dict)
        assert "analysis" in result
        assert "extracted_concept_info" in result
        assert isinstance(result["extracted_concept_info"], str)

        return result

    def post(self, shared, prep_res, exec_res):
        single_present_concept, chunk, current_extracted_concept_info = prep_res

        shared["concept_dict"][single_present_concept] += (
            "\n" + exec_res["extracted_concept_info"]
        )


concept_update_type_switch_node = ConceptUpdateTypeSwitch()
concept_add_node = ConceptAdd(max_retries=10)
concept_append_node = ConceptAppend(max_retries=10)

concept_update_type_switch_node - "add" >> concept_add_node
concept_update_type_switch_node - "append" >> concept_append_node

concept_update = Flow(start=concept_update_type_switch_node)
batch_concept_update = BatchConceptUpdate(start=concept_update)


# *CONCEPT EXTRACTOR
class ConceptExtractor(BatchFlow):
    def prep(self, shared):
        notes = self.params["notes"]
        splitter = TextSplitter.from_tiktoken_model("gpt-3.5-turbo", CHUNK_MAX_TOKENS)
        chunks = [{"chunk": chunk} for chunk in splitter.chunks(notes)]

        print(chunks)

        return chunks


class GetConceptListFromChunk(Node):
    def prep(self, shared):
        concept_dict = shared["concept_dict"]
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
Concept names should be succinct yet accurately describe the content of the concept by being framed as a concise learning outcome.
If a concept overlaps with a previously extracted concept, use the EXACT SAME concept name to ensure that there are NO duplicate concepts.
If you observe no concepts in the chunk, you may generate an empty list for present_concepts.
Output in yaml:
```yaml
analysis: detailed step-by-step analysis of chunk (ONE string)
present_concepts: list of present concept names (LIST of strings)
```
        """
        resp = call_llm(prompt)
        yaml_str = resp.split("```yaml")[1].split("```")[0].strip()
        result = yaml.safe_load(yaml_str)

        assert isinstance(result, dict)
        assert "analysis" in result
        assert "present_concepts" in result
        assert isinstance(result["present_concepts"], list)
        assert all(isinstance(x, str) for x in result["present_concepts"])
        result["present_concepts"] = [x.strip() for x in result["present_concepts"]]

        return result

    def post(self, shared, prep_res, exec_res):
        shared["present_concepts"] = exec_res["present_concepts"]


get_concept_list_node = GetConceptListFromChunk(max_retries=10)

get_concept_list_node >> batch_concept_update

concept_extractor_chunk_flow = Flow(start=get_concept_list_node)
concept_extractor_batch_flow = ConceptExtractor(start=concept_extractor_chunk_flow)


def extract_concepts(notes: str):
    shared = {"concept_dict": {}}
    concept_extractor_batch_flow.set_params({"notes": notes})
    concept_extractor_batch_flow.run(shared)
    return shared["concept_dict"]


if __name__ == "__main__":
    print("TEST FOR concepts.py")

    assert input("DO YOU WISH TO PROCEED? (y/n) ").strip() == "y", "abort"

    print(
        extract_concepts(
            "The characteristics of the Dead Sea: Salt lake located on the border between Israel and Jordan. Its shoreline is the lowest point on the Earth's surface, averaging 396 m below sea level. It is 74 km long. It is seven times as salty (30% by volume) as the ocean. Its density keeps swimmers afloat. Only simple organisms can live in its saline waters."
        )
    )
