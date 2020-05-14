#
# Copyright https://github.com/norm42/summerize_video/blob/master/LICENSE.md
# (Mit license)
#
import sys
import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError

# Add OAuth2 access token here.
# You can generate one for yourself in the App Console.
# See <https://blogs.dropbox.com/developers/2014/05/generate-an-access-token-for-your-own-account/>
dbx_token_dict = {'app': 'variam',
                  'dbxtoken': 'T_QBLMuCRfIAAAAAAAAnG8FL1rxgUL_GvVjrE1xj4QLaF45_YLaDACd4nzAstZln'}
TOKEN = 'T_QBLMuCRfIAAAAAAAAnG8FL1rxgUL_GvVjrE1xj4QLaF45_YLaDACd4nzAstZln'


#
#  ToDo:  
# 1. AES decrypt the token return the token
# 2. Error checking
# 3. Make an encrypt utility
# 4. See if we can get meta data on a file vs the directory
def dbx_open(appname):
    dbx = dropbox.Dropbox(TOKEN)

    # Check that the access token is valid
    try:
        dbx.users_get_current_account()
    except AuthError:
        sys.exit("ERROR: Invalid access token; try re-generating an "
                 "access token from the app console on the web.")
    return (dbx)


def dbx_check(dbx):
    # Check that the access token is valid
    try:
        dbx.users_get_current_account()
    except:
        return (False)
    else:
        return (True)


def bugdbx_open(appname):  # another time
    print("try ", appname)
    for app, dbxtoken in dbx_token_dict.items():
        print(type(app), type(appname))
        print(app, dbxtoken)
        print(app == appname)
        if (app == appname):
            print("opening app ", appname, " with ", dbxtoken)
            dbx = dropbox.Dropbox(TOKEN)

            # Check that the access token is valid
            try:
                dbx.users_get_current_account()
            except AuthError:
                sys.exit("ERROR: Invalid access token; try re-generating an "
                         "access token from the app console on the web.")
            return (dbx)
    return (None)


def dbx_upload(dbx, srcfname, dbx_destname, binfile):
    mode = 'r'  # text file
    if binfile:
        mode = 'rb'  # binary

    with open(srcfname, mode) as f:
        print("Uploading " + srcfname + " to Dropbox as " + dbx_destname + "...")
        try:
            dbx.files_upload(f.read(), dbx_destname, mode=WriteMode('overwrite'))
        except ApiError as err:
            # This checks for the specific error where a user doesn't have
            # enough Dropbox space quota to upload this file
            if (err.error.is_path() and
                    err.error.get_path().reason.is_insufficient_space()):
                sys.exit("ERROR: Cannot back up; insufficient space.")
            elif err.user_message_text:
                print(err.user_message_text)
                sys.exit()
            else:
                print(err)
                sys.exit()

    return (True)


def dbx_download(dbx, dbx_srcname, dstname, binfile):
    # Download the specific revision of the file at BACKUPPATH to LOCALFILE
    print("Downloading " + dbx_srcname + " from Dropbox " + dstname + "...")
    dbx.files_download_to_file(dstname, dbx_srcname, rev=None)
    return (True)


def dbx_getdirlist(dbx, dbx_path):
    idx = 1
    vids = {}
    response = dbx.files_list_folder(path=dbx_path)
    for file in response.entries:
        vids[idx] = {'name': file.name, 'size': file.size, 'server_mod': file.server_modified}
        idx = idx + 1
    return (vids)


def dbx_getmeta(dbx, dbx_file):
    # TBD
    return (True)


def dbx_deletefile(dbx, dbx_file_path):
    print("Deleting " + dbx_file_path)
    response = dbx.files_delete_v2(dbx_file_path)
    return (response)
