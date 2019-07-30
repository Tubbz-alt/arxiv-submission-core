"""Filesystem shim app configuration."""

import os
import tempfile

LEGACY_FILESYSTEM_ROOT = os.environ.get('LEGACY_FILESYSTEM_ROOT')
if LEGACY_FILESYSTEM_ROOT is None:
    LEGACY_FILESYSTEM_ROOT = tempfile.mkdtemp()

LEGACY_FILESYSTEM_SOURCE_DIR_MODE = \
    int(os.environ.get('LEGACY_FILESYSTEM_SOURCE_DIR_MODE', 0o42775))
LEGACY_FILESYSTEM_SOURCE_MODE = \
    int(os.environ.get('LEGACY_FILESYSTEM_SOURCE_MODE', 0o42775))

LEGACY_FILESYSTEM_SOURCE_UID = \
    int(os.environ.get('LEGACY_FILESYSTEM_SOURCE_UID', os.geteuid()))
LEGACY_FILESYSTEM_SOURCE_GID = \
    int(os.environ.get('LEGACY_FILESYSTEM_SOURCE_GID', os.getegid()))
LEGACY_FILESYSTEM_SOURCE_PREFIX = 'src'