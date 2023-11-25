from invoke import Collection, Exit, task
from loguru import logger
from pathlib import Path

import tempfile


@task
def test(c):
    logger.info("Testing for valid token")

    token = c.scdl.token
    output_format = c.scdl.tests.output_format
    test_id = c.scdl.tests.test_id
    test_url = c.scdl.tests.test_url
    options = [" ".join(c.scdl.tests.options)]

    logger.debug(f"Using token {token}")

    options.append(f"--username oauth --password {token}")
    options.append(f"--output '{output_format}'")

    with tempfile.TemporaryDirectory() as tmpdir:
        logger.info(f"Created temporary directory for tests at {tmpdir}")
        with c.cd(tmpdir):
            c.run("yt-dlp {} {}".format(" ".join(options), test_url))
            if not Path(f"{tmpdir}/{test_id}.aac").exists():
                error_msg = "Test failed, could not find .aac file"
                logger.error(error_msg)
                raise Exit(error_msg)

    logger.info("Test passed")


@task
def convert(c, filename):
    logger.info(f"Converting {filename}...")
    if filename.endswith(".wav"):
        c.run(f"flac -s --best -o '{filename[:-4]}.flac' '{filename}'")
    elif filename.endswith(".aac"):
        c.run(f"ffmpeg -i '{filename}' -c:a copy '{filename[:-4]}.m4a'")


@task
def rename(c, filename):
    c.run()


@task
def tag(c, filename):
    c.run()


@task
def download_playlist(
    c,
    url,
    archive_file=None,
    convert_files=False,
):
    logger.info(f"Downloading playlist: {url}")

    token = c.scdl.token
    download_dir = c.scdl.playlists.download_dir
    output_format = c.scdl.playlists.output_format
    options = [" ".join(c.scdl.playlists.options)]

    if archive_file is None:
        archive_file = c.scdl.playlists.archive_file

    options.append(f"--username oauth --password {token}")
    options.append(f"--output '{output_format}'")
    options.append(f"--download-archive {archive_file}")
    # options.append("--simulate")

    if convert_files:
        options.append("--exec 'invoke convert'")

    with c.cd(download_dir):
        c.run(f"yt-dlp {' '.join(options)} {url}")


@task
def download_playlists(c):
    playlist_urls = c.scdl.playlists.playlist_urls

    for url in playlist_urls:
        download_playlist(c, url)


@task
def download_single(
    c,
    url,
    token=None,
    dir=None,
    output=None,
    convert_files=True,
):
    logger.info(f"Downloading single: {url}")

    options = [" ".join(c.scdl.singles.options)]

    if dir is None:
        dir = c.scdl.singles.download_dir
    if output is None:
        output = c.scdl.singles.output_format
    if token is None:
        token = c.scdl.token

    if dir and output:
        options.append(f"--output {dir}/{output}")
    if token:
        options.append(f"--username oauth --password {token}")
    else:
        logger.error("No token specified!")
        raise Exit

    if convert_files:
        options.append("--exec 'invoke convert'")

    c.run("echo yt-dlp {} {}".format(" ".join(options), url))


ns = Collection(test, convert, rename, tag, download_playlist, download_single)
ns.configure({"scdl": {"token": ""}})
