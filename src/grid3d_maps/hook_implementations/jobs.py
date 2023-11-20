import importlib
import os
import sys
from pathlib import Path

try:
    from ert.shared.plugins.plugin_manager import hook_implementation
    from ert.shared.plugins.plugin_response import plugin_response
except ModuleNotFoundError:
    from ert_shared.plugins.plugin_manager import hook_implementation
    from ert_shared.plugins.plugin_response import plugin_response

PLUGIN_NAME = "grid3d_maps"


def _get_jobs_from_directory(directory):
    resource_directory = Path(sys.modules[PLUGIN_NAME].__file__).parent / directory

    all_files = [
        os.path.join(resource_directory, f)
        for f in os.listdir(resource_directory)
        if os.path.isfile(os.path.join(resource_directory, f))
    ]
    return {os.path.basename(path): path for path in all_files}


@hook_implementation
@plugin_response(plugin_name=PLUGIN_NAME)
def installable_jobs():
    return _get_jobs_from_directory("config_jobs")


@hook_implementation
@plugin_response(plugin_name=PLUGIN_NAME)
def installable_workflow_jobs():
    return {}


def _get_module_if_exists(module_name):
    try:
        script_module = importlib.import_module(module_name)
    except ImportError:
        return None
    return script_module


@hook_implementation
@plugin_response(plugin_name=PLUGIN_NAME)
def job_documentation(job_name):
    subscript_jobs = set(installable_jobs().data.keys())
    if job_name not in subscript_jobs:
        return None

    for sm in ["avghc", "aggregate"]:
        module_name = f"{PLUGIN_NAME}.{sm}.{job_name.lower()}"
        module = _get_module_if_exists(module_name)
        if module is not None:
            print(module_name)
            return {
                "description": getattr(module, "DESCRIPTION", ""),
                "examples": getattr(module, "EXAMPLES", ""),
                "category": getattr(module, "CATEGORY", "other"),
            }
    return None
