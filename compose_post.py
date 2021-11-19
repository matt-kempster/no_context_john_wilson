import ast
import os
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple

from subtitle_to_scene import get_subtitle_for_scene


def main():
    scenes_posted_file = Path.cwd() / "scenes_posted.txt"
    scenes_posted: Dict[int, List[Tuple[int, str]]] = ast.literal_eval(
        scenes_posted_file.read_text()
    )
    episode = random.randint(1, 6)
    episode_dir = list(Path.cwd().glob(f"{episode} - *"))[0]
    pics_per_scene: Dict[int, Any] = ast.literal_eval(
        (episode_dir / "pics_per_scene.txt").read_text()
    )
    while True:
        (scene, pic) = random.choice(list(pics_per_scene.items()))
        if scene in (post[0] for post in scenes_posted.get(episode, [])):
            continue
        if pic == "0" or pic == "N":
            continue

        if type(pic) == int:
            glob_filename = f"**/*-{str(scene).zfill(3)}-0{pic}.png"
            the_pic = list(episode_dir.glob(glob_filename))[0]
            pic_name = "C:\\" + str(the_pic.relative_to(Path("/mnt/c"))).replace("/", "\\")
            print(f"Post this: {pic_name}")
        else:
            print(f"Pic needs human help: {episode=}, {scene=}, {pic=}")

        prev_cwd = Path.cwd()
        os.chdir(episode_dir)
        subtitle = get_subtitle_for_scene(scene)
        os.chdir(prev_cwd)

        print(f"Caption:\n{subtitle}")
        print(f"[S1E{episode}] #howtowithjohnwilson ")
        break

    if input("Did you post it? y/n: ") == "y":
        post_record = (scene, str(datetime.today()).split()[0])
        if scenes_posted.get(episode):
            scenes_posted[episode].append(post_record)
        else:
            scenes_posted[episode] = [post_record]
        scenes_posted_file.write_text(str(scenes_posted))


if __name__ == "__main__":
    main()
