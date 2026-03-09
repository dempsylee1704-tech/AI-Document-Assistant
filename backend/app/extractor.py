def extract_text_blocks(doc_data):
    blocks = []
    for block in doc_data["texts"]:
        text = block.get("text", "")
        label = block.get("label")
        prov = block.get("prov")
        if prov:
            page_no = prov[0].get("page_no")
        else:
            page_no = None

        if not text.strip():
            continue

        blocks.append({
            "text": text,
            "label": label,
            "page_no": page_no
        })

    return  blocks