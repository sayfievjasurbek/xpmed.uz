"""Load the existing translation finalizer without duplicating its validation."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('xpmed_translation',Path(__file__).with_name('finalize-translation.py'))
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
finalize_translation=module.finalize
