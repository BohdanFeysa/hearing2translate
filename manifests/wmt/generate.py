import json
import xml.etree.ElementTree as ElementTree
import requests
import os
import tempfile
import io
import zipfile
import shutil
import tarfile
import collections
# pip install ffmpeg-python
import ffmpeg

dir_root = os.environ.get("H2T_DATADIR", ".")
dir_tmp = tempfile.mkdtemp()
os.makedirs(f"{dir_root}/wmt/audio/", exist_ok=True)

# WMT24
print("Downloading WMT24 audio, this might take a while...")
zipfile.ZipFile(
    io.BytesIO(requests.get(
        "https://data.statmt.org/wmt24/general-mt/wmt24_GeneralMT-audio.zip").content
    )).extractall(dir_tmp)

dataset_out = collections.defaultdict(list)
print("Processing WMT24...")
for langs in ["en-de", "en-es", "en-zh", "en-cs", "en-hi", "en-is", "en-ja", "en-ru", "en-uk"]:
    lang1, lang2 = langs.split("-")
    url = f"https://raw.githubusercontent.com/wmt-conference/wmt24-news-systems/refs/heads/main/xml/wmttest2024.{langs}.all.xml"
    response = requests.get(url)
    tree = ElementTree.fromstring(response.content)[0]
    for node in [node for node in tree if node.attrib["domain"] == "speech"]:
        doc_id = node.attrib["id"]
        text_src = [
            x[0][0].text
            for x in node
            if x.attrib.get("type") == "clean_source" and x.tag == "supplemental"
        ][0]
        # we might have two references but one is enough
        text_ref = {
            x.attrib["translator"]: x[0][0].text for x in node
            if x.attrib.get("lang") == lang2 and x.tag == "ref"
        }
        # if it's just one reference, make it a string
        if len(text_ref) == 1:
            text_ref = list(text_ref.values())[0]

        # copy, even override
        fname_new = shutil.copyfile(
            f"{dir_tmp}/WMT24_GeneralMT_audio/test-en-speech-audio/{doc_id.removeprefix('test-en-speech_')}.wav",
            f"{dir_root}/wmt/audio/{doc_id.removeprefix('test-en-speech_')}.wav"
        )

        dataset_out[langs].append({
            "dataset_id": "wmt24",
            "sample_id": len(dataset_out[langs]),
            "src_audio": "/" + fname_new.removeprefix(dir_root+"/"),
            "src_ref": text_src,
            "tgt_ref": text_ref,
            "src_lang": lang1,
            "ref_lang": lang2,
            "benchmark_metadata": {"doc_id": doc_id, "dataset_type": "longform"},
        })


# WMT25
print("Downloading WMT25 data...")
print("WARNING: using temporary location which will change in October 2025")

with open(f"{dir_tmp}/TMP_Sep08-wmt25-genmt-humeval.jsonl.gz", 'wb') as f:
    f.write(requests.get("https://vilda.net/t/wmt25/TMP_Sep08-wmt25-genmt-humeval.jsonl.gz").content)

with tarfile.open(f"{dir_tmp}/TMP_Sep08-wmt25-genmt-humeval.jsonl.gz") as tar:
    tar.extractall(dir_tmp)

with open(f"{dir_tmp}/data/TMP_Sep08-wmt25-genmt-humeval.jsonl", "r") as f:
    data = [json.loads(line) for line in f]
    data = [line for line in data if "_#_speech_#_" in line["doc_id"]]

print("Processing WMT25...")
for langs in ["en-zh_CN", "en-uk_UA", "en-ru_RU", "en-ko_KO", "en-ja_JP", "en-is_IS", "en-et_EE", "en-cs_CZ", "en-bho_IN", "en-ar_EG"]:
    data_local = [x for x in data if x["doc_id"].startswith(langs + "_#_")]
    langs = langs.split("_")[0]
    lang1, lang2 = langs.split("-")

    for line in data_local:
        wav_file = f"{dir_root}/wmt/audio/{line['doc_id'].split('_#_')[2]}.wav"

        # convert MP4 to WAV using ffmpeg-python
        if not os.path.exists(wav_file):
            mp4_file = f'{dir_tmp}/tmp_video.mp4'
            r = requests.get(f"https://vilda.net/t/wmt25/assets/en/speech/{line['doc_id'].split('_#_')[2]}.mp4")
            with open(mp4_file, 'wb') as f:
                f.write(r.content)
            ffmpeg.input(mp4_file).output(wav_file, vn=None).run()

        dataset_out[langs].append({
            "dataset_id": "wmt25",
            "sample_id": len(dataset_out[langs]),
            "src_audio": "/" + wav_file.removeprefix(dir_root+"/"),
            "src_ref": line["src_text"],
            "tgt_ref": line["tgt_text"]["refA"],
            "src_lang": lang1,
            "ref_lang": lang2,
            "benchmark_metadata": {"doc_id": line["doc_id"], "dataset_type": "longform"},
        })


for langs, dataset in dataset_out.items():
    with open(f"manifests/wmt/{langs}.jsonl", "w") as f:
        f.write("\n".join(
            json.dumps(record, ensure_ascii=False)
            for record in dataset
        ) + "\n")