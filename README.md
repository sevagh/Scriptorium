# Scriptorium

Scriptorium target Python 3.7 (mypy and OpenCV weren't ready for 3.8 when I wrote this).

Scriptorium is a (early alpha quality) demo of an OCR-based reading assistant. I got the idea from being hunched over books with a dictionary open, flipping through pages of my notebook to find out if I encountered a word previously, what pages the previous appearances were on, etc.

Scriptorium is meant to accompany my paper dictionary and pen-and-notebook reading methods, and not to replace them. More in the usage section below.

### Setup

[DAWG](https://github.com/pytries/DAWG) must be installed from source. Everything else is covered by setup.py and `requirements*.txt`.

Quick setup guide, assuming the user has a Python 3.7 virtualenv created and activated:

```
$ git clone https://github.com/pytries/DAWG && cd DAWG/ && pip install -e . && cd ../
$ git clone https://github.com/sevagh/Scriptorium && cd Scriptorium && make init && cd ../
```

You can now launch `Scriptorium` from your virtualenv. The other make targets are only relevant to developers (run `make dev_init` to install dev dependencies). Code is formatted with black. The pylint target exists but I'm not fully committed to it yet. The important targets are test and mpypy.

### Usage
