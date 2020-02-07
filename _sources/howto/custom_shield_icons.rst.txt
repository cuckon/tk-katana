Make custom shields
===================

Most of the shields used in our landing pages are generated on
http://img.shields.io

Simply copying, pasting and editing the URL will generate new shields so
for the most part, making new "simple" shields are easy. Just remember to do
URL character substitution for spaces/special characters.

e.g. I want to make a "foo", "bar far away" shield!

1. Start with the "badge" URL https://img.shields.io/badge/
2. Add "foo" https://img.shields.io/badge/foo
3. Add "-" to separate the label from the message https://img.shields.io/badge/foo-
4. Add "bar far away", replacing spaces with "%20" https://img.shields.io/badge/foo-bar%20far%20away
5. Add "-" to separate the message from the color https://img.shields.io/badge/foo-bar%20far%20away-
6. Add the badge color (see https://img.shields.io) https://img.shields.io/badge/foo-bar%20far%20away-red
7. Finish off with ".svg" at the end https://img.shields.io/badge/foo-bar%20far%20away-red.svg

.. image:: https://img.shields.io/badge/foo-bar%20far%20away-red.svg


Custom Icons
------------

Although http://img.shields.io mentions:

    ``?logo=data:image/png;base64,…`` Insert custom logo image (≥ 14px high)

    -- http://img.shields.io under Styles

It doesn't actually tell you how to generate the … (base64 data).

We'll use our Katana logo png at the root of our repository as an example.

1. Generate the base64 **encoded** version of the icon binary data

   You can do this in Linux terminal by running ``base64`` with the file

   - ``-w 0`` to not wrap lines/words
   - ``echo`` to make things look nicer (places prompt in new line)

   .. code-block:: bash

        # While at the root of the repository
        base64 -w 0 icon_64.png; echo

   This should output a **massive line** of URL friendly, encoded text.

   There are also websites online that can generate ``base64`` encoded
   text for files/binary data (google it!).

2. Create a badge URL, e.g. https://img.shields.io/badge/foo-bar%20far%20away-red.svg

   See above example.

3. Add ``?logo=data:image/png;base64,`` and then the massive line of encoded
   text to it, resulting in something like:

   .. code-block:: text

        https://img.shields.io/badge/foo-bar%20far%20away-red.svg?logo=data:image/png;base64,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


Resulting in something like:

.. image:: https://img.shields.io/badge/foo-bar%20far%20away-red.svg?logo=data:image/png;base64,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
