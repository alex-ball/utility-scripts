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
