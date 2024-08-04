from pathlib import Path

from vct import game_loop

dir = fr"{str(Path(__file__).parents[1])}\VCT"

game_loop(dir)
