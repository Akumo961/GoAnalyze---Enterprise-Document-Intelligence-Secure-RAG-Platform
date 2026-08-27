# Phase 2 — Production RAG, Extraction and AI Security

## Scope

Phase 2 upgrades the deterministic Phase 1 evidence workflow with a provider-neutral RAG engine, safe document extraction/OCR integration, AI security controls and a versioned evaluation benchmark.

## Implemented

- deterministic lexical retrieval with ranked chunks
- fail-closed behavior when evidence is insufficient
- document prompt-injection detection
- question prompt-injection detection
- explicit evidence-only system instruction for LLM generation
- pluggable OpenAI-compatible HTTPS model provider
- zero-temperature generation for repeatability
- provider/model metadata on responses
- PDF text extraction through `pypdf` when installed
- DOCX extraction through `python-docx` when installed
- strict content-type and 50 MiB upload boundary
- SHA-256 content identity
- isolated optional Tesseract OCR integration with timeout and generated filenames
- citation coverage evaluation
- cross-tenant retrieval guard
- versioned offline benchmark
- automated Phase 2 CI

## Production configuration

Set:

```text
GOANALYZE_AI_PROVIDER=openai-compatible
GOANALYZE_AI_ENDPOINT=https://<approved-endpoint>
GOANALYZE_AI_API_KEY=<secret-from-secret-manager>
GOANALYZE_AI_MODEL=<approved-model-id>
```

`retrieval-only` is the default and intentionally does not call an LLM. This allows secure evaluation without credentials and prevents accidental external data transmission.

## AI security boundary

Uploaded document text is untrusted data. It cannot override system or developer instructions. Retrieval drops chunks containing known instruction-injection signatures. This is a defense-in-depth control, not proof that all prompt injection is solved.

LLM output remains decision support. The platform must not make legally binding environmental decisions. Regulatory claims require customer-approved authoritative sources; Phase 2 does not add Québec legal content.

## OCR boundary

PDF/DOCX text extraction is implemented. OCR is an integration point using Tesseract when explicitly installed and invoked. OCR accuracy on arbitrary government scans is **NOT VERIFIED IN CURRENT ENVIRONMENT**.

## Evaluation

Run:

```bash
pytest tests/test_phase2_rag_security.py tests/test_phase2_document_extract.py -q
python scripts/run_phase2_eval.py
```

The benchmark is synthetic and measures deterministic retrieval/security behavior. It does not establish production LLM quality. A customer deployment must add a representative, governed evaluation set and evaluate retrieval recall, citation precision, groundedness, refusal behavior, latency, cost and human override rate.

## Not claimed

Phase 2 does not claim:

- Québec legal compliance
- production government deployment
- independent penetration testing
- universal prompt-injection prevention
- OCR accuracy certification
- LLM benchmark performance
- production-scale latency/capacity
- authoritative regulatory knowledge
