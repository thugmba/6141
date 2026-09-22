#!/usr/bin/env bash
set -euo pipefail

source_file="slides_src/session_01_02.html"
pdf_file="slides/session_01_02_lecture.pdf"
page_dir="assets/lecture_slides/session_1_2"
stage_dir=$(mktemp -d)
trap 'rm -rf "$stage_dir"' EXIT

weasyprint "$source_file" "$pdf_file"
pdftoppm -png -r 150 "$pdf_file" "$stage_dir/slide"

for page in 1 2 3 4 5 6 7 8; do
  mv "$stage_dir/slide-${page}.png" "$page_dir/slide_${page}.png"
done

cp "$page_dir/slide_1.png" "assets/session_01_02_slide.png"
pdfinfo "$pdf_file" | awk -F': *' '/^Pages:|^Page size:/ {print}'
