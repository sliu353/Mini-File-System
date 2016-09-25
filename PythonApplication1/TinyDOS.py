# Name: Liu Siyuan
# Upi: sliu353


from Volume import Volume

myVolume = Volume()

while True:
    userInput = input("")
    instructionKeyWords = userInput.split(" ", 2)
    if instructionKeyWords[0] == "quit":
        break
    if instructionKeyWords[0] == "format":
        myVolume.format(instructionKeyWords[1])
    if instructionKeyWords[0] == "reconnect":
        myVolume.reconnect(instructionKeyWords[1])
    if instructionKeyWords[0] == "mkfile":
        myVolume.mkfile(instructionKeyWords[1])
    if instructionKeyWords[0] == "mkdir":
        myVolume.mkdir(instructionKeyWords[1])
    if instructionKeyWords[0] == "ls":
        myVolume.ls(instructionKeyWords[1])
    if instructionKeyWords[0] == "print":
        myVolume.print(instructionKeyWords[1])
    if instructionKeyWords[0] == "append": 
        myVolume.append(instructionKeyWords[1], instructionKeyWords[2])
    if instructionKeyWords[0] == "delfile":
        myVolume.delfile(instructionKeyWords[1])
    if instructionKeyWords[0] == "deldir":
        myVolume.deldir(instructionKeyWords[1])