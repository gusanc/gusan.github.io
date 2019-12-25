import wave
import numpy as np
from matplotlib import pyplot as plt
from PyQt5 import QtCore, QtGui, QtWidgets
from scipy.fftpack import fft,ifft
import math
import threading
from scipy import signal
import pyaudio
def catch_number(y, framerate, nframes):
    frh = []
    frl = []
    math_list = []
    fruquent = [697, 770, 852, 941, 1209, 1336, 1477, 1633]
    math = {(697, 1209): '1', (697, 1336): '2', (697, 1477): '3', (697, 1633): 'A',
            (770, 1209): '4', (770, 1336): '5', (770, 1477): '6', (770, 1633): 'B',
            (852, 1209): '7', (852, 1336): '8', (852, 1477): '9', (852, 1633): 'C',
            (941, 1209): '*', (941, 1336): '0', (941, 1477): '#', (941, 1633): 'D'}
    for fr in fruquent:
        sum1 = sum(y[fr* nframes //framerate-(20* nframes //framerate):fr* nframes //framerate])
        sum2 = sum(y[fr* nframes //framerate:fr * nframes //framerate+(20* nframes //framerate)])
        sumx = sum1 + sum2
        if fr < 1000:
            frl.append([fr, sumx])
        else:
            frh.append([fr, sumx])
    frl = sorted(frl, key=lambda x: x[1])
    frh = sorted(frh, key=lambda x: x[1])
    frl = frl.pop()
    frh = frh.pop()
    if frh[1] < 10:
        return None
    if frl[1] < 10:
        return None
    math_list.append(frl[0])
    math_list.append(frh[0])
    math_list = tuple(math_list)
    for key, value in math.items():
        if key == math_list:
            return value
def Endpoint_detection(wave_data, energy, Zero) :
    sum = 0
    energyAverage = 0
    for en in energy :
        sum = sum + en
    energyAverage = sum / len(energy)

    sum = 0
    for en in energy[:10] :
        sum = sum + en
    ML = sum / 10
    MH = energyAverage /4             
    ML = (ML + MH) / 2    
    sum = 0
    for zcr in Zero[:100] :
        sum = float(sum) + zcr
    Zs = sum / 100                    

    A = []
    B = []
    C = []
    print(MH,ML,Zs)

    
    flag = 0
    for i in range(len(energy)):
        if len(A) == 0 and flag == 0 and energy[i] > MH :
            A.append(i)
            flag = 1
        elif flag == 0 and energy[i] > MH and i - 21 > A[len(A) - 1]:
            A.append(i)
            flag = 1
        elif flag == 0 and energy[i] > MH and i - 21 <= A[len(A) - 1]:
            A = A[:len(A) - 1]
            flag = 1

        if flag == 1 and energy[i] < MH :
            A.append(i)
            flag = 0
   
    for j in range(len(A)) :
        i = A[j]
        if j % 2 == 1 :
            while i < len(energy) and energy[i] > ML :
                i = i + 1
            B.append(i)
        else :
            while i > 0 and energy[i] > ML :
                i = i - 1
            B.append(i)
    

    
    for j in range(len(B)) :
        i = B[j]
        if j % 2 == 1 :
            while i < len(Zero) and Zero[i] >= 3 * Zs :
                i = i + 1
            C.append(i)
        else :
            while i > 0 and Zero[i] >= 3 * Zs :
                i = i - 1
            C.append(i)
    
    for i, data in enumerate(C):
        if i % 2 == 1:
            x = C[i] - C[i-1]
            if x < 10:
                del C[i]
                del C[i-1]

    
    count = []
    for data in C:
        count.append(data * 256)
    return count
def continue_math(count,yt,framerate):
    x = []
    math = []
    for i, data in enumerate(count):
        x.append(data)
        if (i + 1) % 2 == 0:
            y1 = yt[x[0]:x[1]]
            yf1 = abs(fft(y1)) / len(y1)  
            yf2 = yf1[range(int(len(y1) / 2))]  
            math_ = catch_number(yf2, framerate, x[1] - x[0])
            x = []
            if math_ == None:
                continue
            math.append(math_)

    return math

def play():
    chunk = 2048
    wf = wave.open(path, 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()), channels=wf.getnchannels(),rate=wf.getframerate(), output=True)
    data = wf.readframes(chunk)  
    while True:
        data = wf.readframes(chunk)
        if data == "":
            break
        stream.write(data)
    stream.stop_stream()  
    stream.close()
    p.terminate()  

    print('play函数结束！')
def thread_it(func, *args):
    t = threading.Thread(target=func, args=args)
    t.setDaemon(True)
    t.run()

def thread_it_(func, *args):
    t = threading.Thread(target=func, args=args)
    t.setDaemon(True)
    t.start()
def  fftc(path):
    file = wave.open(path, "rb")
    information = file.getparams()
    nchannels, sampwidth, framerate, nframes = information[:4]
    str_data = file.readframes(nframes)
    file.close()
    wave_data = np.fromstring(str_data, dtype=np.short)
    wave_data.shape = -1, 2
    wave_data = wave_data.T
    yt = wave_data[0]
    yf2 = yt
    x = np.arange(0, len(yf2) / 2) * framerate / nframes
    yf1 = abs(fft(yf2)) / len(yt)  
    yf2 = yf1[range(int(len(yf2) / 2))]  
    return x, yf2, framerate, nframes, yt
def calEnergy(wave_data) :
    energy = []
    sum = 0
    for i in range(len(wave_data)) :
        sum = sum + (int(wave_data[i]) ** ui.horizontalSlider_2.value() )
        if (i + 1) % 256 == 0 :
            energy.append(sum)
            sum = 0
        elif i == len(wave_data) - 1 :
            energy.append(sum)
    return energy
def calZero(waveData):
    frameSize = 256
    overLap = 0
    wlen = len(waveData)
    step = frameSize - overLap
    frameNum = math.ceil(wlen/step)
    zcr = np.zeros((frameNum,1))
    for i in range(frameNum):
        curFrame = waveData[np.arange(i*step, min(i*step+frameSize,wlen))]
        curFrame = curFrame - np.mean(curFrame) # zero-justified
        zcr[i] = sum(curFrame[0:-1]*curFrame[1::] <= 0)
    return zcr

def wave_analysis(file_path):
    f=wave.open(file_path,'rb')
    num=file_path[-5] 
    params=f.getparams()
    nchannels,samplewidth,framerate,nframes=params[:4]
    str_data=f.readframes(nframes)
    f.close()
    wave_data=np.fromstring(str_data,dtype=np.short)
    wave_data.shape=-1,1
    if nchannels==2:
        wave_data.shape=-1,2
    else:
        pass
    wave_data=wave_data.T
    time=np.arange(0,nframes)*(1.0/framerate)
    plt.subplot(211)
    plt.plot(time,wave_data[0],'r-')
    plt.xlabel('Time/s')
    plt.ylabel('Ampltitude')
    plt.title('Num '+num+' time/ampltitude')
    plt.show()
    df=framerate/(nframes-1)
    freq=[df*n for n in range(0,nframes)]
    transformed=np.fft.fft(wave_data[0])
    d=int(len(transformed)/2)
    while freq[d]>4000:
        d-=10
    freq=freq[:d]
    transformed=transformed[:d]
    for i,data in enumerate(transformed):
        transformed[i]=abs(data)
    plt.subplot(212)
    plt.plot(freq,transformed,'b-')
    plt.xlabel('Freq/Hz')
    plt.ylabel('Ampltitude')
    plt.title('Num '+num+' freq/ampltitude')
    local_max=[]
    for i in np.arange(1,len(transformed)-1):
        if transformed[i]>transformed[i-1] and transformed[i]>transformed[i+1]:
            local_max.append(transformed[i])
    local_max=sorted(local_max)
    loc1=np.where(transformed==local_max[-1])
    max_freq=freq[loc1[0][0]]
    loc1=np.where(transformed==local_max[-2])
    min_freq=freq[loc1[0][0]]
    plt.show()
    print ('Two freq ',max_freq,min_freq)
    return max_freq,min_freq
    
 
def main():
    x=[]
    y=[]
    for i in np.arange(0,10):
        path=r'C:\Users\dengy\Desktop\123\3.wav'  
        max_freq,min_freq=wave_analysis(path)
        x.append(i)
        y.append(max_freq)
        x.append(i)
        y.append(min_freq)
    plt.scatter(x,y,marker='*')
    plt.show()

def action_frequency_signal():
    plt.xlim((0,2000))
    plt.plot(x, yf)
    plt.show()

def action_zero_signal():
    plt.plot(Z)
    plt.show()

def action_L_signal():
    plt.plot(E)
    plt.show()

def action_E_signal():
    plt.plot(yt)
    plt.show()

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(400, 350)
        MainWindow.setMinimumSize(QtCore.QSize(400, 350))
        MainWindow.setMaximumSize(QtCore.QSize(400, 350))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(40, 180, 65, 243))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_4 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_2.addWidget(self.label_4)
        self.label_3 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_2.addWidget(self.label_3)
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.label_2 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.horizontalSlider = QtWidgets.QSlider(self.centralwidget)
        self.horizontalSlider.setGeometry(QtCore.QRect(250, 450, 140, 32))
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.horizontalSlider.setRange(0,200)
        self.horizontalSlider_2 = QtWidgets.QSlider(self.centralwidget)
        self.horizontalSlider_2.setGeometry(QtCore.QRect(250, 450, 140, 32))
        self.horizontalSlider_2.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_2.setObjectName("horizontalSlider_2")
        self.horizontalSlider_2.setRange(2, 4)
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(90, 210, 113, 20))
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit_2 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_2.setGeometry(QtCore.QRect(90, 340, 113, 20))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.lineEdit_3 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_3.setGeometry(QtCore.QRect(90, 270, 113, 20))
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.lineEdit_4 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_4.setGeometry(QtCore.QRect(90, 400, 113, 20))
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(250, 480, 51, 21))
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(250, 540, 54, 12))
        self.label_6.setObjectName("label_6")
        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        self.label_7.setGeometry(QtCore.QRect(340, 460, 54, 12))
        self.label_7.setText("")
        self.label_7.setObjectName("label_7")
        self.label_8 = QtWidgets.QLabel(self.centralwidget)
        self.label_8.setGeometry(QtCore.QRect(340, 510, 54, 12))
        self.label_8.setText("")
        self.label_8.setObjectName("label_8")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(150, 170, 75, 23))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(270, 170, 75, 23))
        self.pushButton_2.setObjectName("pushButton_2")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 500, 23))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuView = QtWidgets.QMenu(self.menubar)
        self.menuView.setObjectName("menuView")
        MainWindow.setMenuBar(self.menubar)
        self.actionOpen_file = QtWidgets.QAction(MainWindow)
        self.actionOpen_file.setObjectName("actionOpen_file")
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionShow_chart = QtWidgets.QAction(MainWindow)
        self.actionShow_chart.setObjectName("actionShow_chart")
        self.actionAsd_a = QtWidgets.QAction(MainWindow)
        self.actionAsd_a.setObjectName("actionAsd_a")
        self.action_zero_signal = QtWidgets.QAction(MainWindow)
        self.action_zero_signal.setObjectName("action_zero_signal")
        self.action_frequency_signal = QtWidgets.QAction(MainWindow)
        self.action_frequency_signal.setObjectName("action_frequency_signal")
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionOpen_file)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuView.addAction(self.actionShow_chart)
        self.menuView.addAction(self.action_frequency_signal)
        self.menuView.addAction(self.actionAsd_a)
        self.menuView.addAction(self.action_zero_signal)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.retranslateUi(MainWindow)
        self.link(MainWindow)
        self.label_7.setNum(0)
        self.label_8.setNum(2)
        self.horizontalSlider_2.valueChanged['int'].connect(self.label_8.setNum)
        self.horizontalSlider.valueChanged['int'].connect(self.label_7.setNum)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)


    def link(self,MainWindow):
        
        self.actionOpen_file.triggered.connect(lambda: self.FileDialog(MainWindow))
        self.actionExit.triggered.connect(MainWindow.close)
        self.pushButton.clicked.connect(lambda :thread_it_(play))
        self.pushButton_2.clicked.connect(lambda :thread_it(recognition))
        self.action_frequency_signal.triggered.connect(action_frequency_signal)
        self.action_zero_signal.triggered.connect(action_zero_signal)
        self.actionAsd_a.triggered.connect(action_L_signal)
        self.actionShow_chart.triggered.connect(action_E_signal)


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_4.setText(_translate("MainWindow", "音频时长："))
        self.label_3.setText(_translate("MainWindow", "采样频率："))
        self.pushButton.setText(_translate("MainWindow", "播放"))
        self.pushButton_2.setText(_translate("MainWindow", "识别"))
        self.menuFile.setTitle(_translate("MainWindow", "file"))
        self.actionOpen_file.setText(_translate("MainWindow", "open  file"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))
        


    def FileDialog(self,MainWindow):
        fileName1, filetype = QtWidgets.QFileDialog.getOpenFileName(MainWindow,"选取文件","./","音频文件 (*.wav);;Text Files (*.txt)")
        if fileName1 == '':
            return None
        global path
        global yt, yf, x, E ,Z
        path = fileName1
        file = wave.open(path, "rb")
        params = file.getparams()
        self.nchannels, self.sampwidth, self.framerate, self.nframes = params[:4]
        x, yf, framerate, nframes, yt = fftc(path)
        E = calEnergy(yt)
        Z = calZero(yt)
        self.lineEdit.setText(str(round((1/self.framerate) * self.nframes,2)) + "s")
        self.lineEdit_3.setText(str(self.framerate) + "hz")

def recognition():
    x, yf2, framerate, nframes, yt = fftc(path)
    b, a = signal.butter(11, 0.028, 'highpass')
    yt_updata = signal.filtfilt(b, a, yt)  
    b, a = signal.butter(11, 0.0687, 'lowpass')
    yt_updata = signal.filtfilt(b, a, yt_updata) 
    Z = calZero(yt_updata)
    E = calEnergy(yt_updata)
    count = Endpoint_detection(yt_updata,E,Z)
    math = continue_math(count, yt_updata , framerate)
    math_ = ''.join(math)
    QtWidgets.QMessageBox.information(MainWindow,"你输入的数字",math_,QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())


if __name__=='__main__':
    main()

def wave_analysis_single(efficient_data,framerate):  
    
    time=np.arange(0,len(efficient_data[0]))*(1.0/framerate)  

    df=framerate/(len(efficient_data[0])-1)  
    freq=[df*n for n in range(0,len(efficient_data[0]))]  
    transformed=np.fft.fft(efficient_data[0])  
    d=int(len(transformed)/2)  
    while freq[d]>2000:  
        d-=10  
    freq=freq[:d]  
    transformed=transformed[:d]  
    for i,data in enumerate(transformed):  
        transformed[i]=abs(data)  
    transformed=moving_average(transformed,5)  
    transformed=moving_average(transformed,5)  
    transformed=moving_average(transformed,5)  

    local_max=[]  
    for i in np.arange(1,len(transformed)-1):  
        if transformed[i]>transformed[i-1] and transformed[i]>transformed[i+1]:  
            local_max.append(transformed[i])  
    local_max=sorted(local_max)  
    loc1=np.where(transformed==local_max[-1])  
    freq_1=freq[loc1[0][0]]  
    loc1=np.where(transformed==local_max[-2])  
    freq_2=freq[loc1[0][0]]  
    print ('Frequency',freq_1,freq_2 ) 
    return freq_1,freq_2  
          
          
  
  