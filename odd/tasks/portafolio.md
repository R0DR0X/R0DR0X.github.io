# Feature: personal portfolio (web + PDF)

Personal-brand portfolio covering everything the owner knows and does across all projects.
One bilingual (ES/EN) content source renders both a single-page website and a PDF. Client and company names are anonymized.

## Specs

- S1. Original request, verbatim: "puedes hacerme un portafolio de todo lo que se y todo lo que hago en todos los proyectos". Coverage must come from evidence in the owner's projects (local directories under `/home/rodrigo` and Engram memory), not invented claims.
- S2. Format, user's answer verbatim: "Ambos" — "Web + PDF generados desde el mismo contenido". Both deliverables render from one content source.
- S3. Audience, user's answer verbatim: "General / marca personal" — "Mezcla de todo, sin un público específico".
- S4. Language, user's answer verbatim: "Bilingüe" — "Español e inglés". Every visible string exists in both languages.
- S5. Privacy, user's answer verbatim: "Anonimizarlos" — "Ej.: 'empresa de exportación peruana' en vez del nombre". No real client or company name appears in the web or the PDF; secrets, hosts, credentials, IPs and personal data of third parties never appear either.

## Tasks

- T1 [S1, S5] Research inventory of skills and projects (4 parallel `gentle-ai-explore`) → `research/inventory-all.md` (private, gitignored). DONE. Commit: — (private output)
- T2 [S1, S3, S4, S5] Bilingual anonymized content source `content/portfolio.json` + anonymization map in `research/` → inline. DONE (0 denylist hits, every string ES+EN). Commit: 7502843
- T3 [S2, S3] Design directions under `design/portafolio/` (gentle-design, 3 artboards); owner picks one → 01 inline, 02/03 two `gentle-ai-worker` (context backstop). Artboards done; waiting for the owner's pick. Commit: 450c633
- T4 [S2, S3, S4, S5] Hybrid design per L8: `tools/build.py` renders `site/index.html` (es) and `site/en/index.html` (en) from the content source, language switch as links + hreflang → one `gentle-ai-worker` (context backstop), together with T5. Commit: pending
- T5 [S2, S4] Per language: 2-page A4 ATS-friendly CV PDF and a multi-page portfolio PDF, both from the same content source, printed with headless Chrome → same worker as T4 (relaunched per L10). Commit: pending
- T6 [S4, S5] Checks: anonymization denylist scan, both languages complete, no external URLs, a11y basics → inline. Commit: pending

## Log

- L1. User request (2026-11-10), verbatim: "puedes hacerme un portafolio de todo lo que se y todo lo que hago en todos los proyectos"
- L2. Questionnaire answers: Formato "Ambos"; Público "General / marca personal"; Idioma "Bilingüe"; Privacidad "Anonimizarlos".
- L4. T1 done: 4 explorers returned `research/inventory-all.md` (626 lines, read in full). Identity from the owner's own CV `~/Documentos/CV_Ivan_Rodrigo_Pianto.html`: name, headline, location, email, GitHub, roles and years. CV claims without evidence (e.g. commit counts, Prisma) are not used; numbers come only from inventory evidence.
- L5. Anonymization decision under S5: the owner's own brands (company, e-commerce brand, open-source app, game name) are anonymized too, because they are real company/product names; the owner can opt them back in later. Public bodies and datasets (SUNAT, SEACE, ECMWF, OSM) and technology vendors in stacks stay named. Private denylist: `research/denylist.txt` (word-boundary, case-insensitive).
- L6. Design `design/portafolio/` (canvas via symlink `~/design` → `~/portafolio/design`): 01-editorial-index (inline), 02-engineering-console and 03-split-dossier (workers; AA contrast measured, 360/768/1440 px and print checked). Parent spot check: 0 denylist hits, 0 external URLs, 0 voseo in all three. Repo-local git identity set to the CV name and public email.
- L7. Owner's answer to the design pick (2026-11-10), verbatim: "inestiga como hay opciones de presentacion dale". Read as: research the available presentation options, then choose and proceed.
- L8. Research result (explorer, sourced) and decision: hybrid — 03 split-dossier skeleton (identity, role and stack top-left for F-pattern scanning), 01 editorial style for the featured case studies and the numbered index, 02 only for big metric numerals and the area filter; light theme only (dark prints badly and terminal looks read worst for general audiences). Bilingual as separate URLs (`/` es, `/en/` en) with reciprocal hreflang when `meta.siteUrl` is set (Google advises against same-URL content swaps). PDFs: per language a 2-page A4 single-column ATS-friendly CV plus a longer portfolio PDF; A4 because Peru uses ISO A. Added `meta.siteUrl` (empty until the owner picks a host).
- L9. Owner stop (2026-11-10), verbatim: "terminamos". The T4/T5 worker was cancelled when the session shut down; it left only an untracked, unverified `tests/test_build.py` (no `tools/`, no `site/`). T4, T5 and T6 remain open. Resume: relaunch one writer with the T4/T5 handoff (repository_root=/home/rodrigo/portafolio), reusing or replacing that test file.
- L10. Owner follow-up (2026-11-10), verbatim: "dale completa". L9 meant "let's finish", not a stop: resume T4, T5 and T6 to completion.
- L3. Evidence prep: Engram lists 402 projects; only 19 have ≥5 observations. Exported those to `research/engram/*.json` and condensed observations to `research/obs/*.md` (big two also as `*.highlights.md`). `research/` is gitignored because it holds private data.
