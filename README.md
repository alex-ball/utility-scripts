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
    the command line. (NB. assumes you have the `rm` command for deleting a
    temporary file.)
