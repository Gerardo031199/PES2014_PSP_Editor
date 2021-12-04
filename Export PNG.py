import binascii
import zlib
from tkinter import filedialog
from tkinter import *
from tkinter import ttk


PNG = b'\x89PNG\r\n\x1a\n\x00\x00\x00\r'

def open_id():
    file = filedialog.askopenfile(title = "Seleccione sus archivos",mode="rb",filetypes = (("all files","*.*"),("bin files","*.bin")))

    filename = file.name

    data = file.read()

    magic_number = data.find(b'x\xda')

    header = data[0:magic_number]

    data_compress = data[magic_number:len(data)]

    data_decompress = zlib.decompress(data_compress)

    txs_offset = data_decompress.find(b'\x94r\x85)\x01')

    txs_data = data_decompress[txs_offset:len(data_decompress)]

    idat_offset = txs_data[16:18]
    idat_offset_int = int.from_bytes(idat_offset, byteorder='little', signed=False)
    print(idat_offset_int)

    palette_alpha_offset = txs_data[18:20]
    palette_alpha_offset_int = int.from_bytes(palette_alpha_offset, byteorder='little', signed=False)
    print(palette_alpha_offset_int)

    
    palette_alpha = txs_data[palette_alpha_offset_int:idat_offset_int]
    

    high = txs_data[20:22]
    high_int = int.from_bytes(high, byteorder='little', signed=False)
    swap_high = high[::-1]

    width = txs_data[22:24]
    width_int = int.from_bytes(width, byteorder='little', signed=False)
    swap_width = width[::-1]

    IHDR = b'IHDR\x00\x00'+swap_high+b'\x00\x00'+swap_width+b'\x08\x03\x00\x00\x00'

    long_ihdr = zlib.crc32(IHDR)
    long_ihdr_zlib32 = long_ihdr.to_bytes(4, byteorder='big', signed=False)

    palette = b""
    for i in range(1,len(palette_alpha),4):
        palette+= palette_alpha[i - 1:i + 2]
 
    trns = b""
    for i in range(0, len(palette_alpha), 4):
        trns += palette_alpha[i + 3:i + 4]


    trns_x2 = bytearray(trns)
    
    for i in range(len(trns_x2)):
        valor = trns_x2[i]*2
        if valor > 255:
            valor = 255
        trns_x2[i] = valor
        

    print(trns_x2)
        
    num_colors=(len(trns_x2))

    
    palette_set = b""       
    for i in range(0, len(palette_alpha), 96):
        plte1 = palette[i:i + 24]
        plte2 = palette[i + 24:i + 48]
        plte3 = palette[i + 48:i + 72]
        plte4 = palette[i + 72:i + 96]

        palette_set += plte1+plte3+plte2+plte4

    long_plt = zlib.crc32(b'PLTE'+palette_set)
    long_plt_zlib32 = long_plt.to_bytes(4, byteorder='big', signed=False)


    long_trns = zlib.crc32(b'tRNS'+trns_x2)
    long_trns_zlib32 = long_trns.to_bytes(4, byteorder='big', signed=False)

    data = txs_data[1152:len(txs_data)]

    data_modex2 = b""

    for i in range(1, len(data), high_int):
        data_modex2 += data [i:i + high_int] + b'\x00'

    idat_compress = zlib.compress(b'\x00'+data_modex2, 9)

    size_idat_compress =(len(idat_compress))
    size_idat_compress_hxd2 = size_idat_compress.to_bytes(4, byteorder='big', signed=True)

    long_idat = zlib.crc32(b'IDAT'+idat_compress)
    long_idat_zlib32 = long_idat.to_bytes(4, byteorder='big', signed=False)

    with open(filename+'.png','w+b') as new_file:
        new_file.write(PNG)
        new_file.write(IHDR)
        new_file.write(long_ihdr_zlib32)
        new_file.write(b'\x00\x00\x03\x00PLTE')
        new_file.write(palette_set)
        new_file.write(long_plt_zlib32)
        new_file.write(b'\x00\x00\x01\x00')
        new_file.write(b'tRNS')
        new_file.write(trns_x2)
        new_file.write(long_trns_zlib32)
        new_file.write(size_idat_compress_hxd2)
        new_file.write(b'IDAT')
        new_file.write(idat_compress)
        new_file.write(long_idat_zlib32)
        new_file.write(b'\x00\x00\x00\x00IEND\xaeB`\x82')


root = Tk()
root.resizable(False, False)
root.title("Export PNG")

labelframe1 = ttk.LabelFrame(root, text="Export PNG")
labelframe1.grid(column=0, row=0, padx=10, pady=10)

btn1 = ttk.Button(labelframe1,text="Open", command=open_id)
btn1.grid(column=0, row=0, padx=27, pady=10)

root.mainloop()
