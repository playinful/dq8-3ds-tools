import os

def addAllInDir(dir, xbbs):
    for item in os.scandir(dir):
        if (item.is_dir()):
            addAllInDir(dir+'/'+item.name, xbbs)
        elif (item.name[-4:] == '.xbb'):
            xbbs.append(dir+'/'+item.name)
#
#xbbs = []
#
#addAllInDir('.')
#
#for file in xbbs:
#    with open(file, 'rb') as data:
#        ba = bytearray(data.read())
#        startind = 0
#        for b in range(len(ba)):
#            if (ba[b] == 66 and ba[b+1] == 67 and ba[b+2] == 72):
#                startind = b
#                break
#        new_ba = bytearray(ba[startind:])
#        open(file+'.bch', 'wb').write(new_ba)

str_not_exist = "The specified file or directory does not exist."
str_not_xbb = "The specified file is not a valid .xbb file."
str_no_xbbs = "There were no valid .xbb files in the specified directory."

while (True):
    #main program loop
    
    # get the mode
    mode = ''
    while (mode != 'p' and mode != 'u'):
        mode = input('(p)ack or (u)npack an .xbb file: ')
        if (len(mode) > 0):
            mode = mode[0].lower()
    
    # get the addresses to the files
    address = ''
    while (os.path.exists(address) != True):
        address = input('Type the path to the .xbb file, or the directory containing a batch of files: ')
        if (os.path.exists(address) != True):
            print(str_not_exist)
    
    # gather the files
    in_files = []
    if (os.path.isfile(address)):
        if (len(address) >= 4 and address[-4:].lower() == '.xbb'):
            in_files.append(address)
    elif (os.path.isdir(address)):
        addAllInDir(address, in_files)
    
    succ = 0
    fail = 0
    # conversion
    if (mode == 'p'):
        for file in in_files:
            if (os.path.exists(file + '.bch')):
                with open(file, 'rb') as data:
                    ba = bytearray(data.read())
                    startind = -1
                    for b in range(len(ba)):
                        if (ba[b] == 66 and ba[b+1] == 67 and ba[b+2] == 72):
                            startind = b
                            break
                    if (startind > -1):
                        bch_ba = bytearray(open(file+'.bch','rb').read())
                        new_ba = bytearray(ba[:startind] + bch_ba)
                        open(file, 'wb').write(new_ba)
                        succ = succ + 1
                    else:
                        fail = fail + 1
            else:
                fail = fail + 1
    elif (mode == 'u'):
        for file in in_files:
            with open(file, 'rb') as data:
                ba = bytearray(data.read())
                startind = -1
                for b in range(len(ba)):
                    if (ba[b] == 66 and ba[b+1] == 67 and ba[b+2] == 72):
                        startind = b
                        break
                if (startind > -1):
                    new_ba = bytearray(ba[startind:])
                    open(file+'.bch', 'wb').write(new_ba)
                    succ = succ + 1
                else:
                    fail = fail + 1
    
    if (len(in_files) == 0):
        if (os.path.isfile(address)):
            print(str_not_xbb)
        elif (os.path.isdir(address)):
            print(str_no_xbbs)
    else:
        word = ''
        if (mode == 'u'):
            word = 'un'
        print("Successfully " + word + "packed " + str(succ) + " files. Failed to " + word + "pack " + str(fail) + " files.")