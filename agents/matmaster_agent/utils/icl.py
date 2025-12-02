import requests

# class ICLExampleSelector:
#     def __init__(
#         self,
#         examples,
#         model_name='/internfs/ycjin/MatMaster/models/moka-ai/m3e-base',
#         model_kwargs=None,
#         encode_kwargs=None,
#         k=2,
#     ):
#         if model_kwargs is None:
#             model_kwargs = {'device': 'cpu'}
#         if encode_kwargs is None:
#             encode_kwargs = {'normalize_embeddings': False}
#         self.embeddings = HuggingFaceEmbeddings(
#             model_name=model_name,
#             model_kwargs=model_kwargs,
#             encode_kwargs=encode_kwargs,
#         )
#         self.update_vector_store = FAISS.from_texts(
#             [e['update_input'] for e in examples], self.embeddings, metadatas=examples
#         )
#         self.ori_vector_store = FAISS.from_texts(
#             [e['input'] for e in examples], self.embeddings, metadatas=examples
#         )
#         self.ori_example_selector = SemanticSimilarityExampleSelector(
#             vectorstore=self.ori_vector_store, k=k
#         )
#         self.update_example_selector = SemanticSimilarityExampleSelector(
#             vectorstore=self.update_vector_store, k=k
#         )

#     def select_examples(self, query):
#         return self.ori_example_selector.select_examples({'input': query})

#     def select_update_examples(self, query):
#         return self.update_example_selector.select_examples({'input': query})

#     def scene_tags_from_examples(self, examples):
#         scene_prompts = ['\nSCENE_TAGS EXAMPLES:']
#         for example in examples:
#             if 'scene_tags' in example:
#                 scene_prompts.append(
#                     f"User Input: {example['update_input']}\nScenes: {', '.join(example['scene_tags'])}\n"
#                 )
#         return '\n'.join(scene_prompts)

#     def toolchain_from_examples(self, examples):
#         toolchain_prompts = ['\nToolchain EXAMPLES:']
#         for example in examples:
#             if 'toolchain' in example:
#                 toolchain_ = ' | '.join(
#                     [
#                         f"step{idx+1}: {step}"
#                         for idx, step in enumerate(example['toolchain'])
#                     ]
#                 )
#                 toolchain_prompts.append(
#                     f"Input: {example['update_input']}\nToolchain: {toolchain_}\n"
#                 )
#         return '\n'.join(toolchain_prompts)

#     def expand_input_examples(self, examples):
#         expanded_inputs = ['\nEXPAND EXAMPLES:']
#         for example in examples:
#             if 'update_input' in example:
#                 expanded_inputs.append(
#                     f"Original Input: {example['input']}\nExpanded Input: {example['update_input']}\n"
#                 )
#         return '\n'.join(expanded_inputs)


class ICLExampleSelector:
    def __init__(self):
        self.ICL_SERVICE_URL = '101.126.90.82:8001'

    def select_examples(self, query):
        return requests.post(
            url=f"http://{self.ICL_SERVICE_URL}/api/v1/icl/select-examples",
            json={'query': query},
        ).json()['data']

    def select_update_examples(self, query):
        return requests.post(
            url=f"http://{self.ICL_SERVICE_URL}/api/v1/icl/select-update-examples",
            json={'query': query},
        ).json()['data']

    def scene_tags_from_examples(self, examples):
        scene_prompts = ['\nSCENE_TAGS EXAMPLES:']
        for example in examples:
            if 'scene_tags' in example:
                scene_prompts.append(
                    f"User Input: {example['update_input']}\nScenes: {', '.join(example['scene_tags'])}\n"
                )
        return '\n'.join(scene_prompts)

    def toolchain_from_examples(self, examples):
        toolchain_prompts = ['\nToolchain EXAMPLES:']
        for example in examples:
            if 'toolchain' in example:
                toolchain_ = ' | '.join(
                    [
                        f"step{idx+1}: {step}"
                        for idx, step in enumerate(example['toolchain'])
                    ]
                )
                toolchain_prompts.append(
                    f"Input: {example['update_input']}\nToolchain: {toolchain_}\n"
                )
        return '\n'.join(toolchain_prompts)

    def expand_input_examples(self, examples):
        expanded_inputs = ['\nEXPAND EXAMPLES:']
        for example in examples:
            if 'update_input' in example:
                expanded_inputs.append(
                    f"Original Input: {example['input']}\nExpanded Input: {example['update_input']}\n"
                )
        return '\n'.join(expanded_inputs)


def icl_example_selector():
    return ICLExampleSelector()
