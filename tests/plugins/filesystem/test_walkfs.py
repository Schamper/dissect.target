from pytest_codspeed import BenchmarkFixture

from dissect.target.filesystem import VirtualFile, VirtualFilesystem
from dissect.target.plugins.filesystem.walkfs import WalkFSPlugin
from dissect.target.target import Target
from tests._utils import absolute_path


def test_walkfs_plugin(target_unix: Target, fs_unix: VirtualFilesystem) -> None:
    fs_unix.map_file_entry("/path/to/some/file", VirtualFile(fs_unix, "file", None))
    fs_unix.map_file_entry(
        "/path/to/some/other/file.ext", VirtualFile(fs_unix, "file.ext", None)
    )
    fs_unix.map_file_entry("/root_file", VirtualFile(fs_unix, "root_file", None))
    fs_unix.map_file_entry(
        "/other_root_file.ext", VirtualFile(fs_unix, "other_root_file.ext", None)
    )
    fs_unix.map_file_entry("/.test/test.txt", VirtualFile(fs_unix, "test.txt", None))
    fs_unix.map_file_entry(
        "/.test/.more.test.txt", VirtualFile(fs_unix, ".more.test.txt", None)
    )

    target_unix.add_plugin(WalkFSPlugin)

    results = list(target_unix.walkfs())
    assert len(results) == 14
    assert sorted([r.path for r in results]) == [
        "/",
        "/.test",
        "/.test/.more.test.txt",
        "/.test/test.txt",
        "/etc",
        "/other_root_file.ext",
        "/path",
        "/path/to",
        "/path/to/some",
        "/path/to/some/file",
        "/path/to/some/other",
        "/path/to/some/other/file.ext",
        "/root_file",
        "/var",
    ]


def test_benchmark_walkfs(benchmark: BenchmarkFixture, target_bare: Target) -> None:
    fs = VirtualFilesystem()
    fs.map_dir_from_tar("/", absolute_path("_data/plugins/filesystem/walkfs/image.tar"))
    target_bare.filesystems.add(fs)
    target_bare.apply()

    target_bare.add_plugin(WalkFSPlugin)

    result = benchmark(lambda: list(target_bare.walkfs()))
    assert len(result) == 10_000 * 4 + 1
