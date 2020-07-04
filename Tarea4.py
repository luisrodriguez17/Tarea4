import numpy as np 
import matplotlib.pyplot as plt
from scipy import stats
from scipy import signal
from scipy import integrate
import csv
import seaborn as sns

''' 

Tendremos una frecuencia de la portadora f = 5000Hz 
Además se utiliza modulación BPSK 

'''

with open('bits10k.csv') as documento:
    sns.set()
    plt.autoscale(enable=True, axis='both', tight=None)
    bits = csv.reader(documento)
    Nbits = 10000
    #Frecuencia
    f = 5000 #Hz
    #Periodo
    T = 1/f 
    #Puntos de muestreo
    p = 100
    #Muestreo por periodo
    tp = np.linspace(0, T, p)
    #Forma de onda portadora
    portadora = np.sin(2*np.pi*f*tp) 
    #Visualización de la onda
    plt.plot(tp, portadora)
    plt.title("Visualización de la onda")
    plt.xlabel("Tiempo  s")
    plt.show()
    #Frecuencia de muestreo 
    fm = p*f
    #Tiempo señal
    t = np.linspace(0, T*Nbits, Nbits*p)
    #Señal
    senal = np.zeros(t.shape)
    #Señal modulada
    for i, b in enumerate(bits):
        if int(b[0]) == 1:
            senal[i*p:(i+1)*p] = portadora
        if int(b[0]) == 0:
            senal[i*p:(i+1)*p] = -portadora
    pb = 5
    plt.figure()
    plt.plot(senal[0:pb*p])
    plt.title("Sección de señal modulada")
    plt.xlabel('Tiempo s')
    plt.ylabel('Amplitud')
    plt.show()
    #Calculo de la potencia intantanea

    Pins = senal**2

    #Potencia promedio

    Pot = integrate.trapz(Pins, t) / (Nbits*T)

    #Gráfica antes del ruido 
    fig=plt.figure(facecolor='w', edgecolor='k')
    fw, PSD = signal.welch(senal, fm, nperseg=1024)
    plt.semilogy(fw, PSD)
    plt.title("Señal antes del ruido")
    plt.xlabel('Frecuencia / Hz')
    plt.ylabel('Densidad espectral de potencia / V**2/Hz')
    plt.show()

    #SNR o Relación señal a ruido:
    valoresBER = []
    for SNR in range(-2, 4):

        #Potencia del ruido:
        Pn = Pot / (10**(SNR / 10 ))

        #Desviación estandar del ruido
        sigma = np.sqrt(Pn)

        #Simulación canal de ruido AWGN
        ruido = np.random.normal(0, sigma, senal.shape)
        #Simulacion del canal 
        F = senal + ruido
        #Visualización 
        pb = 5
        plt.figure()
        plt.plot(F[0:pb*p])
        plt.title("Visualización señal con ruido SNR =" + str(SNR) + "dB")
        plt.xlabel('Tiempo s')
        plt.ylabel('Amplitud')
        plt.show()
        #Gráfica Welch  
        #Gráfica después del ruido 
        fig=plt.figure(facecolor='w', edgecolor='k')
        fw, PSD = signal.welch(F, fm, nperseg=1024)
        plt.semilogy(fw, PSD)
        plt.title("Señal después del ruido con ruido SNR=" + str(SNR) + "dB")
        plt.xlabel('Frecuencia / Hz')
        plt.ylabel('Densidad espectral de potencia')
        plt.show()
        #Pseudo energía onda original
        E = np.sum(portadora**2)

        #Decodificación de la señal 
        #Bits recibidos:
        BitsR = np.zeros(Nbits)
        documento.seek(0)
        for i, b in enumerate(bits):
            Ep = np.sum(F[i*p:(i+1)*p] * portadora)
            if Ep > E/2:
                BitsR[i] = 1
            else:
                BitsR[i] = 0
        documento.seek(0)
        valores = []
        for b in bits: 
            valores.append(int(b[0]))
        error = np.sum(np.abs(valores - BitsR))
        BER = error / Nbits
        print("Ocurren ", error, "errores con un BER de: ", BER)
        valoresBER.append(BER)

    fig=plt.figure(facecolor='w', edgecolor='k')
    valoresSNR = np.linspace(-2, 3, 6)
    plt.scatter(valoresSNR, valoresBER)
    plt.xlabel("SNR (dB)")
    plt.ylabel("BER")
    plt.title("BER vs SNR")
    plt.show()
