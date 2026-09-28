#!/usr/bin/env python3
"""Transcribe a time window of a media file *alone* to verify a cut boundary "by ear".

Uses whisper.cpp (`whisper-cli`) with ggml-large-v3-turbo; results cached in a JSON file.
  hear.py FILE START END [--lang fr] [--model PATH] [--cache hear.cache.json]
Lib: from hear import hear   -> list of normalised tokens
"""
import argparse, json, os, re, subprocess, tempfile, unicodedata

MODEL = os.path.expanduser('~/.cache/whisper/ggml-large-v3-turbo.bin')
_cache, _cache_path = {}, None


def norm(w):
    w = unicodedata.normalize('NFKD', w.lower())
    return re.sub(r"[^a-z0-9']", '', ''.join(c for c in w if not unicodedata.combining(c)))


def hear(path, a, b, lang='fr', model=MODEL, cache_path='hear.cache.json'):
    global _cache, _cache_path
    if cache_path != _cache_path:
        _cache = json.load(open(cache_path)) if os.path.exists(cache_path) else {}
        _cache_path = cache_path
    k = f'{os.path.abspath(path)}|{a:.2f}|{b:.2f}|{lang}'
    if k not in _cache:
        with tempfile.TemporaryDirectory() as tmp:
            wav = f'{tmp}/c.wav'
            # 300 ms lead-in + padding: whisper drops words glued to the file edges
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{a:.3f}', '-to', f'{b:.3f}', '-i', path,
                            '-af', 'adelay=300|300,apad=pad_dur=0.5', '-ac', '1', '-ar', '16000', wav], check=True)
            out = subprocess.run(['whisper-cli', '-m', model, '-l', lang, '-t', '8', '-nt', '-np', wav],
                                 capture_output=True, text=True).stdout
        _cache[k] = [t for t in (norm(x) for x in ' '.join(out.split()).split()) if t]
        json.dump(_cache, open(cache_path, 'w'), ensure_ascii=False)
    return _cache[k]


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('file'); ap.add_argument('start', type=float); ap.add_argument('end', type=float)
    ap.add_argument('--lang', default='fr'); ap.add_argument('--model', default=MODEL)
    ap.add_argument('--cache', default='hear.cache.json')
    a = ap.parse_args()
    print(' '.join(hear(a.file, a.start, a.end, a.lang, a.model, a.cache)))
