Python Files

| File             | Description                                                  |
| ---------------- | ------------------------------------------------------------ |
| single_bgauto.py | Checks for new video files on dropbox, gets files, generates summarization jpg. |
| dbxlib_notoken.py        | Library of fuctions that use the dropbox api to list directories, get a file, store a file, and delete a file. |
| createhtml.py    | Scans video and image directories and generates html for the flask server. |
| imagelist.py     | Flask server code.                                           |

Note that the dbxlib.py file does not contain my dropbox TOKEN for my dropbox app.  You will either need to modify the code to use a file system that contains the video files or create your own dropbox app.
