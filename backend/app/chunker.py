def merge_blocks_to_chunks(blocks, chunk_size, overlap):
    chunks = []
    current_text = ""
    page_start = None
    page_end = None

    for block in blocks:
        text = block["text"]
        page = block["page_no"]

        if page_start is None:
            page_start = page

        page_end = page
        current_text += " " + text


        if len(current_text) >= chunk_size:
            chunks.append({
                "text": current_text.strip(),
                "page_start": page_start,
                "page_end": page_end
            })

            current_text = current_text[-overlap:]
            page_start = page
            page_end = page

    if current_text.strip():
        chunks.append({
            "text": current_text.strip(),
            "page_start": page_start,
            "page_end": page_end
        })

        return chunks