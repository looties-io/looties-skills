#!/usr/bin/env bash
# Télécharge les sources qui font foi pour le skill french-accounting et en extrait le texte.
#
# Usage : fetch-sources.sh [DOSSIER_CIBLE]        (par défaut : ~/.accounting-sources)
# Env :   PCG_URL   remplace l'URL du PCG quand l'ANC publie une nouvelle version consolidée
#
# Idempotent : un PDF déjà présent est conservé, sauf avec FORCE=1. Nécessite curl ; pdftotext
# (poppler) est facultatif mais fortement conseillé, car les agents cherchent dans le .txt.
set -euo pipefail

TARGET="${1:-$HOME/.accounting-sources}"
PCG_URL="${PCG_URL:-https://www.anc.gouv.fr/files/anc/files/1_Normes_fran%C3%A7aises/Plans%20comptables/2026/PCG--1er-janvier-2026.pdf}"
FORCE="${FORCE:-0}"

mkdir -p "$TARGET/pcg" "$TARGET/courses/aunege"

fetch() { # url destination
  local url="$1" dest="$2" tmp
  if [[ -s "$dest" && "$FORCE" != "1" ]]; then
    echo "conservé   $dest"
    return
  fi
  tmp="$(mktemp "$dest.XXXXXX")"
  curl -fsSL --retry 2 -A "french-accounting-skill/1.0" -o "$tmp" "$url"
  if ! head -c 5 "$tmp" | grep -q '%PDF-'; then
    rm -f "$tmp"
    echo "erreur : $url n'a pas renvoyé de PDF" >&2
    return 1
  fi
  mv "$tmp" "$dest"
  echo "téléchargé $dest"
}

extract() { # pdf
  local pdf="$1" txt="${1%.pdf}.txt"
  if ! command -v pdftotext >/dev/null 2>&1; then
    return
  fi
  if [[ ! -s "$txt" || "$pdf" -nt "$txt" ]]; then
    pdftotext -layout "$pdf" "$txt"
    echo "texte      $txt"
  fi
}

fetch "$PCG_URL" "$TARGET/pcg/PCG.pdf"
extract "$TARGET/pcg/PCG.pdf"

shopt -s nullglob
courses=("$TARGET"/courses/aunege/*.pdf)
for pdf in ${courses[@]+"${courses[@]}"}; do # expansion sûre en bash 3.2 d'un tableau peut-être vide
  extract "$pdf"
done

if ! command -v pdftotext >/dev/null 2>&1; then
  echo "attention : pdftotext introuvable ; installez poppler (brew install poppler / apt install poppler-utils) puis relancez" >&2
fi

cat <<EOF

Sources prêtes dans $TARGET
  PCG :            $TARGET/pcg/PCG.pdf (plan de comptes : grep -n "^Art. 1121-1" $TARGET/pcg/PCG.txt)
  Leçons AUNEGe :  ${#courses[@]} PDF dans $TARGET/courses/aunege/
EOF
if [[ ${#courses[@]} -eq 0 ]]; then
  cat <<EOF
                   facultatif : téléchargez-les depuis https://moodle.luniversitenumerique.fr/course/view.php?id=1034
                   (CC BY-NC-ND 4.0, usage personnel) dans ce dossier, puis relancez ce script.
EOF
fi
