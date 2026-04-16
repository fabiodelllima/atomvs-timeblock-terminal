"""E2E snapshot testing configuration.

Custom snap_compare fixture using syrupy 5.x + Textual's pilot API,
replacing the legacy pytest-textual-snapshot dependency.

The fixture preserves the same interface used by all existing tests:
    assert snap_compare(app, terminal_size=(...), run_before=callback)
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

import pytest
from syrupy.extensions.single_file import SingleFileSnapshotExtension

if TYPE_CHECKING:
    from collections.abc import Callable

    from syrupy.assertion import SnapshotAssertion
    from syrupy.types import SerializableData, SerializedData
    from textual.app import App


class SVGSnapshotExtension(SingleFileSnapshotExtension):
    """Syrupy extension that stores snapshots as individual .svg files.

    Overrides serialize to accept str from Textual's export_screenshot(),
    since SingleFileSnapshotExtension expects bytes by default.
    """

    _file_extension = "svg"

    def serialize(
        self,
        data: SerializableData,
        *,
        exclude: Any = None,
        include: Any = None,
        matcher: Any = None,
    ) -> SerializedData:
        """Encode SVG string to bytes for single-file storage."""
        if isinstance(data, str):
            return data.encode("utf-8")
        return super().serialize(data, exclude=exclude, include=include, matcher=matcher)


@pytest.fixture
def snapshot(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    """Configure syrupy to use SVG single-file snapshots."""
    return snapshot.use_extension(SVGSnapshotExtension)


@pytest.fixture
def snap_compare(snapshot: SnapshotAssertion):
    """Drop-in replacement for pytest-textual-snapshot's snap_compare.

    Uses Textual's App.run_test() + export_screenshot() with syrupy
    for snapshot comparison. Maintains identical call signature.
    """

    def _compare(
        app: App,
        *,
        terminal_size: tuple[int, int] = (80, 24),
        run_before: Callable | None = None,
    ) -> bool:
        async def _capture() -> str:
            async with app.run_test(size=terminal_size) as pilot:
                if run_before is not None:
                    await run_before(pilot)
                return app.export_screenshot()

        svg = asyncio.run(_capture())
        assert svg == snapshot
        return True

    return _compare
