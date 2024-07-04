import os
import sys
from datetime import datetime
from pathlib import Path

import appmap

output_directory = Path("tmp/appmap/code")
output_directory.mkdir(parents=True, exist_ok=True)  # Step 2: Ensure the directory exists

timestamp = datetime.now().isoformat(timespec="seconds")
output_file = output_directory / f"{timestamp}.appmap.json"

r = appmap.Recording()
with r:
    import generate

    generate.test("presets/templates/Generator(CC48fs12).hlx", "")
    # print(sample.C().hello_world(), file=sys.stderr)

with open(output_file, "w") as f:
    f.write(
        appmap.generation.dump(
            r,
            {
                "name": str(timestamp),
                "recorder": {
                    "type": "code",
                    "name": "code",
                },
            },
        )
    )
