from app.rag import rag_pipeline


def test_retrieve_returns_results():
  question = "Who is telling the story at the beginning of the book?"
  docs, metas = rag_pipeline.retrieve(question, top_k=2)

  assert len(docs) > 0
  assert len(metas) > 0
  sources = {m["source"] for m in metas}
  assert any(s.endswith(".pdf") or s.endswith(".txt") or s.endswith(".md") for s in sources)
