"""
This module contains Filesystem class, which functions as an
adapter to either connect to 3rd party storage servers like Amazon S3
or use local filesystem.
"""
from contextlib import contextmanager
import boto3
import io
import os, errno
import ConfigParser
from zipfile import ZipFile
import mimetypes

class Filesystem():
    """Filesystem class
    """
    def __init__(self, connect_to=None, config_file=None, bucket_name=None, rootdir='', tmpdir='tmp'):
        """Initialize Filesystem instance.

        Args:
            connect_to(str|None): If None, use local filesystem, Other values: 'aws-s3'
            config_file: If exists, will be passed to storage interface, otherwise use environment
                         variables.
            bucket_name(str|None): Bucket name in remote storage.
            rootdir(str): Root directory in remote storage.
            tmpdir(str): Directory location where files from remote storage will be temporarily stored.
                         Name of file stored will be its md5. Directory is cleaned up periodically and in
                         each build.
        """
        self.s3 = None
        self.connect_to = connect_to
        self.rootdir = rootdir
        self.tmpdir = tmpdir
        if connect_to == 'aws-s3':
            if config_file != None:
                os.environ['AWS_CONFIG_FILE'] = config_file
                os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file
            self.s3 = boto3.resource('s3')
            self.bucket = self.s3.Bucket(bucket_name)

    @contextmanager
    def get_path(self, path="", base_dir=""):
        """Get either a path or io.BytesIO instance.

        The following code shows an example where we get a zip file from storage
        and print the names listed in that zip file.
        To run this test, create 'awsconfig' file in the same
        directory with this module and make sure bucket_name and rootdir are correct
        and the zip file exists there. Zip file should contain a file named "test.txt".

        >>> path = os.path.join(base_path, 'awsconfig')
        >>> tmpdir = os.path.join(base_path, 'tmp')
        >>> bucket_name = 'arthur-storage'
        >>> rootdir = 'workspace'
        >>> fs = Filesystem(connect_to='aws-s3', bucket_name=bucket_name, rootdir=rootdir,
        ...                 config_file=path, tmpdir=tmpdir)
        >>> with fs.get_path('test.zip') as path:
        ...     with ZipFile(path, 'r') as zipfile:
        ...         for zipinfo in zipfile.infolist():
        ...             print zipinfo.filename
        test.txt

        Args:
            path(string): An absolute path that will be converted or used.
            base_dir(string): Absolute path pointing to the base directory to be removed from
                              path when used to connect to remote storage. e.g.
                              if the app path is `/media/disk/app/` and path is `/media/disk/app/storage/file.txt`
                              then it is expected that remote storage's path should be `storage/file.txt`.

        Returns:
            string: Path usable in both local and remote scenarios.
        """
        if self.s3 != None:
            s3path = self.key_from_path(path, base_dir)
            obj = self.bucket.Object(key=s3path)
            try:
                os.makedirs(self.tmpdir)
            except OSError, e:
                if e.errno != errno.EEXIST:
                    raise
            md5 = obj.get()['ETag'].replace('"', '')
            ext = mimetypes.guess_extension(obj.get()['ContentType'])
            filename = "%s%s" % (md5,ext)
            localpath = os.path.join(self.tmpdir, filename)
            if not os.path.exists(localpath):
                self.bucket.download_file(s3path, localpath)
            yield localpath
        else:
            yield path

    def key_from_path(self, path="", base_dir=""):
        """Turn path into key to use in 3rd party storage.

        Currently this is as simple as removing base dir from path, then
        prefixing it with rootdir value.

        Args:
            path(string): Path to be converted into key.
            base_dir(string): Base directory path to be removed from path.
        Returns:
            string: Key version of given path.
        """
        path = path.replace(base_dir, '')
        if path[0] == os.path.sep:
            path = path[1:]
        return os.path.join(self.rootdir, path)

if __name__ == '__main__':
    import doctest
    import pdb
    import os, sys, inspect
    # base_path points to current directory.
    base_path = os.path.realpath(
        os.path.abspath(
            os.path.join(
                os.path.split(
                    inspect.getfile(
                        inspect.currentframe()
                    )
                )[0]
            )
        )
    )
    doctest.testmod()