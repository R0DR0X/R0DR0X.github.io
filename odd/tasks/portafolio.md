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
- T2 [S1, S3, S4, S5] Bilingual anonymized content source `content/portfolio.json` + anonymization map in `research/` → inline. Commit: pending
- T3 [S2, S3] Design directions under `design/portafolio/` (gentle-design, 3 artboards); owner picks one → inline. Commit: pending
- T4 [S2, S4] Website `site/index.html` rendered from the content source, ES/EN toggle → inline. Commit: pending
- T5 [S2, S4] PDF per language rendered from the same content (print stylesheet + headless Chromium) → inline. Commit: pending
- T6 [S4, S5] Checks: anonymization denylist scan, both languages complete, no external URLs, a11y basics → inline. Commit: pending

## Log

- L1. User request (2026-11-10), verbatim: "puedes hacerme un portafolio de todo lo que se y todo lo que hago en todos los proyectos"
- L2. Questionnaire answers: Formato "Ambos"; Público "General / marca personal"; Idioma "Bilingüe"; Privacidad "Anonimizarlos".
- L4. T1 done: 4 explorers returned `research/inventory-all.md` (626 lines, read in full). Identity from the owner's own CV `~/Documentos/CV_Ivan_Rodrigo_Pianto.html`: name, headline, location, email, GitHub, roles and years. CV claims without evidence (e.g. commit counts, Prisma) are not used; numbers come only from inventory evidence.
- L5. Anonymization decision under S5: the owner's own brands (company, e-commerce brand, open-source app, game name) are anonymized too, because they are real company/product names; the owner can opt them back in later. Public bodies and datasets (SUNAT, SEACE, ECMWF, OSM) and technology vendors in stacks stay named. Private denylist: `research/denylist.txt` (word-boundary, case-insensitive).
- L3. Evidence prep: Engram lists 402 projects; only 19 have ≥5 observations. Exported those to `research/engram/*.json` and condensed observations to `research/obs/*.md` (big two also as `*.highlights.md`). `research/` is gitignored because it holds private data.
