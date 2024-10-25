import time
import multiprocessing
import Picamera2
import cv2
import time
import warnings
import serial
import serial.tools.list_ports


def setup_picamera(fps=60):
    camera = Picamera2()
    camera.start_preview()
    config = camera.create_preview_configuration(main = {"size" : (640, 480)})
    camera.configure(config)
    
    ctrls = {
        "ExposureTime": 500,
        'FrameDurationLimits' : (int(1/fps * 1e6), 100000)
    }
    camera.set_controls(ctrls)
    output = SplitFrames()

    encoder = JpegEncoder(q=70)
    print("Picamera setup done.")
    return camera, encoder, output
    
def setup_webcam(fps=60):
    camera_id = 1
    vid = cv2.VideoCapture(camera_id)
    print("Webcam setup done.")
    return vid

def setup_motor():
    usb_com_port = None

    first_time = True

    if usb_com_port is None:
        print("Iniciando setup automático de comunicação Serial")
        serial_port_list = serial.tools.list_ports.comports()
        serial_port_list_size = len(serial_port_list)
        if (serial_port_list_size == 0):
            print("Não foi detectado nenhuma comunicação serial compatível")
            print("verifique se o módulo pulsador (arduino) está conectado")
            exit()
        elif (serial_port_list_size > 1):
            warnings.warn("ATENÇÃO - Foram encontradas mais de uma porta serial, o código exercutaa apenas com uma delas")
        selected_port = sorted(serial_port_list)[0]
        arduino_port = serial.Serial(port=selected_port.name, baudrate=115200, timeout=100000)
        print(f"Porta {selected_port.name} conectada")
        time.sleep(1)
        
     else:
        try:
            arduino_port = serial.Serial(port=usb_com_port, baudrate=115200, timeout=100000)
        except:
            print("Erro na conexão da comunicação serial, é recomendado alterar a variável usb_com_port no config.py para None")
            exit()
    print("Motor setup done.")
    return arduino_port
    
def picamera_acquisition(start_event, stop_event, camera, encoder, output):
    try:
        start_event.wait() # Waits for the beginning of the acquisition
        camera.start_recording(encoder, FileOutput(output))
    finally:
        stop_event.wait()
        camera.stop_recording()

def webcam_acquistion(start_event, stop_event, vid):
    frame_num = 0
    try:
        start_event.wait() # Waits for the beginning of the acquisition
        ret, frame = vid.read()
        while not stop_event.is_set()
            frame_num += 1
            cv2.imwrite(f'frames/frame_{frame_num}.jpg', frame)
    finally:
        vid.release()
        
def motor_control(start_event, stop_event, arduino_port):
    # [Posição desejada, Velocidade desejada]
    sequence = [
        # Velocidade 1:
        [13000,100],
        [0,100]
                ] 

    try:
        start_event.set() # Starts the data acquisition
        for command in sequence:
            if (arduino_port.inWaiting() > 2):
                arduino_port.flushInput()
                position = command[0]
                speed = command[1]
                text_to_send = f"{position}, {speed}\n"
                print(text_to_send)
                arduino_port.write(text_to_send.encode())
                first_time = False
        event.clear() # Stops the acquisition
        stop_event.stop
    finally:
        arduino_atuador.close()

   

if __name__ == '__main__':
    # Sampling frequency of image capturing:
    fs = 60 # Hz
    
    # Setup picamera:
    camera, encoder, output = setup_picamera(fs)
    
    # Setup webcam:
    vid = setup_webcam(fs)
    
    # Setup motor:
    arduino_port = setup_motor()
    
    # Semaphore to sync acquisition (all the elements are ready to acquire):
    start_event = multiprocessing.event()
    start_event.clear()
    stop_event = multiprocessing.event()
    stop_event.clear()
    
    
    p1 = multiprocessing.Process(target=picamera_acquisition, args=[start_event, stop_event, camera, encoder, output])
    p2 = multiprocessing.Process(target=webcam_acquistion, args=[start_event, stop_event, vid])
    p3 = multiprocessing.Process(target=motor_control, args=[start_event, stop_event, arduino_port])
    
    # Start proccess:
    p1.start()
    p2.start()
    p3.start()
    
    #
    p1.join()
    p2.join()
    p3.join()

    
    
