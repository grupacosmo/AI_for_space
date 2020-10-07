import sensor
import image
import KPU as kpu
import json
import struct
from Maix import freq
from fpioa_manager import fm
from machine import UART
from board import board_info
from fpioa_manager import fm

#Wiktor Tomsik 2020-10-05

def enum(**enums):
    return type('Enum', (), enums)

#Available network architetures
ModelTypes = enum(YOLO=0, MOBILE_NET=1,EDGE=2,SHARP=3)
model_type = ModelTypes.MOBILE_NET
CHANGE_UART_COMMAND = 115
PwrCommand = enum(LOW = 109,MEDIUM = 110,HIGH = 111,LOW = 112)
ZM =False
#How many times data pocket is sent
DATA_ITERATION = 2
UART_BOUND_RATE = 115200
UART_BITS = 8
UART_STOP_BIT = 0
UART_PARITY_BIT = 0

fm.register(board_info.PIN15, fm.fpioa.UART1_TX, force=True)
fm.register(board_info.PIN17, fm.fpioa.UART1_RX, force=True)

uart = UART(UART.UART1, UART_BOUND_RATE,UART_BITS,UART_STOP_BIT,UART_PARITY_BIT, timeout=1000, read_buf_len=4096)

def init_mobile_net_from_sd(name,out,labels,sensitivity = [0.5,0.3]):
    """Loading mobilenet from sd"""
    task = kpu.load("/sd/"+name)
    kpu.set_outputs(task, out[0], out[1],out[2],out[3])
    classifier_labels = labels
    global model_type
    global global_task
    model_type = ModelTypes.MOBILE_NET
    global_task = task
    return task

def init_yolo_from_mem(address =0x300000, out = None,sensitivity = [0.5,0.3]):
    """Loading yolo nn from memory"""
    #anchor a set of constant dependent on architeure type
    anchor = (1.889, 2.5245, 2.9465, 3.94056, 3.99987, 5.3658, 5.155437, 6.92275, 6.718375, 9.01025)
    task = kpu.load(address)
    if out is not None:
        kpu.set_outputs(task, out[0], out[1],out[2],out[3])
    a = kpu.init_yolo2(task, sensitivity[0], sensitivity[1], 5, anchor)
    global model_type
    global global_task
    model_type = ModelTypes.YOLO
    global_task = task
    return task




def handle_uart(kpu_result):
    uart_reply = uart.read()
    if uart_reply is None:
        return

    for command in uart_reply:
        if 101 <= command <= 107:
            if model_type is ModelTypes.YOLO:
                handle_yolo_result_reqest(kpu_result,command)
            elif model_type is ModelTypes.MOBILE_NET:
                handle_mobile_result_reqest(kpu_result,command)

        elif command == 108:
            reset()
        elif 109 <= command <= 111:
            pass
            #handle_toggle_power_mode_reqest(command)
        #elif pwr_mode_timer:
            #pass
            #handle_pwr_timer() todo
        elif CHANGE_UART_COMMAND:
            global ZM
            if ZM == True:
                return
            ZM = change_model(0)
            continue

def change_model(uart_reply):
    print("nn model changed")

    a = kpu.deinit(global_task)
    index = 0
    if uart_reply is None:
        return

    if uart_reply is 0:
        output = [0,7,7,30]
        sensitivity = [0.3,0.3]
        task = init_yolo_from_mem(0x300000,output,sensitivity)
        index = 0
    elif uart_reply is 1:
        name = 'palm_tree.kmodel'
        output = [0,1,2,1]
        labels = ['oil palm plantations detected','not detected']
        init_mobile_net_from_sd(name,output,labels)
        index = 1
    elif uart_reply is 2:
        model_type = ModelTypes.EDGE
    elif uart_reply is 3:
        model_type = ModelTypes.SHARP

    _id = CHANGE_UART_COMMAND.to_bytes(1,'little')
    for i in range(DATA_ITERATION):
        uart.write(_id)
    uart.write(index.to_bytes(1,'little'))
    return True


def handle_toggle_power_mode_reqest(command):
    """Change of kpu and cpu freqency for varing power consuption"""
    return
    if command is PwrCommand.LOW:
        freq.set (cpu = 26, kpu = 26)
    elif command is PwrCommand.MEDIUM:
        freq.set (cpu = 400, kpu = 400)
    elif command is PwrCommand.HIGH:
        freq.set (cpu = 600, kpu = 600)

    for i in range(DATA_ITERATION):
        uart.write(PwrCommand.ID)
    for i in range(DATA_ITERATION):
         cpu_freq,kpu_freq =  freq.get()
         uart.write(int(cpu_freq).to_bytes(2,'little'))
         uart.write(int(kpu_freq).to_bytes(2,'little'))


def write_val(id,values):
    """Sending data touart"""
    _id = id.to_bytes(1,'little')
    if model_type is ModelTypes.YOLO:
        if id <= 102:
            print("asDDASSEDFA")
            _values = [int(v).to_bytes(2,'little') for v in values]
        elif id == 103:
            _values = [bytearray(struct.pack("f", v)) for v in values]
        else:
            _values = [int(v).to_bytes(1,'little') for v in values]

    elif model_type is ModelTypes.MOBILE_NET:
         _values = bytearray(struct.pack("f", values))

    for i in range(DATA_ITERATION):
        print("A2")
        uart.write(_id)
    for v in _values:
        for i in range(DATA_ITERATION):
            print("A1")
            uart.write(v)

def handle_mobile_result_reqest(kpu_result,command):
    if kpu_result is None:
        return

    result = []
    plist=kpu_result[:]
    if command == 101:
        result.append(max(plist))
    elif command == 102:
        result.append(plist[0])
        result.append(plist[1])


    pmax = max(plist)
    max_index = plist.index(pmax)


def handle_yolo_result_reqest(kpu_result,command):
    if kpu_result is None:
        return

    result = []

    for kpu_val in kpu_result:
        result_dict = json.loads(str(kpu_val))
        #result = list(result_dict.values())[command-100]
        result = []
        if command == 101:
            result.append(result_dict['x'])
            result.append(result_dict['y'])
        elif command == 102:
            result.append(result_dict['w'])
            result.append(result_dict['h'])
        elif command == 103:
            result.append(result_dict['value'])
        elif command == 104:
            result.append(result_dict['classid'])
        elif command == 105:
            result.append(result_dict['index'])
        elif command == 106:
            result.append(result_dict['objnum'])

        print(kpu_val)
        print(result)
        print(command)

        write_val(command,result)


class RectInterpol:
    def __init__(self,value):
        self.x = 224
        self.y =224
        self.w =0
        self.h =0
        self.value = value
    def get(self,rect):
        a =self.value
        b = (1-self.value)
        self.x = self.x*a +rect[0]*b
        self.y = self.y*a +rect[1]*b
        self.w = self.w*a +rect[2]*b
        self.h = self.h*a +rect[3]*b
        return (round(self.x),round(self.y),round(self.w),round(self.h*0.6))

rect = RectInterpol(0.7)
result_dict = dict()



sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_windowing((224, 224))
sensor.run(1)
#sensor.set_vflip(1)

output = [0,7,7,30]
sensitivity = [0.4,0.3]
task = init_yolo_from_mem(0x300000,output,sensitivity)
#name = 'palm_tree.kmodel'
#output = [0,1,2,1]
##labels = ['DETECTED: oil palm plantations','NOT DETECTED']
#labels = ['DETECTED: ','NOT DETECTED: ']
#global_task = init_mobile_net_from_sd(name,output,labels)

while(True):
    frame = sensor.snapshot()
    frame.pix_to_ai()

    if model_type is ModelTypes.MOBILE_NET:
        kpu_result = kpu.forward(global_task, frame)
        handle_uart(kpu_result)

        plist=kpu_result[:]
        plist = (plist[0],plist[1]-0.05)
        pmax = max(plist)
        max_index = plist.index(pmax)
        pmax = round(pmax*100)/100
        print(str(labels[max_index]).strip());
        print(plist)
        frame.draw_string(70, 20, str(labels[max_index]).strip()+str(pmax), scale=2.2,color=(255,50,50))
    elif model_type is ModelTypes.YOLO:
        kpu_result = kpu.run_yolo2(global_task, frame)
        handle_uart(kpu_result)

        if kpu_result:
            for i in kpu_result:
                r = rect.get(i.rect())
                a = frame.draw_rectangle(r)
                frame.draw_cross((round(r[0]+r[2]*0.5),round(r[1]+r[3]*0.5)),color=(255,0,0))
                print(i)
    elif model_type is ModelTypes.EDGE:
        frame.conv3((-1,-1,-1,-1,8,-1,-1,-1,-1))
    elif model_type is ModelTypes.SHARP:
        frame.conv3((-1,-1,-1,-1,9,-1,-1,-1,-1))


a = kpu.deinit(global_task)






