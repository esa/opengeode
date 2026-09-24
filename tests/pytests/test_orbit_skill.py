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


def test_both_bundled_skills_are_staged():
    '''The panel hands orbit every skill it ships: the SDL construction
    reference and the MCP remote-control interface. Each is staged
    under its own name with its own body.'''
    import opengeode.OrbitChatPanel as panel
    calls = []

    class Chat:
        def use_skill(self, name, text=''):
            calls.append((name, text))
            return True
    assert panel._stage_skill(Chat()) is True
    names = [name for name, _ in calls]
    assert panel.SKILL_NAME in names
    assert panel.MCP_SKILL_NAME in names
    # Each body carries its own skill's content, frontmatter stripped.
    bodies = {name: text for name, text in calls}
    assert bodies[panel.MCP_SKILL_NAME].startswith('# OpenGEODE SDL Remote Control')
    assert not bodies[panel.MCP_SKILL_NAME].startswith('---')


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
                          lambda chat: staged.append(('staged', chat)) or True)
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
