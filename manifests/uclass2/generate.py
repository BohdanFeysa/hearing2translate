import os, sys, json, re
from pathlib import Path
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup


CONTEXT_URLS = {
    "monolog": "https://www.uclass.psychol.ucl.ac.uk/Release2/Monologue/AudioOnly/wav/",
    "reading": "https://www.uclass.psychol.ucl.ac.uk/Release2/Reading/AudioOnly/wav/",
    "conversation": "https://www.uclass.psychol.ucl.ac.uk/Release2/Conversation/AudioOnly/wav/",
}

DATASET_ID = "uclass2"
SRC = "en"
TGTS = ["es","it","fr","de","nl","pt"]
HEADERS = {"User-Agent": "Mozilla/5.0"}

def ensure_dir(p):
    Path(p).mkdir(parents=True, exist_ok=True)

def download_file(url, dest, referer=None):
    headers = dict(HEADERS)
    if referer: headers["Referer"] = referer
    with requests.get(url, stream=True, headers=headers) as r: #, timeout=30
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(262144):
                if chunk:
                    f.write(chunk)

def get_wav_links(page_url):
    """Return list of absolute wav URLs found on the page (hrefs ending with .wav)."""
    resp = requests.get(page_url, headers=HEADERS)#, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = urljoin(page_url, a["href"].strip())
        if urlparse(href).path.lower().endswith(".wav"):
            links.append(href)
    # preserve order and dedupe
    seen = set(); uniq = []
    for u in links:
        if u not in seen:
            seen.add(u); uniq.append(u)
    return uniq

def build_for_context(ctx, page_url, base_dir, overwrite=False):
    print(f"\n=== CONTEXT: {ctx} ===")
    wav_urls = get_wav_links(page_url)
    print("Found .wav files:", len(wav_urls))
    if not wav_urls:
        return 0

    stage_dir = Path(base_dir) / DATASET_ID / "audio" / SRC / ctx
    ensure_dir(stage_dir)
    manifests_dir = Path("manifests") / DATASET_ID / ctx
    ensure_dir(manifests_dir)

    id_width = max(1, len(str(len(wav_urls))))
    records = []
    for i, url in enumerate(wav_urls, start=1):
        sid = str(i).zfill(id_width)
        fname = Path(urlparse(url).path).name.split("?")[0] or (sid + ".wav")
        dst = stage_dir / fname
        if not dst.exists() or overwrite:
            try:
                download_file(url, dst, referer=page_url)
                print("Downloaded:", fname)
            except Exception as e:
                print("Download failed:", url, e, file=sys.stderr)
                continue
            pass
        else:
            print("Exists, skipped:", fname)

        pid = None
        m = re.search(r"(?:spk|speaker|child|kid|p|s)[-_]*?(\d{1,3})", fname, re.I)
        if m: pid = m.group(1)

        rec = {
            "dataset_id": DATASET_ID,
            "sample_id": sid,
            "src_audio": f"/{DATASET_ID}/audio/{SRC}/{ctx}/{fname}",
            "src_ref": None,
            "tgt_ref": None,
            "src_lang": SRC,
            "benchmark_metadata": {
                "native_acc": None,
                "spoken_acc": None,
                "participant_id": pid,
                "context": ctx
            }
        }
        records.append(rec)

    # write per-target manifests with tgt_lang immediately after src_lang
    for tgt in TGTS:
        outp = manifests_dir / f"{SRC}-{tgt}.jsonl"
        with outp.open("w", encoding="utf-8") as fo:
            for r in records:
                ordered = {
                    "dataset_id": r["dataset_id"],
                    "sample_id": r["sample_id"],
                    "src_audio": r["src_audio"],
                    "src_ref": r["src_ref"],
                    "tgt_ref": r["tgt_ref"],
                    "src_lang": r["src_lang"],
                    "tgt_lang": tgt,
                    "benchmark_metadata": r["benchmark_metadata"],
                }
                fo.write(json.dumps(ordered, ensure_ascii=False) + "\n")
        print("Wrote manifest:", outp)

    return len(records)

def main():
    base_dir = os.environ.get("H2T_DATADIR")
    if not base_dir:
        print("ERROR: set H2T_DATADIR environment variable before running (PowerShell: $env:H2T_DATADIR = 'C:\\path')", file=sys.stderr)
        sys.exit(1)

    total = 0
    for ctx in ("monolog","reading","conversation"):
        page = CONTEXT_URLS[ctx]
        cnt = build_for_context(ctx, page, base_dir, overwrite=False)
        total += cnt

    print(f"\nDone. Total staged records across contexts: {total}")

if __name__ == "__main__":
    main()
