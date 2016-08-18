# utility-scripts

A collection of command-line scripts that make my life easier:

  * **odt-meta-fix:** Add or modify author metadata of ODT file

    It is transparently easy to edit author metadata in Microsoft Word but
    tediously hard to do so in LibreOffice. (You can replace that information
    with whatever is entered in your User Data, but that makes it rather awkward
    to have more than one author or to edit a document someone else has
    written.) I come across this a lot as I often have to turn other people's
    documents into PDF, and author information is rather prominently displayed
    in the PDF metadata. This Python script lets you edit the author metadata on
    the command line.

  * **pdfposter2thm:** Convert a folder of PDFs into JPEGs

    This Bash script was designed for creating thumbnail images of PDF posters.
    It runs through all the PDFs in the current working directory and converts
    them to JPEG bitmaps using ImageMagick, saving the result in a `thumbnails`
    subdirectory. Any page with a 1-to-sqrt(2) aspect ratio (like, say, A4) will
    be scaled to a 495×350 px image, and all other images will have a similar
    area.

    I had hoped to do this transparently in pixels per centimetre, given that
    the ISO page sizes are rounded to the nearest millimetre, but alas on my
    system at least the ImageMagick option `-units PixelsPerCentimeter` seems
    utterly ineffective. Hence it reports its progress in inches (sigh).

  * **get-audio:** Download audio content to chronological queues

    I wrote this Python 3 script to fill a particular need I have. Unlike
    everyone else, it seems, I find it most convenient to download all the
    podcasts to which I listen to a single queue and listen to them in strict
    chronological order. This script downloads them, renames them with the date
    and time of release at the start (so they sort correctly) and evens out the
    levels. As well as downloading podcasts, it can also download BBC radio
    programmes and add them to the queue. For programmes that are best listened
    to in a block rather than strict chronological order, the script supports
    an 'audiobook' queue; unfortunately it is not yet clever enough to date the
    the individual audiobook folders so you have to do that manually when you
    think the folder is full enough.

    The script has become quite complicated, so as well as the standard Python
    libraries it also relies on

      * the non-standard libraries [`requests`](http://docs.python-requests.org/),
        [`dateutil`](https://dateutil.readthedocs.org/),
        [`clint`](https://pypi.python.org/pypi/clint/) and
        [`blist`](https://pypi.python.org/pypi/blist/);
      * [`mp3gain`](http://mp3gain.sourceforge.net/),
        [`aacgain`](http://aacgain.altosdesign.com/) and
        [`vorbisgain`](https://sjeng.org/vorbisgain.html);
      * [`get_iplayer`](http://www.infradead.org/get_iplayer/html/get_iplayer.html).

  * **fix-atom-spellcheck:** Add system spellcheck dictionaries to Atom editor

    The [Atom editor](https://atom.io/) spell checker responds to the system
    language, but on Linux systems only looks at the dictionaries that it ships
    with, i.e. American English. This script adds the system's dictionaries to
    Atom's dictionary folder. It was worth scripting since this must be redone
    every time the software gets updated.
