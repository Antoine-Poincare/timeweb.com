import io
import json
import tarfile
import time

from lxml.html import iterlinks

import requests

from rq import get_current_job


def parse(tid: str, host: str) -> None:
    job = get_current_job()
    print(f"Starting task for {host}")
    job.meta["status"] = "In progress"
    job.save_meta()

    links = []
    r = requests.get(f"https://{host}")
    if r.status_code == 200:
        for elem in iterlinks(r.text):
            el, href, path, n = elem
            #time.sleep(0.2)
            if path.startswith("/"):
                print(path)
                links.append(path)
        json_str = json.dumps(links, ensure_ascii=False, indent=4) + "\n"
        json_bytes = json_str.encode('utf-8')
        with tarfile.open(f"static/{tid}.tar.xz", "w:xz") as xz:
            buf = io.BytesIO(json_bytes)
            info = tarfile.TarInfo(f"{tid}.json")
            info.size = buf.seek(0, io.SEEK_END)
            xz.addfile(info,
                       fileobj=io.BytesIO(buf.getvalue()))
        job.meta["status"] = "Completed"
        job.meta["url"] = f"https://timeweb.com/ru/task/{tid}.tar.xz"
        job.save_meta()
    else:
        job.meta["status"] = f"Error: {r.status_code}"
        job.save_meta()
    print('Task completed')
