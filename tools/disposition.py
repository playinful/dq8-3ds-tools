import os

mode = ""
while len(mode) != 1 or not mode in "up":
    mode = input('Type "p" to pack or "u" to unpack: ')[:1].lower()
target = ""
while len(target) <= 0:
    target = input('Type the path to the file: ')
    target = target.replace("/", "\\")
    while target.endswith("\\") or target.endswith("/"):
        target = target[:-1]

files = []
if os.path.isdir(target):
    for i in os.listdir(target):
        if i.endswith(".xbb"):
            files.append(f"{target}\\{i}")
elif os.path.isfile(target):
    files.append(target)
elif os.path.isfile(target+".xbb"):
    files.append(target+".xbb")
else:
    input("Not a valid file or directory.")
    exit()

for file in files:
    
    data = None
    with open(file, "rb") as o:
        data = o.read()
    
    if data[0:3] != b"XBB":
        continue

    file_pointers = []
    file_lengths = []
    filename_pointers = []
    file_pointer_locations = []
    file_length_locations = []
    for i in range(0x20, len(data), 0x10):
        pointer = int.from_bytes(data[i:i+4], "little")
        #if len(file_pointers) == 0 or pointer > file_pointers[-1]:
        if len(file_pointers) == 0 or i + 0x10 < filename_pointers[0]:
            file_pointers.append(pointer)
            file_pointer_locations.append(i)
            file_lengths.append(int.from_bytes(data[i+4:i+8], "little"))
            file_length_locations.append(i+4)
            filename_pointers.append(int.from_bytes(data[i+8:i+12], "little"))
        else:
            break
    
    if (len(file_pointers) <= 0):
        continue

    filenames = []
    for pointer in filename_pointers:
        filename = bytes()
        for i in range(pointer, len(data)):
            if data[i] == 0:
                break
            filename += data[i:i+1]
        filenames.append(filename.decode())
    while filenames[-1] == "":
        filenames.pop()
        file_pointers.pop()
        file_lengths.pop()
        filename_pointers.pop()
        file_pointer_locations.pop()
        file_length_locations.pop()

    file_datas = []
    for pointer, length in zip(file_pointers, file_lengths):
        file_datas.append(data[pointer:pointer+length])

    outdir = f"{file[:-4]}"
    if mode == "u":
        if not os.path.exists(outdir):
            os.makedirs(outdir)

        for filename, filedata in zip(filenames, file_datas):
            print(filename)
            with open(f"{outdir}\\{filename}", "wb") as o:
                o.write(filedata)
    if mode == "p":
        for i in range(len(filenames)):
            filename = filenames[i]
            if not os.path.exists(f"{outdir}\\{filename}"):
                continue

            filedata = bytes()
            with open(f"{outdir}\\{filename}", "rb") as o:
                filedata = o.read()

            if not filedata.endswith(b"\n\r\n"):
                while filedata.endswith(b"\n") or filedata.endswith(b"\r"):
                    filedata = filedata[:-1]
                filedata += b"\n\r\n"

            file_datas[i] = filedata

        outdata = data[:file_pointers[0]]

        for i in range(len(file_datas)):
            fdata = file_datas[i]

            file_pointers[i] = len(outdata)
            file_lengths[i] = len(fdata)
            outdata += file_datas[i]

        for i in range(len(file_pointers)):
            pointer = int.to_bytes(file_pointers[i], 4, "little")
            length  = int.to_bytes(file_lengths[i] , 4, "little")

            pointer_location = file_pointer_locations[i]
            outdata = outdata[:pointer_location] + pointer + outdata[pointer_location+4:]
            #outdata[pointer_location+0] = pointer[0]
            #outdata[pointer_location+1] = pointer[1]
            #outdata[pointer_location+2] = pointer[2]
            #outdata[pointer_location+3] = pointer[3]

            length_location = file_length_locations[i]
            outdata = outdata[:length_location] + length + outdata[length_location+4:]
            #outdata[length_location+0] = length[0]
            #outdata[length_location+1] = length[1]
            #outdata[length_location+2] = length[2]
            #outdata[length_location+3] = length[3]
        bakfile = file[:-4] + "_bak"
        appendix = ""
        while os.path.exists(f"{bakfile}{appendix}.xbb"):
            if appendix == "":
                appendix = 2
            else:
                appendix += 1
        bakfile = f"{bakfile}{appendix}.xbb"
        with open(bakfile, "wb") as o:
            o.write(data)

        with open(f"{file}", "wb") as o:
            o.write(outdata)
        print(f"{file}")

input("Done.")