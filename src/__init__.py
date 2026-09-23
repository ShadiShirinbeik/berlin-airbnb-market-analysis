"""Reusable analysis code for the Berlin Airbnb project.

Notebooks import from here; nothing analytical lives in a notebook cell that
could not be tested. Usage inside a notebook:

    import sys; sys.path.append("..")
    from src import config as cfg, cleaning, stats_utils as st, viz
"""
__version__ = "1.0.0"
