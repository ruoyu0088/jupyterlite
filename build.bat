jupyter lite build --contents content --output-dir dist --pyodide pyodide.tar.bz2
python utils.py patch
copy /y patch\568.01d8de54f0240b4168bd.js dist\extensions\jupyterlab-open-url-parameter\static\
python fix_content.py