pip install ..
sphinx-apidoc -P -f -o source/ ../tourcalc/ --ext-autodoc --separate --module-first
sphinx-build -b html source build
