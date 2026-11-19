import os
import subprocess
import shutil
import pytest
from opengeode import ogParser, ogAST
from opengeode.opengeode import SDL_View, SDL_Scene
from PySide6.QtWidgets import QApplication

@pytest.fixture(scope="module")
def qapp():
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_makefile_generation_content(qapp, tmp_path, monkeypatch):
    """Test that Makefile.<process> contains correct relative paths for Ada, C, Rust and clean target."""
    pr_dir = tmp_path / "project"
    pr_dir.mkdir()
    monkeypatch.chdir(pr_dir)
    pr_file = pr_dir / "myproc.pr"
    pr_file.write_text("process myproc; start; stop; endprocess;")

    asn1_file1 = pr_dir / "dataview-uniq.asn"
    asn1_file1.write_text("TASTE-Dataview DEFINITIONS ::= BEGIN END")
    asn1_file2 = pr_dir / "extra.asn"
    asn1_file2.write_text("Extra-Dataview DEFINITIONS ::= BEGIN END")

    scene = SDL_Scene(context='process')
    view = SDL_View(scene)
    view.filename = str(pr_file)
    proc = ogAST.Process()
    proc.processName = "myproc"
    proc.instance_of_ref = None
    scene.ast = ogAST.AST()
    scene.ast.processes = [proc]

    # Set up DV with multiple ASN.1 files
    class FakeDV:
        asn1Files = [str(asn1_file1), str(asn1_file2)]
        exportedTypes = {}

    ogParser.DV = FakeDV()
    proc.DV = FakeDV()

    view._silent_save = True
    assert view.save_diagram()

    makefile_path = pr_dir / "Makefile.myproc"
    assert makefile_path.exists()
    content = makefile_path.read_text()

    # Verify no '../' in other ASN.1 files (which happened when relative to 'code')
    lines = content.splitlines()
    for line in lines:
        if "asn1scc" in line:
            assert "dataview-uniq.asn" in line
            assert "extra.asn" in line
            assert "../extra.asn" not in line

    # Verify Ada rule
    assert "code/myproc_datamodel.asn" in content
    # Verify C rule has code_c and NOT code/myproc_datamodel.asn in c target
    c_target = content[content.index("c:"):content.index("rust:")]
    assert "code_c/myproc_datamodel.asn" in c_target
    assert "code/myproc_datamodel.asn" not in c_target

    # Verify Rust rule
    rust_target = content[content.index("rust:"):content.index("clean:")]
    assert "code_rust" in rust_target
    assert "opengeode --toRust ../*.pr" in rust_target
    assert "code_rust/myproc_datamodel.asn" in rust_target
    assert "-Rust" in rust_target
    assert "cargo build --lib" in rust_target

    # Verify clean rule
    clean_target = content[content.index("clean:"):]
    assert "rm -rf code code_c code_rust" in clean_target


def test_makefile_execution(qapp, tmp_path, monkeypatch):
    """Test running make targets on an actual project."""
    monkeypatch.chdir(tmp_path)
    src_dir = os.path.abspath("/home/maxime/tool-src/opengeode/tests/testsuite/test-append")
    if not os.path.exists(src_dir):
        pytest.skip("test-append not found")

    shutil.copy(os.path.join(src_dir, "og.pr"), str(tmp_path))
    shutil.copy(os.path.join(src_dir, "dataview-uniq.asn"), str(tmp_path))
    original_pr = (tmp_path / "og.pr").read_text()

    scene = SDL_Scene(context='process')
    view = SDL_View(scene)
    view.filename = str(tmp_path / "og.pr")
    proc = ogAST.Process()
    proc.processName = "og"
    proc.instance_of_ref = None
    scene.ast = ogAST.AST()
    scene.ast.processes = [proc]

    class FakeDV:
        asn1Files = [str(tmp_path / "dataview-uniq.asn")]
        exportedTypes = {}

    ogParser.DV = FakeDV()
    proc.DV = FakeDV()

    view._silent_save = True
    assert view.save_diagram()

    # Restore the actual og.pr contents so opengeode can parse it during build
    (tmp_path / "og.pr").write_text(original_pr)

    makefile = tmp_path / "Makefile.og"
    assert makefile.exists()

    # Test make c
    res_c = subprocess.run(["make", "-f", "Makefile.og", "c"], cwd=str(tmp_path), capture_output=True, text=True)
    assert res_c.returncode == 0, f"make c failed:\n{res_c.stderr}\n{res_c.stdout}"
    assert (tmp_path / "code_c" / "og.c").exists()

    # Test make rust
    res_rust = subprocess.run(["make", "-f", "Makefile.og", "rust"], cwd=str(tmp_path), capture_output=True, text=True)
    assert res_rust.returncode == 0, f"make rust failed:\n{res_rust.stderr}\n{res_rust.stdout}"
    assert (tmp_path / "code_rust" / "target").exists()

    # Test make clean
    res_clean = subprocess.run(["make", "-f", "Makefile.og", "clean"], cwd=str(tmp_path), capture_output=True, text=True)
    assert res_clean.returncode == 0
    assert not (tmp_path / "code_c").exists()
    assert not (tmp_path / "code_rust").exists()
