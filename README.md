# SimSaber
Python-based Beat Saber replay simulator and scoring validator.

### Notes

<img src="note.png" width="300" />

There are two box colliders for Beat Saber blocks; the bigger one (bigger than the visible cube) can detect only the good cuts. The smaller one (smaller than the cube itself) is for bad cuts only. We can't find the hitbox sizes in the game code; the actual hitboxes are encoded into game assets together with the models. The BeatLeader team did us a favor and built mods to discover the hitbox sizes. From this, we know that (excluding all modifiers):

- Arrow "good cut" hitbox is always:
  - Size: 0.8 x 0.5 x 1.0 box
  - Centered at: 0, 0, -0.25 relative to the note model
- Dot note "good cut" hitbox is always:
  - Size 0.8 x 0.8 x 1.0 box
  - Centered at 0, 0, -0.25 relative to the note model
- All notes "bad cut" hitbox is always:
  - Size: 0.4 x 0.4 x 0.4 box
  - Centered at 0, 0, 0 relative to the note model
