# WMT24 and WMT25

The WMT24 and WMT25 are primarily text-only datasets but include a `speech` domain, which is based on publicly available YouTube video. For these, human translation was created.

```bibtex
@inproceedings{kocmi-etal-2024-findings,
    title = "Findings of the {WMT}24 General Machine Translation Shared Task: The {LLM} Era Is Here but {MT} Is Not Solved Yet",
    author = "Kocmi, Tom  and
      Avramidis, Eleftherios  and
      Bawden, Rachel  and
      Bojar, Ond{\v{r}}ej  and
      Dvorkovich, Anton  and
      Federmann, Christian  and
      Fishel, Mark  and
      Freitag, Markus  and
      Gowda, Thamme  and
      Grundkiewicz, Roman  and
      Haddow, Barry  and
      Karpinska, Marzena  and
      Koehn, Philipp  and
      Marie, Benjamin  and
      Monz, Christof  and
      Murray, Kenton  and
      Nagata, Masaaki  and
      Popel, Martin  and
      Popovi{\'c}, Maja  and
      Shmatova, Mariya  and
      Steingr{\'i}msson, Steinth{\'o}r  and
      Zouhar, Vil{\'e}m",
    booktitle = "Proceedings of the Ninth Conference on Machine Translation",
    month = nov,
    year = "2024",
    address = "Miami, Florida, USA",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2024.wmt-1.1/",
    doi = "10.18653/v1/2024.wmt-1.1",
    pages = "1--46",
}
```

and

```bibtex
TODO
```


## Instructions


The script `generate.py` will build the jsonl files for the following language pairs (the dataset has more languages but this is the intersection with hearing2translate):
- en-es
- en-de
- en-zh

```bash
H2T_DATADIR="manifests/wmt" python3 manifests/wmt/generate.py
```

For the WMT25 part, the videos need to be converted from MP4 to wav, which necessitates local ffmpeg installation and `pip install ffmpeg-python`.
After running the steps above, your directory layout will be:

```
${H2T_DATADIR}/
└─ audio/
    ├─ 392RoIzR2Fs_001.wav
    ├─ Fhach-AU5Ko_020.wav
    └─ ...
├─ en-es.jsonl
├─ en-de.jsonl
└─ en-zh.jsonl
```

If your generate.py script writes manifests, you should get JSONL files (one per language pair) under your chosen output path (e.g., `manifests/wmt/wmt24` and `manifests/wmt/wmt25`). The JSONL entry looks like:

```json
{
    "dataset_id": "wmt24",
    "sample_id": 5,
    "src_audio": "manifests/wmt/wmt24/audio/-_31PoDRu28_001.wav",
    "src_ref": "Now I need to quickly mention the reactor's name, as it was considered a zero power installation. You see, a zero power nuclear reactor is capable of sustaining a stable fission chain reaction, with no significant increase or decline in the reaction rate. This type of installation is essential to gain practical experience of reactor operation, but can still be deadly if the delicate balance isn't maintained.",
    "tgt_ref": "Ahora tengo que mencionar rápidamente el nombre del reactor, ya que era considerado una instalación de potencia cero. Bien, un reactor nuclear de potencia cero es capaz de mantener una reacción de fisión en cadena estable, sin aumento ni disminución significativa de la velocidad de reacción. Este tipo de instalación es esencial para adquirir experiencia práctica en el funcionamiento de los reactores, pero puede ser mortal si no se mantiene el delicado equilibrio.",
    "src_lang": "en",
    "ref_lang": "es",
    "benchmark_metadata": {"context": null, "doc_id": "test-en-speech_-_31PoDRu28_001", "dataset_type": "video"}
}
```

## Licence

The audios are sourced from YouTube videos with CC-BY license.