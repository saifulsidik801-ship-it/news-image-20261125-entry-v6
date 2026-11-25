// news-image-20261125 entry (Node 22, standard library only).
// The front page is entry.png beside this file; the program copies it to
// the grader's output directory so the judge sees exactly those bytes.
// Run locally with: mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync } from 'node:fs';
import { join } from 'node:path';

copyFileSync(new URL('./entry.png', import.meta.url), join(process.env.MAKEFUN_OUTPUT_DIR ?? '/output', 'entry.png'));
