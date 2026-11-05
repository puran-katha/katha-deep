# कथा दीप · Katha Deep — website

A free, static website for your mythology reels (Hindi + English).

## 1. Put in your Instagram handle
Open `index.html`, search for `instagramHandle`, and replace `yourhandle` with yours (no @).
To rename the site, search for `कथा दीप` / `Katha Deep`.

## 2. Host it free on GitHub Pages
1. Sign in at https://github.com → **New repository** → name it e.g. `katha-deep` → Public → Create.
2. On the empty repo page click **uploading an existing file**.
3. Drag in **everything inside this `website` folder** (`index.html`, `README.md`, and the `assets` folder). Click **Commit changes**.
4. Repo → **Settings → Pages** → Source: *Deploy from a branch* → Branch `main`, folder `/ (root)` → Save.
5. After ~1 minute your site is live at `https://<your-username>.github.io/katha-deep/`.
   Tip: name the repo `<your-username>.github.io` to get the shorter URL `https://<your-username>.github.io/`.
6. Put that link in your Instagram bio.

## 3. Add a new reel later
1. Compress it (keeps it under GitHub's 25 MB browser-upload limit):
   `ffmpeg -i MyReel.mp4 -vf scale=720:-2 -c:v libx264 -preset veryfast -crf 27 -c:a aac -b:a 96k -movflags +faststart assets/reels/my-reel.mp4`
2. Save a cover image as `assets/posters/my-reel.jpg` (vertical, ~540×960).
   `ffmpeg -ss 3 -i MyReel.mp4 -frames:v 1 -vf scale=540:-2 assets/posters/my-reel.jpg`
3. In `index.html`, copy one block in the `REELS` list, set `id: "my-reel"`, and fill in the Hindi/English text.
   `deity` can be `vishnu`, `shiva`, `hanuman`, `ganesha` (filter buttons appear automatically).
4. Upload the changed files to the repo again — the site updates in about a minute.

## Features
- Language switch: हिं / हिं + En / En (remembered per visitor)
- Hover a card to preview, click for a full-screen vertical player
- Swipe up/down (phone) or arrow keys (computer) to go to the next reel
- Share button — every reel has its own link, e.g. `.../#reel/gajendra-moksha`
