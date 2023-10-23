# def _string_to_dict(to_convert):
#     r"""Converts a string with equal signs to dictionary. E.g.
#     >>> _string_to_dict(" name=user university=stanford")
#     {'name': 'user', 'university': 'stanford'}
#     """
#     return {s.split("=", 1)[0]: s.split("=", 1)[1] for s in to_convert.split(" ") if len(s) > 0}


# def prompt_to_chatml(prompt: str, start_token: str = "<|im_start|>", end_token: str = "<|im_end|>"):
#     prompt = prompt.strip()
#     assert prompt.startswith(start_token)
#     assert prompt.endswith(end_token)
#     message = []
#     for p in prompt.split("<|im_start|>")[1:]:
#         newline_splitted = p.split("\n", 1)
#         role = newline_splitted[0].strip()
#         content = newline_splitted[1].split(end_token, 1)[0].strip()
#         if role.startswith("system") and role != "system":
#             other_params = _string_to_dict(role.split("system", 1)[-1])
#             role = "system"
#         else:
#             other_params = dict()
#         message.append(dict(content=content, role=role, **other_params))
#     return message

def load_prompt(prompt_path):
    from string import Template
    with open(prompt_path, "r") as f:
        prompt = f.read()
    return Template(prompt)

def load_jsonl(jsonl_path):
    import json
    with open(jsonl_path, "r") as f:
        return [json.loads(line) for line in f.readlines()]

def save_jsonl(data, jsonl_path):
    import json, os
    os.makedirs(os.path.dirname(jsonl_path), exist_ok=True)
    with open(jsonl_path, "w") as f:
        for d in data:
            f.write(json.dumps(d) + "\n")