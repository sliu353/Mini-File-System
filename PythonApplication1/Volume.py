from drive import Drive

availableBlockIndices = list(range(1, 128))
BITMAP_SIZE = 128
FILE_INFO_SIZE = 64
ROOT_FILE_MAX_INDEX = 5
FILE_MAX_INDEX = 7
FILE_TYPE_LENGTH = 2
FILE_NAME_LENGTH = 9
FILE_LENGTH = 4
BLOCK_SIZE = 512

availableBlocksList = ['+'] + ['-' for x in range(127)]

class Volume:
    
    def __init__(self):
        self.currentDrive = None
        self.rootDirectory = None  
        self.blocksAvailability = None      

    def format(self, name):
        thisDrive = Drive(name)
        thisDrive.format()
        thisDrive.write_block(0, "+" + "-" * 127 + ("f:" + " " * 9 + "0000:" + "000 " * 12) * 6)
        global availableBlocksList
        availableBlocksList = ['+'] + ['-' for x in range(127)]
        global availableBlockIndices 
        availableBlockIndices = list(range(1, 128))
        self.currentDrive = thisDrive
        self.rootDirectory = Directory(self.currentDrive, None, 0, None, None) #drive, fileNum, parentBlockNum, parent, name
        self.blocksAvailability = thisDrive.read_block(0)[:127]

    def mkfile(self, path):
        nodes = path.strip('/').split('/')
        lastNode = self.rootDirectory
        for node in nodes[:-1]:
            lastNode = lastNode.getChild(node)
        lastNode.addFile(nodes[-1])

    def mkdir(self, path):
        nodes = path.strip('/').split('/')
        lastNode = self.rootDirectory
        for node in nodes[:-1]:
            lastNode = lastNode.getChild(node)
        lastNode.addDirectory(nodes[-1])

    def reconnect(self, name):
        self.currentDrive = Drive(name)
        self.rootDirectory = Directory(self.currentDrive, None, 0, None, name)
        self.currentDrive.reconnect()      
        self.blocksAvailability = self.currentDrive.read_block(0)[:127]

    def append(self, path, data):
        nodes = path.strip('/').split('/')
        lastNode = self.rootDirectory
        for node in nodes:
            lastNode = lastNode.getChild(node)
        lastNode.appendData(data)
            
    def ls(self, path):
        nodes = path.strip('/').split('/')
        lastNode = self.rootDirectory
        for node in nodes:
            if node != "":
                lastNode = lastNode.getChild(node)
        lastNode.list()

    def print(self, path):
        nodes = path.strip('/').split('/')
        lastNode = self.rootDirectory
        for node in nodes:
            if node != "":
                lastNode = lastNode.getChild(node)
        lastNode.print()

    def delfile(self, path):
        nodes = path.strip('/').split('/')
        lastNode = self.rootDirectory
        for node in nodes:
            if node != "":
                lastNode = lastNode.getChild(node)
        lastNode.delete()

    def deldir(self, path):
        nodes = path.strip('/').split('/')
        lastNode = self.rootDirectory
        for node in nodes:
            if node != "":
                lastNode = lastNode.getChild(node)
        lastNode.delete()

class Directory:

    def __init__(self, drive, fileNum, parentBlockNum, parent, name):
        self.name = name
        self.drive = drive
        self.fileNum = fileNum  # This indicate the index of current directory in the parent directory
        self.parentBlockNum = parentBlockNum # parentBlockNum is the index of the data of the this directory
        self.parent = parent
        self.children = dict()
        self.childrenCounter = 0
        self.blocksIndices = []
        self.firstBlockFull = False
        self.type = "Directory"
        if parent == None:
            self.blocksIndices = [0]
    
    #Get children by name
    def getChild(self, childName):
        return self.children.get(childName)

    def getParent(self):
        return self.parent

    def removeChild(self, fileNum):
        #self.children = [child for child in self.children if child.fileNum != fileNum]
        #for child in self.children:
        #    if child.fileNum > fileNum:
        #        child.fileNum -= 1
        childToPopKey = None
        for key in self.children:
            if self.children[key].fileNum == fileNum:
                childToPopKey = key
        if childToPopKey != None:
            self.children.pop(childToPopKey)
        for key in self.children:
            if self.children[key].fileNum > fileNum:
                self.children[key].fileNum -= 1
        self.childrenCounter -= 1
        
    def addDirectory(self, childName):
        # Check which block to store this child
        if self.parent != None:
            blockNum = int(self.childrenCounter / 8)
            if len(self.blocksIndices) <= blockNum and self.parent != None:
                global availableBlockIndices
                availableBlockIndex = availableBlockIndices.pop(0)
                self.blocksIndices.append(availableBlockIndex)
                self.drive.write_block(self.blocksIndices[blockNum], ("f:" + " " * 9 + "0000:" + "000 " * 12) * 8)
                global availableBlocksList
                availableBlocksList[availableBlockIndex] = "+"
                self.drive.write_block(0, (''.join(availableBlocksList) + self.drive.read_block(0)[BITMAP_SIZE:]))
                blocksIndicesString = ""
                for index in self.blocksIndices:
                    blocksIndicesString = blocksIndicesString + str(index).zfill(3) + " "
                blocksIndicesString = blocksIndicesString + "000 " * (12 - len(self.blocksIndices))
                parentBlockContent = self.drive.read_block(self.parentBlockNum)
                if self.parent.parent != None:
                    parentBlockContent = parentBlockContent[0 : self.fileNum * FILE_INFO_SIZE + FILE_TYPE_LENGTH + FILE_NAME_LENGTH] + str(512 * len(self.blocksIndices)).rjust(FILE_LENGTH, "0") + ":" + blocksIndicesString + parentBlockContent[(self.fileNum + 1) * FILE_INFO_SIZE:]
                else:
                    parentBlockContent = parentBlockContent[0 : self.fileNum * FILE_INFO_SIZE + FILE_TYPE_LENGTH + FILE_NAME_LENGTH + BITMAP_SIZE] + str(512 * len(self.blocksIndices)).rjust(FILE_LENGTH, "0") + ":" + blocksIndicesString + parentBlockContent[(self.fileNum + 1)* FILE_INFO_SIZE + BITMAP_SIZE:]
                self.drive.write_block(self.parentBlockNum, parentBlockContent)
        else:
            blockNum = 0
        blockContent = self.drive.read_block(self.blocksIndices[blockNum])
        # If this directory is not root directory.
        if self.parent != None:
            blockContent = blockContent[0 : (self.childrenCounter - 8 * blockNum) * FILE_INFO_SIZE] + "d:" + childName.ljust(9, " ") +  "0000:000 000 000 000 000 000 000 000 000 000 000 000 " + blockContent[(self.childrenCounter - 8 * blockNum) * FILE_INFO_SIZE  + FILE_INFO_SIZE:]
            newDir = Directory(self.drive, int(self.childrenCounter % 8), self.blocksIndices[blockNum], self, childName)
        else:
            blockContent = blockContent[0 : 128 + (self.childrenCounter - 6 * blockNum) * FILE_INFO_SIZE] + "d:" + childName.ljust(9, " ") +  "0000:000 000 000 000 000 000 000 000 000 000 000 000 " + blockContent[128 + (self.childrenCounter - 6 * blockNum) * FILE_INFO_SIZE  + FILE_INFO_SIZE:]
            newDir = Directory(self.drive, self.childrenCounter, self.blocksIndices[blockNum], self, childName)
        self.drive.write_block(self.blocksIndices[blockNum], blockContent)
        self.children[childName] = newDir
        self.childrenCounter = self.childrenCounter + 1

    def addFile(self, childName):
        # Check which block to store this child
        if self.parent != None:
            blockNum = int(self.childrenCounter / 8)
            if len(self.blocksIndices) <= blockNum and self.parent != None:
                global availableBlockIndices
                availableBlockIndex = availableBlockIndices.pop(0)
                self.blocksIndices.append(availableBlockIndex)
                self.drive.write_block(self.blocksIndices[blockNum], ("f:" + " " * 9 + "0000:" + "000 " * 12) * 8)
                global availableBlocksList
                availableBlocksList[availableBlockIndex] = "+"
                self.drive.write_block(0, (''.join(availableBlocksList) + self.drive.read_block(0)[BITMAP_SIZE:]))
                blocksIndicesString = ""
                for index in self.blocksIndices:
                    blocksIndicesString = blocksIndicesString + str(index).zfill(3) + " "
                blocksIndicesString = blocksIndicesString + "000 " * (12 - len(self.blocksIndices))
                parentBlockContent = self.drive.read_block(self.parentBlockNum)
                if self.parent.parent != None:
                    parentBlockContent = parentBlockContent[0 : self.fileNum * FILE_INFO_SIZE + FILE_TYPE_LENGTH + FILE_NAME_LENGTH] + str(512 * len(self.blocksIndices)).rjust(FILE_LENGTH, "0") + ":" + blocksIndicesString + parentBlockContent[(self.fileNum + 1) * FILE_INFO_SIZE:]
                else:
                    parentBlockContent = parentBlockContent[0 : self.fileNum * FILE_INFO_SIZE + FILE_TYPE_LENGTH + FILE_NAME_LENGTH + BITMAP_SIZE] + str(512 * len(self.blocksIndices)).rjust(FILE_LENGTH, "0") + ":" + blocksIndicesString + parentBlockContent[(self.fileNum + 1)* FILE_INFO_SIZE + BITMAP_SIZE:]
                self.drive.write_block(self.parentBlockNum, parentBlockContent)
        else:
            blockNum = 0
        blockContent = self.drive.read_block(self.blocksIndices[blockNum])
        # If this directory is not root directory.
        if self.parent != None:
            blockContent = blockContent[0 : (self.childrenCounter - 8 * blockNum) * FILE_INFO_SIZE] + "f:" + childName.ljust(9, " ") +  "0000:000 000 000 000 000 000 000 000 000 000 000 000 " + blockContent[(self.childrenCounter - 8 * blockNum) * FILE_INFO_SIZE  + FILE_INFO_SIZE:]
            newFile = File(self.drive, int(self.childrenCounter % 8), self.blocksIndices[blockNum], self, childName) 
        else:
            blockContent = blockContent[0 : 128 + (self.childrenCounter - 6 * blockNum) * FILE_INFO_SIZE] + "f:" + childName.ljust(9, " ") +  "0000:000 000 000 000 000 000 000 000 000 000 000 000 " + blockContent[128 + (self.childrenCounter - 6 * blockNum) * FILE_INFO_SIZE  + FILE_INFO_SIZE:]
            newFile = File(self.drive, self.childrenCounter, self.blocksIndices[blockNum], self, childName)
        self.drive.write_block(self.blocksIndices[blockNum], blockContent)
        self.children[childName] = newFile
        self.childrenCounter = self.childrenCounter + 1

    def list(self):
        if len(self.children) > 0:
            for child in self.children:
                if self.parent != None:
                    print("Name: " + self.children.get(child).name + " Type: " + self.children.get(child).type + " Size: " + self.drive.read_block(self.children.get(child).parentBlockNum)[self.children.get(child).fileNum * FILE_INFO_SIZE + FILE_TYPE_LENGTH + FILE_NAME_LENGTH : self.children.get(child).fileNum * FILE_INFO_SIZE + FILE_TYPE_LENGTH + FILE_NAME_LENGTH + FILE_LENGTH])
                else:
                    print("Name: " + self.children.get(child).name + " Type: " + self.children.get(child).type + " Size: " + self.drive.read_block(self.children.get(child).parentBlockNum)[self.children.get(child).fileNum * FILE_INFO_SIZE + FILE_TYPE_LENGTH + FILE_NAME_LENGTH + BITMAP_SIZE : self.children.get(child).fileNum * FILE_INFO_SIZE + FILE_TYPE_LENGTH + FILE_NAME_LENGTH + BITMAP_SIZE + FILE_LENGTH ])
        else:
            print("This folder is empty")

    def delete(self):
        if len(self.children) > 0:
            print("========== Please delete all the children first before deleting this directory! ==========")
            return
        global availableBlockIndices
        global availableBlocksList
        for index in self.blocksIndices:
            self.drive.write_block(index, " " * BLOCK_SIZE)
            availableBlockIndices.append(index)
            availableBlocksList.pop(index)
            availableBlocksList.insert(index, "-")
        self.drive.write_block(0, (''.join(availableBlocksList) + self.drive.read_block(0)[BITMAP_SIZE:]))
        availableBlockIndices.sort()
        # If the parent folder is not root directory
        parentBlockContent = self.drive.read_block(self.parentBlockNum)
        if self.parent.parent != None:
            parentBlockContent = parentBlockContent[:self.fileNum * FILE_INFO_SIZE] + parentBlockContent[(self.fileNum + 1) * FILE_INFO_SIZE:] + ("f:" + " " * 9 + "0000:" + "000 " * 12)
        else:
            parentBlockContent = parentBlockContent[:(self.fileNum) * FILE_INFO_SIZE + BITMAP_SIZE] + parentBlockContent[BITMAP_SIZE + (self.fileNum + 1) * FILE_INFO_SIZE:] + ("f:" + " " * 9 + "0000:" + "000 " * 12)    
        self.parent.removeChild(self.fileNum)
        if len(self.parent.children) == 0:
            parentBlockContent = " " * BLOCK_SIZE
            self.drive.write_block(self.parentBlockNum, " " * BLOCK_SIZE)
            availableBlockIndices.append(self.parentBlockNum)
            availableBlocksList.pop(self.parentBlockNum)
            availableBlocksList.insert(self.parentBlockNum, "-")
            self.drive.write_block(0, (''.join(availableBlocksList) + self.drive.read_block(0)[BITMAP_SIZE:]))
        self.drive.write_block(self.parentBlockNum, parentBlockContent)

class File:
    def __init__(self, drive, fileNum, parentBlockNum, parent, name):
        self.name = name
        self.drive = drive
        self.fileNum = fileNum  # This indicate the index of current file in its parent
        self.parentBlockNum = parentBlockNum
        self.parent = parent
        self.type = "File"
        self.blocksIndices = []
        self.size = 0

    def appendData(self, data):
        data = data.strip("\"")
        allData = ""
        if len(self.blocksIndices) > 0:
            for block in self.blocksIndices[:-1]:
                allData = allData + self.drive.read_block(block)
            allData = allData + self.drive.read_block(self.blocksIndices[-1])[:self.size - BLOCK_SIZE * (len(self.blocksIndices) - 1)]
        allData = allData + data
        allDataSize = len(allData) 
        self.size = allDataSize
        numOfNewBlocksNeeded = (int(len(allData) / 512) + 1) - len(self.blocksIndices)
        while numOfNewBlocksNeeded > 0:
            global availableBlockIndices
            availableBlockIndex = availableBlockIndices.pop(0)
            self.blocksIndices.append(availableBlockIndex)
            global availableBlocksList
            availableBlocksList[ availableBlockIndex] = "+"
            self.drive.write_block(0, (''.join(availableBlocksList) + self.drive.read_block(0)[BITMAP_SIZE:]))
            numOfNewBlocksNeeded = numOfNewBlocksNeeded - 1
        dataCounter = 0
        for blockIndex in self.blocksIndices:
            self.drive.write_block(blockIndex, allData[dataCounter * BLOCK_SIZE : (dataCounter + 1) * BLOCK_SIZE].ljust(BLOCK_SIZE, " "))
            dataCounter = dataCounter + 1
        blocksIndicesString = ""
        for index in self.blocksIndices:
            blocksIndicesString = blocksIndicesString + str(index).zfill(3) + " "
        blocksIndicesString = blocksIndicesString + "000 " * (12 - len(self.blocksIndices))
        parentBlockContent = self.drive.read_block(self.parentBlockNum)
        # When the file is not in root directory
        if self.parent.parent != None:
            parentBlockContent = parentBlockContent[0 : self.fileNum * FILE_INFO_SIZE + FILE_TYPE_LENGTH + FILE_NAME_LENGTH] + str(allDataSize).rjust(FILE_LENGTH, "0") + ":" + blocksIndicesString + parentBlockContent[(self.fileNum + 1) * FILE_INFO_SIZE :]
        else:
            parentBlockContent = parentBlockContent[0 : self.fileNum * FILE_INFO_SIZE + FILE_TYPE_LENGTH + FILE_NAME_LENGTH + BITMAP_SIZE] + str(allDataSize).rjust(FILE_LENGTH, "0") + ":" + blocksIndicesString + parentBlockContent[(self.fileNum + 1) * FILE_INFO_SIZE + BITMAP_SIZE:]
        self.drive.write_block(self.parentBlockNum, parentBlockContent)

    def print(self):
        output = ""
        if len(self.blocksIndices) > 0:
            for blockIndex in self.blocksIndices[:-1]:
                output += self.drive.read_block(blockIndex)
            output += self.drive.read_block(self.blocksIndices[-1])[:self.size - (len(self.blocksIndices) - 1) * BLOCK_SIZE]
        else:
            output = "=" * 20 + "This is an empty file" + "=" * 20
        print(output)

    def delete(self):
        global availableBlockIndices
        global availableBlocksList
        for index in self.blocksIndices:
            self.drive.write_block(index, " " * BLOCK_SIZE)
            availableBlockIndices.append(index)
            availableBlocksList.pop(index)
            availableBlocksList.insert(index, "-")
        self.drive.write_block(0, (''.join(availableBlocksList) + self.drive.read_block(0)[BITMAP_SIZE:]))
        availableBlockIndices.sort()
        # If the parent folder is not root directory
        parentBlockContent = self.drive.read_block(self.parentBlockNum)
        if self.parent.parent != None:
            parentBlockContent = parentBlockContent[:self.fileNum * FILE_INFO_SIZE] + parentBlockContent[(self.fileNum + 1) * FILE_INFO_SIZE:] + ("f:" + " " * 9 + "0000:" + "000 " * 12)
        else:
            parentBlockContent = parentBlockContent[:(self.fileNum) * FILE_INFO_SIZE + BITMAP_SIZE] + parentBlockContent[BITMAP_SIZE + (self.fileNum + 1) * FILE_INFO_SIZE:] + ("f:" + " " * 9 + "0000:" + "000 " * 12)    
        self.parent.removeChild(self.fileNum)
        self.drive.write_block(self.parentBlockNum, parentBlockContent)
        