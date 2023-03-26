'''
Inspired by :
https://gist.github.com/Jwely/ad8eb800bacef9e34dd775f9b3aad987

TODO : add python regex to only download file with specific pattern
'''
import os
import ftplib
from pathlib import Path
import atexit
class RecursiveFtp():
    '''
    Class to download files recursively from FTP server
    '''
    def __init__(self, hostname, port, username, password, output_root):
        self._output_root = output_root
        self._list_dir = ['/']
        self._list_file = []
        self._ftp = ftplib.FTP()
        self._ftp.connect(hostname, port)
        self._ftp.login(username, password)

        # This will recursively apply to all subdir because list_dir kept getting appended
        for dir in self._list_dir:
            self._append_list(dir, self._ftp.nlst(dir))

        self._list_dir= self._remove_duplicates(self._list_dir)
        self._list_file = self._remove_duplicates(self._list_file)
        # print('list_dir:')
        # print(self._list_dir)
        # print('list_file:')
        # print(self._list_file)

        atexit.register(self.cleanup)

    def _append_list(self, relative_path, list_obj):
        '''
        Recursively create a list of directories and files
        @param relative_path : relative path
        '''
        for obj in list_obj:
            new_path = relative_path + '/' + obj
            print('new path : '+ new_path)
            try:
                self._ftp.cwd(new_path)
                self._list_dir.append(new_path)
            except Exception as e: # ftplib.error_perm
                print(e)
                self._list_file.append(new_path)
                continue
            self._ftp.cwd('..')

    def _remove_duplicates(self, myList):
        # Remove duplicates
        myList = list(set(myList))
        # Remove extra '//'
        newList = []
        for data in myList:
            new_data = data.replace('//', '')
            newList.append(new_data)
        return newList

    def _make_dir_tree(self, output_root):
        """ 
        Create new local dir tree 
        @param output_root output dir (relative path)
        """
        # Get absolute path of the output folder
        outputPath = Path.joinpath(Path(os.getcwd()), output_root)
        # Create dir tree
        for fpath in self._list_dir:
            newPath = Path.joinpath(Path(outputPath), fpath)
            # print("\nnewPath: "+ str(newPath))
            if (not os.path.exists(newPath)):
                try:
                    os.makedirs(newPath)
                    print("created {0}".format(newPath))
                except OSError as e:
                    print(e)

    def download_files(self, output_root, overwrite = True):
        # Create dir tree first
        self._make_dir_tree(output_root)
        # Start downloading files
        for file in self._list_file:
            name = '/' + file
            dest = output_root + name          # relative path
            if not os.path.exists(dest) or overwrite is True:
                try:
                    with open(dest, 'wb') as f:
                        self._ftp.retrbinary("RETR {0}".format(name), f.write)
                    print("downloaded: {0}".format(dest))
                except FileNotFoundError:
                    print("FAILED: {0}".format(dest))
            else:
                print("already exists: {0}".format(dest))

    def cleanup(self):
        self._ftp.quit()


if __name__ == "__main__":
    HOSTNAME = "localhost"
    USERNAME = "someUser"
    PASSWORD = "somePassword"
    PORT = 2121
    output_root = './download_ftp'

    recursiveFtp = RecursiveFtp(HOSTNAME, PORT, USERNAME, PASSWORD, output_root)
    recursiveFtp.download_files(output_root)

    print('End of program')

