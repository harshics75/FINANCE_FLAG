from app.rag.chunker import chunk_table, chunk_text


def test_chunk_text_splits_long_content():
    text = "\n\n".join(f"Paragraph {i} " + "x" * 300 for i in range(10))
    chunks = chunk_text(text, page_number=1, max_chars=800)
    assert len(chunks) > 1
    assert all(c.page_number == 1 for c in chunks)


def test_chunk_table_marks_type():
    c = chunk_table("| a | b |", page_number=2, sheet="P&L")
    assert c.content_type == "table"
    assert c.meta["sheet"] == "P&L"
