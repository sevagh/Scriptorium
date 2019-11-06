# Scriptorium

Very early demo. README is Fedora 30-centric, and French-to-English centric (as that is my use case).

I target Python 3.7. Note that I use asyncio, not because I want to, but because [wordbook](https://github.com/tomplus/wordbook) forces me to.

### Dictionary setup

```
$ sudo dnf install dictd
```

On Fedora 30, dictd uses dict.org by default:

```
sevagh:Scriptorium $ dict -D | grep 'eng-fra\|fra-eng'
 fd-fra-eng     French-English FreeDict Dictionary ver. 0.3.4
 fd-eng-fra     English-French FreeDict Dictionary ver. 0.1.4
```

You can set up your local dictionaries with:

```
$ sudo dnf install dictd-server
$ sudo systemctl enable --now dictd
```
