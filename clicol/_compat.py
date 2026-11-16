"""Resource and entry point loading across supported Python versions."""

from io import StringIO
from pkgutil import get_data

try:
    from importlib import metadata
except ImportError:  # Python < 3.8
    import importlib_metadata as metadata


def read_config_resource(config, resource):
    """Read a bundled UTF-8 INI file without requiring a filesystem path."""
    try:
        data = get_data('clicol', resource)
    except OSError:
        # Match ConfigParser.read's handling of missing files.
        return
    if data is not None:
        with StringIO(data.decode('utf-8')) as stream:
            config.read_file(stream, source=resource)


def iter_entry_points(group):
    """Support both the original mapping API and selectable entry points."""
    points = metadata.entry_points()
    if hasattr(points, 'select'):
        return iter(points.select(group=group))
    return iter(points.get(group, ()))
