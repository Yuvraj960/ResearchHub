"""
Python 3.12 compatibility shim.

passlib 1.7.x imports `pkg_resources` which was removed from Python 3.12's
default namespace. This module installs a minimal shim before any Flask-Security
or passlib imports happen.

Import this module FIRST in run.py and celery_worker.py.
"""
import sys

try:
    import pkg_resources  # noqa: F401 – already available, nothing to do
except ModuleNotFoundError:
    import importlib.metadata as _meta
    import types

    _pkg = types.ModuleType("pkg_resources")

    def _get_distribution(name):
        try:
            return _meta.distribution(name)
        except _meta.PackageNotFoundError as exc:
            raise _DistributionNotFound(name) from exc

    class _DistributionNotFound(Exception):
        pass

    _pkg.get_distribution = _get_distribution
    _pkg.DistributionNotFound = _DistributionNotFound
    _pkg.require = lambda *a, **kw: None
    sys.modules["pkg_resources"] = _pkg
