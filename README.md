# PythonApplication1

This is a simple file management system coded in Python. 

This is a very simple disk operating system called TinyDOS which provides the ability to store and retrieve data on a virtual drive.

The following commands are supported:

- `format volumeName`
Creates an ordinary file called volumeName and fills it in as a newly formatted TinyDOS volume. The real file will be 66944 bytes long.

- `ls fullDirectoryPathname`
Lists the contents of the directory specified by fullDirectoryPathname. All pathnames of files and directories for TinyDOS should be fully qualified.

- `mkfile fullFilePathname`
Makes a file with the pathname fullFilePathname. Any directories in the path should already exist.

- `mkdir fullDirectoryPathname`
Makes a directory with the pathname fullDirectoryPathname. Any directories in the path should already exist.

- `append fullFilePathname "data"`
Writes all of the data between the double quotes to the end of the file called fullFilePathname. The file must already exist. Double quotes will not appear inside the data.

- `print fullFilePathname`
Prints all of the data from the file called fullFilePathname to the screen. The file must already exist.

- `delfile fullFilePathname`
Deletes the file called fullFilePathname. The file must already exist.

- `deldir fullDirectoryPathname`
Deletes the directory called fullDirectoryPathname. The directory must already exist and the directory must be empty.

- `quit`
The TinyDOS program quits.
