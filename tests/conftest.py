"""Forces pygame onto SDL's headless "dummy" video/audio drivers before
anything in the test session imports pygame, so the full test suite
(including the smoke test that spins up a real Game/Renderer) runs without
a display -- e.g. in CI or over SSH.
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
