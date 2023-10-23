# %%
def process_document(document):
    sections = []       # (level, section_text)
    paragraph_list = []
    title_passage = document.passages[0]
    # print(title_passage)
    title = title_passage.text
    infons = title_passage.infons
    # print(dict(infons))
    journal_name = (infons["journal-title"].lower() if "journal-title" in infons else "") + " " + (infons["journal"] if "journal" in infons else "")
    if not any([name in journal_name for name in ["nature", "science", "cell", "nat", "sci"]]):
        return None    # skip this paper
    # print(title_passage.annotations)
    for p in document.passages[1:]:
        # print(p)
        try: 
            if "section_type" not in p.infons or "type" not in p.infons:
                continue
            stype = p.infons['section_type']
            ptype = p.infons['type']
            text = p.text.strip()
            if stype == "TITLE":
                return None    # skip this paper
            if stype in ["SUPPL", "ABBR", "AUTH_CONT", "ACK_FUND", "COMP_INT", "REF", "KEYWORD", "APPENDIX", "REVIEW_INFO"] + ["FIG", "TABLE"]:
                continue
            assert stype in ["ABSTRACT", "INTRO", "RESULTS", "DISCUSS", "CONCL", "METHODS", "CASE"], f"Unknown section type: {stype}, {ptype}, {text}"
            if ptype.startswith('title'):
                # print(stype, ptype, text)
                level_str = ptype.removeprefix('title_')
                if not level_str.isdigit():
                    continue
                level = int(level_str) if ptype != "title" else 1       # 1-6
                # pop the sections stack until the level is lower than the current level
                while sections and sections[-1][0] >= level:
                    sections.pop()
                sections.append((level, text))
            elif ptype == 'abstract':
                paragraph_list.append({"title": title, "section": "", "content": text, "section_type": stype})
            elif ptype == 'paragraph':
                paragraph_list.append({"title": title, "section": " / ".join([s for l, s in sections]), "content": text, "section_type": stype})
            elif ptype in ["footnote", "abstract_title_1", "footnote_title_2", "footnote_title", "footnote_title_caption"]:
                continue
            else:
                print(f"[WARNING] Unknown passage stype: {stype} ptype: {ptype}, text: {text}")
        except Exception as e:
            print(f"[ERROR] {e}. Passage: {p}")
            raise e
    return {"title": title, "infons": dict(infons), "passages": paragraph_list}

# %%
from bioc import biocxml
import glob
import json
import numpy as np
import multiprocessing as mp
from pathlib import Path
from tqdm import tqdm

data_glob = "../../../data/pubtator/output/BioCXML/*.BioC.XML"
path_list = glob.glob(data_glob)
path_list.sort(key=lambda x: int(Path(x).stem.split(".")[0]))
print(path_list[:10])

# collection = biocxml.load(path_list[0])
# doc = process_document(collection.documents[0])
# exit(0)

def work_main(path_list, output_path):
    document_list = []
    for file_path in tqdm(path_list):
        try:
            collection = biocxml.load(file_path)
            for document in collection.documents:
                doc = process_document(document)
                if doc is not None:
                    document_list.append(doc)
        except Exception as e:
            print(f"[ERROR] {e}. File: {file_path}")
            # raise e
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        for doc in document_list:
            f.write(json.dumps(doc) + "\n")

workers = 24
path_batch_list = np.array_split(path_list, workers)
print("path_batch_list:", [len(p) for p in path_batch_list])
output_path_list = [f"outputs/doc_{i}.jsonl" for i in range(workers)]

with mp.Pool(workers) as pool:
    pool.starmap(work_main, zip(path_batch_list, output_path_list))

# %%



