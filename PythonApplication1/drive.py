'''
Modified on 28/08/2016
The underlying Drive class which actually stores all data in a real text file.
@author: robert
'''

import os

class Drive:
    '''
    A drive. Represented as an ordinary text file on disk.
    '''

    BLK_SIZE = 512      # number of bytes in a block
    DRIVE_SIZE = 128   # number of blocks in a server
    EMPTY_BLK = ' ' * BLK_SIZE
    SEPARATOR = '\n**     **\n'

    def __init__(self, name):
        '''Create a Drive object.
        
        name - the name of the real file which stores this Drive on the disk
        '''
        self.name = name
     
    def format(self):
        '''Equivalent of a low-level format.
        Associate a drive object with its underlying real file.
        Write the block information, including block separators, to this file.
        '''
        self.file = open(self.name, mode='w+')
        for n in range(Drive.DRIVE_SIZE):
            separator = Drive.SEPARATOR[:3] + str(n).rjust(4) + Drive.SEPARATOR[7:]
            self.file.write(Drive.EMPTY_BLK + separator)
    
    def reconnect(self):
        '''Reconnect an existing real file as a Drive object.'''
        if not os.path.exists(self.name):
            raise IOError('file does not exist')
        self.file = open(self.name, mode='r+')
    
    def disconnect(self):
        '''Shut the underlying real file down.'''
        self.file.close()
    
    def write_block(self, n, data):
        '''Write "data" to block "n" of the drive.'''
        if n < 0 or n >= Drive.DRIVE_SIZE:
            raise IOError('block out of range')
        if len(data) != Drive.BLK_SIZE:
            raise ValueError('data not block size')
        self.file.seek(n * (Drive.BLK_SIZE + len(Drive.SEPARATOR)))
        written = self.file.write(data)
        self.file.flush()
        if written != Drive.BLK_SIZE:
            raise IOError('incomplete block write')
        
    def read_block(self, n):
        '''Read and return block "n" from the drive.'''
        if n < 0 or n >= Drive.DRIVE_SIZE:
            raise IOError('block out of range')
        self.file.seek(n * (Drive.BLK_SIZE + len(Drive.SEPARATOR)))
        data = self.file.read(Drive.BLK_SIZE)
        if len(data) != Drive.BLK_SIZE:
            raise IOError('incomplete block read')
        return data