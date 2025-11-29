"""A script to generate the CoVoST2 jsonl files and save audios"""
import argparse
import csv
import json
import os
import time

from datasets import concatenate_datasets, load_dataset
import pandas as pd
import soundfile as sf

# As we have no target references anyways, we translate to all of them
tgt_langs_covost = ["uk"]

tgt_langs_noRef = ['en']

src_langs = [
    'uk'
]

base_dir = os.environ.get("H2T_DATADIR")

def load_written_ids(json_out):
    """Read existing JSONL file and collect sample_ids to avoid duplicates"""
    if not os.path.exists(json_out):
        return set()
    written = set()
    with open(json_out, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                rec = json.loads(line)
                written.add(rec["sample_id"])
            except json.JSONDecodeError:
                continue  # Skip malformed lines
    return written

def process_in_batches(dataset, batch_size=1000):
    """Process dataset in batches"""
    batch = []
    for _, row in enumerate(dataset):
        batch.append(row)
        if len(batch) >= batch_size:
            yield batch
            batch = []
            # Small delay to prevent overwhelming the connection
            time.sleep(0.1)
    # Process remaining items
    if batch:
        yield batch


def build_jsonl(clip_dir):
    """Build the jsonl files containing datapoints for each src-tgt pair in CoVoST2"""

    for src in src_langs:
        audio_output_dir = os.path.join(base_dir, 'covost2', "audio", src)
        os.makedirs(audio_output_dir, exist_ok=True)

        if src == 'en':
            for tgt in tgt_langs_covost:
                json_out = f"manifests/covost2/{src}-{tgt}.jsonl"
                process_language_pair(src, tgt, json_out, audio_output_dir, clip_dir, ref = True)
            for tgt in tgt_langs_noRef:
                # We run inference anyways even without target reference
                json_out = f"manifests/covost2/{src}-{tgt}.jsonl"
                process_language_pair(src, tgt, json_out, audio_output_dir, clip_dir, ref = False)
        else:
            tgt = 'en'
            json_out = f"manifests/covost2/{src}-{tgt}.jsonl"
            process_language_pair(src, tgt, json_out, audio_output_dir, clip_dir)


def process_language_pair(src, tgt, json_out, audio_output_dir, clip_dir, ref=True):
    """Process a language pair when NO translation TSV is available.
    src_ref = sentence, tgt_ref = None.
    """

    # Load all local CommonVoice metadata for the source language
    metadata = pd.concat([
        pd.read_csv(
            f'{clip_dir}/{src}/{split}.tsv',
            encoding='utf-8',
            header=0,
            sep='\t',
            escapechar='\\',
            quoting=csv.QUOTE_NONE,
            na_filter=False
        )
        for split in ['train', 'dev', 'test', 'invalidated', 'other', 'validated']
    ])

    # Extract utt_id
    metadata['utt_id'] = metadata['path'].apply(
        lambda x: x.replace('.mp3', '').split('_')[-1]
    )
    metadata['utt_id'] = metadata['utt_id'].astype(str)

    # Sample 1200 items
    metadata = metadata.sample(n=min(2500, len(metadata)), random_state=42)
    metadata = metadata.reset_index(drop=True)

    print(f"Processing {src}-{tgt}: randomly selected {len(metadata)} samples")

    # Load already-written IDs
    written_ids = load_written_ids(json_out)
    processed_in_session = 0

    with open(json_out, 'a', encoding='utf-8') as f:
        for _, row in metadata.iterrows():
            utt_id = row["utt_id"]

            if utt_id in written_ids:
                continue

            # Load local MP3 audio
            audio_file = f'{clip_dir}/{src}/clips/common_voice_{src}_{utt_id}.mp3'
            audio, sr = sf.read(audio_file)

            # Save converted WAV
            audio_filename = f"{utt_id}.wav"
            audio_filepath = os.path.join(audio_output_dir, audio_filename)
            relative_audio_path = f"/covost2/audio/{src}/{audio_filename}"

            if not os.path.exists(audio_filepath):
                sf.write(audio_filepath, audio, sr)

            # Build the final record
            record = {
                "dataset_id": "covost2",
                "sample_id": utt_id,
                "src_audio": relative_audio_path,
                "src_ref": row["sentence"],   # we DO have source text
                "tgt_ref": None,              # we do NOT have translations
                "src_lang": src,
                "tgt_lang": tgt,
                "benchmark_metadata": {
                    "context": "short"
                }
            }

            f.write(json.dumps(record, ensure_ascii=False) + '\n')
            f.flush()

            written_ids.add(utt_id)
            processed_in_session += 1

            if processed_in_session % 100 == 0:
                print(f"Processed {processed_in_session} samples for {src}-{tgt}")

    print(f"Successfully completed {src}-{tgt} with {processed_in_session} samples.")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--clip_dir",type=str,
                        help="dir containing the de, en, and es CommonVoice 4.0 data. Should contain 'en/clips','es/clips','de/clips'")
    args = parser.parse_args()
    build_jsonl(args.clip_dir)
