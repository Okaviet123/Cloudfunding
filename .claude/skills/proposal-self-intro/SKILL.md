---
name: proposal-self-intro
description: Embed Yuhei Yamada's self-introduction (About me with photo and career, the SilkRoad 2040 vision map, and the Let's connect block with WeChat / LINE / WhatsApp / LinkedIn) into a partner proposal artifact, then smooth the seams so the page reads as one story. Use this whenever the user wants to add 自己紹介, About me, 略歴, SilkRoad 2040, ビジョン, or 連絡先 / QR codes to a proposal (提案アーティファクト, partnership proposal, Japan market plan) for any manufacturer partner such as MorTech, DERAX, EDUP or a new one, or asks to re-sync proposals after the self-introduction changed. Also use it when the user says the self-introduction feels disconnected from the rest of a proposal.
---

# Proposal self-introduction

Yuhei sends bilingual/trilingual (EN · 中文 · 日本語) proposal artifacts to manufacturers in China and ASEAN. Every proposal should carry the same self-introduction, placed early, flowing naturally into the proposal's own content, and ending with a way to reach him directly. This skill puts it there and fixes the seams.

## Source of truth

- `05_sales/profile/self-introduction.html` — the standalone page (published at https://claude.ai/artifact/BWYL4zkvcMcgh8SxzjxdRP). Sections `#person`, `#silk-road`, `#connect`; portable CSS between `/* embed:start */` and `/* embed:end */`.
- `05_sales/profile/img/` — `yuhei.jpg`, `qr-wechat.png`, `qr-line.png`, `qr-whatsapp.png`. Each QR is wrapped in a link to its decoded https URL so phone viewers can tap it.

Edit the standalone page first, then re-embed. Never fork the copy inside a proposal: the next re-sync would overwrite it, and the two would drift apart.

## Workflow

1. **Find the proposal.** If the user doesn't name one, list artifacts (`Artifact` action `list`) and pick the proposal they are working on; ask only when two candidates are equally likely. Read it once with `action: "read"` (no path) so a republish is allowed, then again with `path: "index.html"` to get the file on disk. Keep a copy of the pre-embed file in the scratchpad.

2. **Write the bridge sentence** for this partner (see Copy rules). The default is "Step 1 is Japan. We want to start it with {partner}." Change it when the proposal is about a different first market or a different kind of deal.

3. **Run the script** from the repo root:
   ```bash
   python3 .claude/skills/proposal-self-intro/scripts/embed_self_intro.py \
     --intro 05_sales/profile/self-introduction.html \
     --proposal <path/to/proposal/index.html> \
     --partner "MorTech" \
     --bridge-en "Step 1 is Japan.<br>We want to start it with MorTech." \
     --bridge-zh "第一步是日本。<br>我们希望和 MorTech 一起开始。" \
     --bridge-ja "最初の一歩は日本です。<br>MorTech様と一緒に始めたいと考えています。"
   ```
   What it does:
   - Inserts About me and SilkRoad 2040 right after the cover. This is the first `<section>` after `</header>`, or the section named by `--insert-before`.
   - Inserts Let's connect before the appendix. This is `#method`, the section named by `--contact-before`, or the footer.
   - Maps the intro's color tokens to the proposal's (for example `--core` → `--accent`) and scopes any missing tokens to the embedded sections.
   - Adds the bridge: a sentence at the end of the dark band, and a line that crosses into the next section.
   - Makes the map open on Japan on phones.
   - Fences everything with `self-intro` markers.

   Flags:
   - `--makers hide`: use for partners outside China. Yuhei's model is N:N trade, so showing China as the only source misrepresents it for a Thai or Vietnamese maker.
   - `--replace`: re-embed after the standalone page changed. It strips the previous marked embed first.

   Read the script's report:
   - `token … scoped` lines are fine.
   - A `CHECK class names used by both pages` line means a class is styled by both pages without a parent scope. Rename the intro's class in the standalone page and re-embed. This is how `.src` (the proposal's source tag) once turned the Makers legend into a fat white bar.

4. **Fix the rhythm of section backgrounds.** The embedded sections are About (white) → SilkRoad (ink band) → next section, and Let's connect (white) sits before the appendix. Change the `band` classes of the proposal's own sections so that neighbours alternate (`white` / `alt` / plain / `deep`). Two equal backgrounds in a row read as one long section, and that is what makes a seam feel "苦しい".

5. **Review the whole flow, not just the inserted part.** Render the page at 1280px and 390px (Playwright, light and dark) and look at every seam: cover → About, SilkRoad → first content section, last content section → Let's connect. Check:
   - No horizontal overflow and no script errors.
   - The Makers legend shows a thin dashed line.
   - The QR codes are not clipped at 390px.
   - The bridge line visibly runs across the band edge.
   - Something in the proposal ties back to the vision. If nothing does, suggest one line, for example in the plan: "After Japan: ASEAN and India." Do not add it silently.
   - The proposal's hero promise still comes before the self-introduction (the cover stays first).

6. **Publish** to the proposal's URL with the images:
   ```
   files: {"img/yuhei.jpg": "05_sales/profile/img/yuhei.jpg",
           "img/qr-wechat.png": "05_sales/profile/img/qr-wechat.png",
           "img/qr-line.png": "05_sales/profile/img/qr-line.png",
           "img/qr-whatsapp.png": "05_sales/profile/img/qr-whatsapp.png"}
   ```
   The proposal's own images stay, because files left out of a publish are kept.

7. **Report in Japanese business keigo.** Give the link, a numbered flow table (section → role, new sections marked 【新規】), what you adjusted at the seams, and the points to confirm. Remind the user that the artifact is private until they share it.

## Copy rules (learned from Yuhei's edits)

- **Plain and strong.** Write junior-high-school English: short sentences and simple verbs. Asian-business directness, not Western corporate phrasing. Use "Let's go far together!", not "I am looking for partners who want to go the distance".
- **"SilkRoad 2040"** is one word plus the year. It is a proper noun and keeps that form in every language (日本語 too: 「SilkRoad 2040」).
- **Japanese** uses business keigo toward the partner, with 様 after the partner name. Keep Yuhei's own words where he gave them: 今の商流, 直近のチャレンジ.
- **Markets.**
  - Now: Japan, Thailand, Myanmar.
  - Next challenge: ASEAN (Indonesia, Vietnam), India.
  - Future: the Middle East, Europe.
  - Bangkok is the hub.
  - China is shown only as Makers, and only for China-based partners.
- **Facts.** Use only facts Yuhei stated or trade.bku1.com states. Flag anything you could not verify (for example "自社の学校" is his word, not on the site). Do not reintroduce removed items such as the 525 / 96 workforce numbers unless he asks.
- **Layout.** The face photo sits at the right end of the name block. The contact block comes after the proposal's questions or plan, as the last call to action before the appendix.

## When the standalone page changes

Edit `05_sales/profile/self-introduction.html`, publish it, commit, then re-run the script with `--replace` on each proposal that carries it, and republish each one. Keep class names in the standalone page unique enough to survive embedding (`cchip`, `mk`, `.who .role`), and keep the `embed:start` / `embed:end` markers around the portable CSS.
