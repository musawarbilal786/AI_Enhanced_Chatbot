# Included PDF dataset

This folder contains the exact three PDFs supplied for the project:

1. `prospectus_post_graduate.pdf` - International Postgraduate Prospectus 2025/26
2. `prospectus_under_graduate.pdf` - Undergraduate Prospectus 2025/26
3. `rules_and_regulations.pdf` - University rules and regulations

The RAG pipeline extracts text page-by-page and preserves filename, document title, category and page number for citations. Re-run `python scripts/build_index.py` whenever a PDF changes.
