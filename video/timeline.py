"""
Loads the active project's edit (video/projects/<name>.py).
Select with the GTA_PROJECT environment variable (default: p2).

  p1 - "10 détails que personne ne connaît" (vertical source clips, voiceover.mp3)
  p2 - "10 trucs à savoir avant de jouer"   (16:9 trailer footage reframed to 9:16, voiceover2.mp3)
"""
import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
PROJECT = os.environ.get("GTA_PROJECT", "p2")
_mod = importlib.import_module(f"projects.{PROJECT}")
globals().update({k: v for k, v in vars(_mod).items() if not k.startswith("__")})
