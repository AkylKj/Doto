# Doto Cyrillic change log

## 2026-10-26 — version 1.001, independent Russian extension

Upstream: oliverlalan/Doto, commit 1c587f2eed62cb257055540ac2a15f356070414f (2024-10-06 UTC).
Original design and copyright remain attributed to the Doto Project Authors; see AUTHORS.txt, CONTRIBUTORS.txt and OFL.txt. This independent fork is not an upstream release or an endorsement by those authors.

Added U+0410–U+044F, U+0401, U+0451, U+2116 and U+20BD in all four UFO masters. New drawings follow the 100-unit dot lattice and use original dot contours. Latin lookalikes reuse original geometry. Russian lowercase к has a dedicated x-height drawing. Added Cyrillic/Russian language-system declarations and mark positioning. Corrected advance widths of four existing combining marks to zero; their contours, and all other original GLIF contours, are unchanged.

New binaries use the family name Doto Cyrillic, preserving OFL metadata, both variable axes and nine weight instances. Added source generator, pinned build environment, static/variable TTF and WOFF2 builds, independent coverage/interpolation/shaping/regression tests, CI and a rendered Russian specimen.

Scope: modern Russian alphabet, numeral sign and ruble sign. No claim of full Unicode Cyrillic, italic or language-specific Serbian/Bulgarian support. Existing upstream binary directories are preserved and clearly distinguished from the new fonts/cyrillic builds.
