#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''Tests for the orbit chat panel's skill handling.

The panel hands the bundled SDL skill (orbit_skills/
SDL_SKILL_DOCUMENTATION.md) to orbit with orbit-acp's use_skill(name,
text) — the API for a skill the app ships itself — when the connection
to orbit is established. These tests check the parts that do not need a
GUI: the frontmatter stripping, the staging call, and the degradation
when staging is impossible.
'''

import pytest

# The orbit_acp import is optional for OpenGEODE as a whole; for these
# tests it is required (they exercise the panel's use of its API).
orbit_acp = pytest.importorskip('orbit_acp')
pytest.importorskip('PySide6')

from orbit_acp import Conversation, OrbitError

from opengeode.OrbitChatPanel import (SKILL_FILENAME, SKILL_NAME,
                                     OrbitAgent, _skill_body, _stage_skill)

FAKE = "python3 -m orbit_acp.testing.fake_agent"


def test_skill_name_matches_the_bundled_file():
    '''The name staged is the one the skill file declares in its YAML
    frontmatter, so what orbit stages reads as the skill it names.'''
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    skill = os.path.join(os.path.dirname(here), os.pardir,
                         'orbit_skills', SKILL_FILENAME)
    with open(skill, encoding='utf-8') as f:
        front = f.read(400)
    assert f'name: {SKILL_NAME}' in front


def test_skill_is_embedded_in_the_qt_resource():
    '''The skill ships the way the fonts and help files do: embedded in
    opengeode.qrc, compiled by pyside6-rcc into opengeode/icons.py (a
    package module every pip install carries). This is what makes the
    skill available in a pip installation, where no skill file exists on
    disk. The resource must hold the whole skill, frontmatter included.'''
    from PySide6.QtCore import QFile, QIODevice
    import opengeode.icons  # NOQA - importing registers the Qt resources
    f = QFile(':/orbit_skills/' + SKILL_FILENAME)
    assert f.open(QIODevice.ReadOnly), 'the skill is not in the resource'
    data = bytes(f.readAll().data())
    f.close()
    assert data.startswith(b'---')
    assert b'name: sdl-model-construction' in data
    assert b'OpenGEODE SDL Model Construction' in data
    # Byte-identical with the on-disk file of the source checkout.
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    disk = os.path.join(os.path.dirname(here), os.pardir,
                       'orbit_skills', SKILL_FILENAME)
    with open(disk, 'rb') as fp:
        assert data == fp.read()


def test_skill_is_read_from_the_resource_not_the_disk(monkeypatch):
    '''_read_skill_text serves the skill from the compiled Qt resource
    (what a pip install carries) even when no file exists on disk.'''
    import opengeode.OrbitChatPanel as panel
    monkeypatch.setattr(panel, '_bundled_skill_path',
                        lambda: '/nonexistent/orbit_skills/SKILL.md')
    text = panel._read_skill_text()
    assert text.startswith('---\nname: sdl-model-construction')
    body = panel._skill_body()
    assert body.startswith('# OpenGEODE SDL Model Construction')


def test_skill_falls_back_to_the_file_when_resource_lacks_it(monkeypatch):
    '''A source checkout whose icons.py predates the skill in the qrc
    (resources not recompiled) still finds the skill through the disk
    fallback: _read_skill_text reads the file when the Qt resource is
    not there.'''
    import os
    import opengeode.OrbitChatPanel as panel
    here = os.path.dirname(os.path.abspath(__file__))
    disk = os.path.join(os.path.dirname(here), os.pardir,
                       'orbit_skills', SKILL_FILENAME)
    with open(disk, encoding='utf-8') as fp:
        raw = fp.read()
    monkeypatch.setattr(panel, '_read_skill_text', lambda: raw)
    body = panel._skill_body()
    assert body.startswith('# OpenGEODE SDL Model Construction')


def test_skill_body_has_no_frontmatter():
    '''orbit stages only the instruction body of a skill (it adds the
    "# Skill: <name>" heading itself), so the YAML frontmatter of the
    bundled file — metadata for discovery, not instructions — must be
    stripped, exactly as orbit's own skill loader strips it from disk.'''
    body = _skill_body()
    assert body, 'the bundled SDL skill was not found'
    assert not body.lstrip().startswith('---')
    assert 'name: sdl-model-construction' not in body
    assert 'description:' not in body[:200]
    # The real content survives: the skill's own title heading.
    assert body.startswith('# OpenGEODE SDL Model Construction')


def test_skill_body_is_frontmatter_stripped(tmp_path, monkeypatch):
    '''_skill_body mirrors orbit's frontmatter parsing: a fence is a
    whole line of three dashes; the body is what follows the closing
    fence, stripped; a file without fences is all body.'''
    fake = tmp_path / 'SKILL_DOC.md'
    fake.write_text('---\nname: x\ndescription: y\n---\n\nUseful text.\n',
                    encoding='utf-8')
    import opengeode.OrbitChatPanel as panel
    # Feed the parser through its read seam, so no resource or disk file
    # interferes with the pure frontmatter-stripping behaviour.
    monkeypatch.setattr(panel, '_read_skill_text',
                        lambda: fake.read_text(encoding='utf-8'))
    assert panel._skill_body() == 'Useful text.'
    # No frontmatter: whole file is the body.
    fake.write_text('Just body.\n', encoding='utf-8')
    assert panel._skill_body() == 'Just body.'
    # Unclosed frontmatter: orbit's loader treats the whole file as the
    # body too (frontmatter exists only when both fences are present).
    fake.write_text('---\nname: x\n\nBody only.\n', encoding='utf-8')
    assert panel._skill_body().endswith('Body only.')
    assert panel._skill_body().startswith('---')


def test_stage_skill_hands_the_bundled_skill_to_orbit():
    '''The staging call the panel makes when the connection is
    established: use_skill(name, text) with the bundled body. The fake
    agent checks name and text as orbit itself checks them.'''
    with Conversation(command=FAKE.split(), cwd='.') as chat:
        assert _stage_skill(chat) is True


def test_stage_skill_refused_by_the_agent_returns_false():
    '''A staging that the agent refuses (an orbit without the text form,
    or any other error) degrades to False: the conversation stays
    usable, just without the skill.'''
    class Refuses:
        def use_skill(self, name, text=''):
            raise OrbitError('no skill loading here')
    assert _stage_skill(Refuses()) is False


def test_stage_skill_without_body_returns_false(tmp_path, monkeypatch):
    '''No skill file shipped (a build without it): nothing is staged and
    nothing is asked of the agent.'''
    import opengeode.OrbitChatPanel as panel
    monkeypatch.setattr(panel, '_skill_body', lambda text=None: '')
    calls = []

    class Chat:
        def use_skill(self, name, text=''):
            calls.append((name, text))
    assert panel._stage_skill(Chat()) is False
    assert calls == []


def test_each_mode_stages_its_own_skill():
    '''The panel hands orbit the mode's staged skill: the complete SDL
    construction reference in file mode (the agent edits files, it
    needs the whole language), and ONLY the compact MCP remote-control
    interface in mcp mode — its quick card covers common SDL text and
    it points at the full reference, which the panel publishes to the
    model directory's .orbit/skills/ for ON-DEMAND loading with
    skill(name=...). Staging both (~30k tokens) made reasoning models
    burn context deliberating before the first tool call.'''
    import opengeode.OrbitChatPanel as panel
    from opengeode.OrbitChatPanel import MODE_FILE, MODE_MCP

    class Chat:
        def __init__(self):
            self.calls = []
        def use_skill(self, name, text=''):
            self.calls.append((name, text))
            return True
    # File mode: the SDL reference only
    chat = Chat()
    assert panel._stage_skill(chat, MODE_FILE) is True
    assert [n for n, _ in chat.calls] == [panel.SKILL_NAME]
    # MCP mode: ONLY the remote-control interface (the reference is
    # published on demand instead of staged)
    chat = Chat()
    assert panel._stage_skill(chat, MODE_MCP) is True
    assert [n for n, _ in chat.calls] == [panel.MCP_SKILL_NAME]
    # The staged body is the content, not the frontmatter
    bodies = {n: b for n, b in chat.calls}
    assert bodies[panel.MCP_SKILL_NAME].startswith(
        '# OpenGEODE SDL Remote Control')
    assert not bodies[panel.MCP_SKILL_NAME].startswith('---')


def test_publish_reference_skill_writes_the_on_demand_copy(tmp_path):
    '''In MCP mode the complete SDL reference must be loadable on
    demand: the panel writes it into the model directory's
    .orbit/skills/ and marks the directory as an orbit project root
    (an empty orbit.json) — without that marker orbit never looks at
    .orbit/skills/ at all. The written file keeps its frontmatter
    (orbit's own loader reads it to get the skill's name).'''
    import os
    import opengeode.OrbitChatPanel as panel

    model_dir = str(tmp_path / "model")
    os.makedirs(model_dir)
    # A .pr so the dir looks like a model directory
    with open(os.path.join(model_dir, "m.pr"), "w") as fp:
        fp.write("system m; endsystem;\n")

    assert panel._publish_reference_skill(model_dir) is True
    root = os.path.join(model_dir, ".orbit", "skills")
    assert sorted(os.listdir(root)) == [panel.SKILL_FILENAME]
    with open(os.path.join(root, panel.SKILL_FILENAME),
              encoding="utf-8-sig") as fp:
        body = fp.read()
    assert body.startswith("---")
    assert "name: sdl-model-construction" in body[:200]
    # The project-root marker
    with open(os.path.join(model_dir, "orbit.json")) as fp:
        assert fp.read().strip() == "{}"
    # Idempotent: a second call neither breaks nor rewrites
    before = os.stat(os.path.join(root, panel.SKILL_FILENAME)).st_mtime_ns
    assert panel._publish_reference_skill(model_dir) is True
    after = os.stat(os.path.join(root, panel.SKILL_FILENAME)).st_mtime_ns
    assert before == after
    # An existing marker file is left alone
    with open(os.path.join(model_dir, "orbit.json"), "w") as fp:
        fp.write('{"default_agent": "custom"}\n')
    assert panel._publish_reference_skill(model_dir) is True
    with open(os.path.join(model_dir, "orbit.json")) as fp:
        assert "default_agent" in fp.read()


def test_publish_reference_skill_no_dir_returns_false():
    '''No model directory (a brand-new unsaved diagram): nothing to
    publish to, the call degrades to False.'''
    import opengeode.OrbitChatPanel as panel
    assert panel._publish_reference_skill("") is False


def test_agent_stages_the_skill_before_ready():
    '''OrbitAgent.start stages the skill on the worker thread, after the
    Conversation is opened and before ready is emitted — so the staged
    skill is consumed by the conversation's first question, which is
    what "load the SDL skill at startup" means with this API.'''
    staged = []

    class FakeConversation:
        def __init__(self, **kwargs):
            self.asked = 0
        def use_skill(self, name, text=''):
            staged.append((name, text))
        def close(self):
            pass

    import opengeode.OrbitChatPanel as panel
    monkeypatched = pytest.MonkeyPatch()
    monkeypatched.setattr(panel, 'Conversation', FakeConversation)
    monkeypatched.setattr(panel, '_stage_skill',
                          lambda chat, mode=None: staged.append(
                              ('staged', chat, mode)) or True)
    try:
        agent = OrbitAgent()
        agent.start(cwd='.', briefing='')
        # Wait for the worker thread to open and stage.
        import time
        deadline = time.time() + 10
        while not staged and time.time() < deadline:
            time.sleep(0.01)
        assert staged, 'the skill was not staged at startup'
        assert staged[0][0] == 'staged'
        assert agent.skill_staged is True
        agent.stop()
    finally:
        monkeypatched.undo()


def test_agent_start_in_mcp_mode_publishes_the_reference_to_cwd(tmp_path):
    '''Regression: OrbitAgent.start's worker called the panel's
    _model_dir() on the AGENT — an AttributeError that killed the
    worker thread at startup ("'OrbitAgent' object has no attribute
    '_model_dir'"), so the conversation never became ready and the
    editor showed no chat. The publish must use the conversation's own
    cwd (the model directory passed to start), which is exactly what
    the worker has in scope.'''
    staged = []
    published = []

    class FakeConversation:
        def __init__(self, **kwargs):
            pass
        def use_skill(self, name, text=''):
            staged.append(name)
        def close(self):
            pass

    import opengeode.OrbitChatPanel as panel
    from opengeode.OrbitChatPanel import MODE_MCP
    monkeypatched = pytest.MonkeyPatch()
    monkeypatched.setattr(panel, 'Conversation', FakeConversation)
    monkeypatched.setattr(panel, '_stage_skill',
                          lambda chat, mode=None: True)
    monkeypatched.setattr(panel, '_publish_reference_skill',
                          lambda d: published.append(d) or True)
    try:
        import os
        agent = OrbitAgent()
        model_dir = str(tmp_path / "model")
        os.makedirs(model_dir)
        agent.start(cwd=model_dir, briefing='', mode=MODE_MCP)
        import time
        deadline = time.time() + 10
        while not published and time.time() < deadline:
            time.sleep(0.01)
        # The publish received the CONVERSATION's cwd — the model dir —
        # (the old code crashed here with AttributeError).
        assert published == [model_dir], (
                'the reference must be published to the conversation cwd, '
                'got: %r' % (published,))
        agent.stop()
    finally:
        monkeypatched.undo()


def test_eventfilter_modifier_combo_is_a_flag_or():
    '''Regression: `modifiers() & (Qt.ShiftModifier, Qt.ControlModifier)`
    raised TypeError ("KeyboardModifier and tuple") on every key press
    in the chat entry, breaking the chat panel. The mask must be a
    flag OR, not a tuple.'''
    import os
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt, QEvent
    from PySide6.QtGui import QKeyEvent
    from opengeode.OrbitChatPanel import OrbitChatPanel

    app = QApplication.instance() or QApplication([])
    from PySide6.QtWidgets import QMainWindow

    window = QMainWindow()
    panel = OrbitChatPanel(window)
    window.show()
    panel.show()
    app.processEvents()

    def key(key_, mod):
        return QKeyEvent(QEvent.KeyPress, key_, mod)

    # Plain Return must be consumed and must not raise.
    assert panel.eventFilter(panel.entry,
                             key(Qt.Key_Return, Qt.NoModifier)) is True
    # Shift+Return and Ctrl+Return fall through to insert a newline.
    assert panel.eventFilter(panel.entry,
                             key(Qt.Key_Return, Qt.ShiftModifier)) is False
    assert panel.eventFilter(panel.entry,
                             key(Qt.Key_Return, Qt.ControlModifier)) is False
    # Any other key is untouched.
    assert panel.eventFilter(panel.entry,
                             key(Qt.Key_A, Qt.NoModifier)) is False

    panel.hide()
    window.hide()


def test_mode_toggle_selects_one_skill_and_the_right_env():
    '''The editing mode the panel offers: MCP mode stages ONLY the
    remote-control skill and announces the bridge socket; file mode
    stages ONLY the SDL reference and announces nothing — orbit must
    not route tool calls into the editor in file mode. Switching
    rebuilds the conversation so the choice applies from the first
    prompt.'''
    import opengeode.OrbitChatPanel as panel
    from opengeode.OrbitChatPanel import (MODE_FILE, MODE_MCP,
                                          SKILLS_PER_MODE)

    # File mode stages the full SDL reference (the agent edits files
    # directly). MCP mode stages ONLY the compact tool skill; the full
    # reference is published to the model dir's .orbit/skills/ and
    # loaded ON DEMAND with skill(name=...).
    file_skills = SKILLS_PER_MODE[MODE_FILE]
    mcp_skills = SKILLS_PER_MODE[MODE_MCP]
    assert [n for n, _ in file_skills] == ["sdl-model-construction"]
    assert [n for n, _ in mcp_skills] == ["sdl-mcp-remote-control"]

    # _stage_skill stages the mode's skill only
    class FakeChat:
        def __init__(self):
            self.staged = []
        def use_skill(self, name, text=""):
            if not text:
                raise ValueError("a client skill needs text")
            self.staged.append(name)
            return True
    chat = FakeChat()
    assert panel._stage_skill(chat, MODE_FILE) is True
    assert chat.staged == ["sdl-model-construction"]
    chat2 = FakeChat()
    assert panel._stage_skill(chat2, MODE_MCP) is True
    assert chat2.staged == ["sdl-mcp-remote-control"]


def test_mode_toggle_in_a_real_panel():
    '''The toggle on the real panel: switching mode clears or restores
    the bridge env on the new conversation's agent, and each mode
    stages its own skill. Drives the panel with the fake orbit agent.'''
    import os
    os.environ.setdefault('ORBIT_ACP_AGENT',
                          'python3 -m orbit_acp.testing.fake_agent')
    import opengeode.OrbitChatPanel as panel
    from opengeode.OrbitChatPanel import MODE_MCP
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QTimer
    from PySide6.QtUiTools import QUiLoader
    app = QApplication.instance() or QApplication([])
    from opengeode.opengeode import OG_MainWindow, SDL_View, parse_args
    repo = os.path.dirname(os.path.dirname(os.path.abspath(
        panel.__file__)))
    loader = QUiLoader()
    loader.registerCustomWidget(OG_MainWindow)
    loader.registerCustomWidget(SDL_View)
    mw = loader.load(os.path.join(repo, 'opengeode.ui'))
    import sys
    old_argv = sys.argv[:]
    sys.argv = ['opengeode', '--edit']
    options = parse_args()
    sys.argv = old_argv
    mw.start(options, None, app)
    p = mw.orbit_chat_panel

    # The mode button sits ABOVE the chat view (a mode selector
    # configures the conversation, so it belongs at the top).
    def _find(lay, target):
        for i in range(lay.count()):
            item = lay.itemAt(i)
            if item.widget() is target:
                return i
            sub = item.layout()
            if sub is not None:
                j = _find(sub, target)
                if j is not None:
                    return (i, j)
        return None
    btn_pos = _find(p.layout(), p.mode_btn)
    view_pos = _find(p.layout(), p.view)
    assert isinstance(btn_pos, tuple), "mode button not in the top row"
    assert isinstance(view_pos, int), "chat view not a top-level row"
    assert btn_pos[0] < view_pos, "mode button must be above the chat"

    results = {}
    def step1():
        results['default'] = p._mode
        results['default_env'] = p._agent._env is not None
        p._toggle_mode()          # -> file
        QTimer.singleShot(1500, step2)
    def step2():
        results['file_env'] = p._agent._env is None
        results['file_skill'] = getattr(p._agent, 'skill_staged', None)
        p._toggle_mode()          # -> mcp
        QTimer.singleShot(1500, step3)
    def step3():
        results['mcp_env'] = p._agent._env is not None
        results['mcp_skill'] = getattr(p._agent, 'skill_staged', None)
        p._agent.stop(delete_session=True)
        results['done'] = True
        app.quit()
    QTimer.singleShot(1500, step1)
    QTimer.singleShot(20000, app.quit)   # hard stop
    app.exec()

    assert results['default'] == MODE_MCP
    assert results['default_env'] is True
    assert results['file_env'] is True, "file mode must clear the bridge env"
    assert results['file_skill'] is True
    assert results['mcp_env'] is True, "mcp mode must announce the bridge"
    assert results['mcp_skill'] is True
