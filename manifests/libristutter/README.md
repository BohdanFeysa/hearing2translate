# Libristutter

## Overview

FLEURS (Few-shot Learning Evaluation of Universal Representations of Speech), is a benchmark dataset for speech research. The dataset is an n-way parallel speech dataset that includes 102 languages and is based on the machine translation FLoRes-101 benchmark. It contains approximately 12 hours of speech per language. The FLEURS benchmark enables the evaluation of various speech tasks, including Automatic Speech Recognition (ASR), Speech Language Identification (Speech LangID), Translation, and Retrieval.

```bibtex
@ARTICLE{9528931,
  author={Kourkounakis, Tedd and Hajavi, Amirhossein and Etemad, Ali},
  journal={IEEE/ACM Transactions on Audio, Speech, and Language Processing}, 
  title={FluentNet: End-to-End Detection of Stuttered Speech Disfluencies With Deep Learning}, 
  year={2021},
  volume={29},
  number={},
  pages={2986-2999},
  keywords={Speech processing;Deep learning;Training;Benchmark testing;Tools;Speaker recognition;Residual neural networks;Attention;disfluency;deep learning;BLSTM;speech;stutter;squeeze-and-excitation},
  doi={10.1109/TASLP.2021.3110146}}
```

## Instructions

Define the path where **Libristutter** will be stored:

```bash
export H2T_DATADIR=""
```

Run the Python script to generate the processed data:

```bash
python generate.py
```

## Expected Output

After running the steps above, your directory layout will be:

```
${H2T_DATADIR}/
└─ libristutter/
   └─ audio/
     º│  ├─6000-55211-0004.flac
      │  ├─ 2518-154825-0004.flac
      │  └─ ...
      └─ de/
      │  ├─ 4018-107312-0003.flac
      │  ├─ 625-132118-0031.flac
      │  └─ ...
      └─ ...
```

If your generate.py script writes manifests, you should get a  JSONL file  under your chosen output path (e.g., ./manifests/Libristutter/). A jsonl entry looks like:


```json
{
  "dataset_id": "fleurs",
  "sample_id": "<string>",
  "src_audio": "/fleurs/audio/<src_lang>/<audio file>",
  "src_ref": "<source raw_transcription>",
  "tgt_ref": "<target raw_transcription>",
  "src_lang": "en",
  "tgt_lang": "en",
  "benchmark_metadata": {"has_stutter":"True|False", "stutter_pos":[]}
}
```

## License

All datasets are licensed under the Creative Commons Non Commercial license (CC BY-NC 4.0).
