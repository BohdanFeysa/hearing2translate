#!/usr/bin/env python3
import argparse, json, os, re, sys, shutil
from pathlib import Path


CTX_KEYWORDS = {
    "reading": ["reading", "read", "passage"],
    "monolog": ["monolog", "mono"],
    "conversation": ["conversation", "dialog", "dialogue", "conv"]
}

def guess_context_from_path(p: Path) -> str:
    s = str(p).lower()
    for ctx, kws in CTX_KEYWORDS.items():
        if any(k in s for k in kws):
            return ctx
    return "unknown"

def guess_participant_id(text: str) -> str | None:
    m = re.search(r"(?:spk|speaker|child|kid|p|s)\s*[-_]*\s*(\d{1,3})", text, re.I)
    return m.group(1) if m else None


def main():
    ap = argparse.ArgumentParser(description="Stage WAVs and build JSONL manifest")
    ap.add_argument("--audio_dir", required=True,
                    help="Source directory containing downloaded .wav files (searched recursively)")
    ap.add_argument("--dataset_id", default="uclass2")
    ap.add_argument("--src_lang", default="en")
    ap.add_argument("--tgt_lang", default="null")
    ap.add_argument("--output", default=None,
                    help="Output JSONL path (default: manifests/<dataset_id>/<src>.jsonl)")
    ap.add_argument("--stage_dir", default=None,
                    help="Folder to copy wavs into (default: DATA/<dataset_id>/audio/<src_lang>/)")
    ap.add_argument("--prefix", default=None,
                    help="Prefix placed in 'src_audio' (default: /<dataset_id>/audio/<src_lang>/)")
    ap.add_argument("--id_width", type=int, default=6, help="Zero-pad width for sample_id")
    ap.add_argument("--keep_name", action="store_true",
                    help="Keep original filename instead of <sample_id>.wav")
    ap.add_argument("--overwrite", action="store_true",
                    help="Overwrite staged audio if it already exists")
    args = ap.parse_args()


    src_root = Path(args.audio_dir).resolve()
    if not src_root.exists():
        print(f"ERROR: audio_dir not found: {src_root}", file=sys.stderr)
        sys.exit(1)

    stage_dir = (Path("DATA") / args.dataset_id / "audio" / args.src_lang) if args.stage_dir is None else Path(args.stage_dir)
    stage_dir.mkdir(parents=True, exist_ok=True)

    out_path = (Path("manifests") / args.dataset_id / f"{args.src_lang}.jsonl") \
               if args.output is None else Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rel_prefix = args.prefix or f"/{args.dataset_id}/audio/{args.src_lang}/"

    # Collect and sort .wav files for stable IDs
    wavs = sorted(src_root.rglob("*.wav"))
    if not wavs:
        print(f"WARNING: no .wav files found under {src_root}", file=sys.stderr)

    n_written = 0
    with out_path.open("w", encoding="utf-8") as fout:
        for i, src_wav in enumerate(wavs, start=1):
            sample_id = str(i).zfill(args.id_width)

            # Choose staged filename
            staged_name = src_wav.name if args.keep_name else f"{sample_id}.wav"
            dst_wav = stage_dir / staged_name

            # Copy if needed
            if dst_wav.exists() and not args.overwrite:
                pass
            else:
                dst_wav.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_wav, dst_wav)

            # Infer metadata
            context = guess_context_from_path(src_wav)
            pid = (guess_participant_id(src_wav.name)
                   or guess_participant_id(str(src_wav.parent))
                   or None)

            record = {
                "dataset_id": "UClass2",
                "sample_id": sample_id,
                "src_audio": f"{rel_prefix}{dst_wav.name}",
                "src_ref": None,
                "tgt_ref": None,
                "src_lang": args.src_lang,
                "tgt_lang": args.tgt_lang,
                "benchmark_metadata": {
                    "native_acc": None,
                    "spoken_acc": None,
                    "participant_id": pid,
                    "context": context
                }
            }
            fout.write(json.dumps(record, ensure_ascii=False) + "\n")
            n_written += 1

    print(f"Staged audio dir : {stage_dir.resolve()}")
    print(f"Manifest written : {out_path.resolve()}  (records: {n_written})")

if __name__ == "__main__":
    main()
