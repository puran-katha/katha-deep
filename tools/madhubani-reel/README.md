# Madhubani reel kit

Code for the Madhubani-style devotional reels (first used for "दिवाली क्यों मनाते हैं?").
Not part of the website. It's kept here so the reels can be rebuilt or new ones made.

- `madhu.py`: drawing kit. Includes `Pen`, the patterns, `figure(kind, f, h, pose)` for ram/sita/lakshman/hanuman/ravana, `diya`, `peacock`, `fish`, `tree` and the palette.
- `reel_template.py`: the Diwali reel (scenes, backgrounds, animation, captions, border, brush wipe). Run `GF=<fonts dir> python3 reel_template.py out.mp4 [t0 t1]`.
- `audio_template.py`: tanpura bed, per-scene sound effects and ducked voice (needs `sfx.py`).
- `voice_proc.py`: tightens pauses and speeds up a Gemini narration (rubberband, formant preserved).
- `align_sections.py`, `align_phrases.py`, `dscript_example.py`: align narration sections to scenes with Piper + MFCC DTW.
