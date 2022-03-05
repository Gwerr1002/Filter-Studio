
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 12:28:51 2022

@author: Gerardo Ortíz Montufar

This work is licensed under the Creative Commons Attribution 4.0
International License. To view a copy of this license, visit
http://creativecommons.org/licenses/by/4.0/ or send a letter to
Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
"""

from numpy import pi
from Resources.Filters import Filter
from Resources.PFilter import frecResponse
from Resources.DesignerGUI import Ui_MainWindow, QtWidgets

class MainWindow(QtWidgets.QMainWindow, frecResponse):
    
    def __init__(self, parent = None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # Setup matplotlib canvas to hold four graphs in the given layout, with a toolbar
        self.ui.MagCanvas.setupCanvas(toolbar = True)
        self.ui.PhaseCanvas.setupCanvas(toolbar = True)
        self.ui.NyCanvas.setupCanvas(toolbar = True)
        
        self.opciones = {
            "Butterworth": Filter.Butterworth,
            "Chebyshev": Filter.Chebyshev,
            "FIR": Filter.FIR,
            }
        self.Tipo = self.opciones["FIR"]
        self.HPoLP = False
        self.Ap = 1
        self.Ap_max = 2
        self.Ar = 60
        self.fp = 1e+3
        self.fr = 1.5e+3
        self.fs = 5e+3
        self.cutf = float()
        self.Filtro = []
        
        self.ui.Ap.setMinimum(int(self.Ap))
        self.setAp()
        self.ui.Ap.setMinimum(.01)
        self.ui.Ar.setMinimum(int(self.Ar))
        self.setAr()
        self.ui.Ar.setMinimum(1)
        self.ui.fr.setMinimum(int(self.fr))
        self.setfr()
        self.ui.fr.setMinimum(1)
        self.ui.fp.setMinimum(self.fp)
        self.setfp()
        self.ui.fp.setMinimum(1)
        self.ui.fs.setMinimum(int(self.fs))
        self.setfs()
        self.ui.fs.setMinimum(1)
        
        self.Generar()
        
        self.ui.Tfiltro.currentIndexChanged.connect(self.EN_DIS)
        self.ui.HP.stateChanged.connect(self.setHPoLP)
        self.ui.IIR.stateChanged.connect(self.EN_DIS)
        self.ui.Ap.valueChanged.connect(self.setAp)
        self.ui.Ar.valueChanged.connect(self.setAr)
        self.ui.fp.valueChanged.connect(self.setfp)
        self.ui.fr.valueChanged.connect(self.setfr)
        self.ui.fs.valueChanged.connect(self.setfs)
        self.ui.GenFiltro.clicked.connect(self.Generar)
        self.ui.Ap_slider.sliderMoved.connect(self.Slider)
        self.ui.Ar_slider.sliderMoved.connect(self.Slider)
        self.ui.fr_slider.sliderMoved.connect(self.Slider)
        self.ui.fp_slider.sliderMoved.connect(self.Slider)
        
        
        
    def EN_DIS(self):
        key = self.ui.Tfiltro.currentText()
        self.Tipo = self.opciones[key]
        if  (key == "Butterworth" or key == "Chebyshev") and (not self.ui.IIR.isChecked()):
            self.ui.fs.setEnabled(False)
            self.ui.fs.setValue(0)
            self.ui.IIR.setEnabled(True)
        elif (key == "Butterworth" or key == "Chebyshev") and (self.ui.IIR.isChecked()):
            self.ui.fs.setEnabled(True)
            self.ui.fs.setValue(0)
            self.ui.IIR.setEnabled(True)
        elif key == "FIR":
            self.ui.fs.setEnabled(True)
            self.ui.fs.setValue(0)
            self.ui.IIR.setEnabled(False)
    
    def setHPoLP(self):
        if self.ui.HP.isChecked():
            self.HPoLP = True
        else:
            self.HPoLP = False
    
    def setAp(self):
        self.Ap = self.ui.Ap.value()
        self.Ap_max = 2*self.Ap
        self.ui.Ap_slider.setMaximum(100)
        self.ui.Ap_slider.setSliderPosition(50)
    
    def setAr(self):
        self.Ar = self.ui.Ar.value()
        self.ui.Ar_slider.setMaximum(int(2*self.Ar))
        self.ui.Ar_slider.setSliderPosition(int(self.Ar))
        
    def setfp(self):
        self.fp = self.ui.fp.value()
        self.ui.fp_slider.setMaximum(int(10*self.fp))
        self.ui.fp_slider.setMinimum(int(.1*self.fp))
        self.ui.fp_slider.setTickInterval(int(.1*self.fp))
        self.ui.fp_slider.setSliderPosition(int(self.fp))
        
    def setfr(self):
        self.fr = self.ui.fr.value()
        self.ui.fr_slider.setMaximum(int(10*self.fr))
        self.ui.fr_slider.setMinimum(int(.1*self.fr))
        self.ui.fp_slider.setTickInterval(int(.1*self.fp))
        self.ui.fr_slider.setSliderPosition(int(self.fr))
        
    def setfs(self):
        self.fs = self.ui.fs.value()
        
    def Generar(self):
        key = self.ui.Tfiltro.currentText()
        try:
            if key == "Butterworth" or key == "Chebyshev":
                self.cutf, self.Filtro = self.Tipo(self.Ap, self.Ar, self.fp, self.fr,self.HPoLP)
                if self.ui.IIR.isChecked():
                    self.Filtro = Filter.BilinearTF(self.fs, self.Filtro)
                    Response = super().IIR(self.Filtro, self.cutf, self.fs)
                else:
                    Response = super().Fltr(self.Filtro, self.cutf)      
            elif key == "FIR":
                self.cutf, self.Filtro = self.Tipo(self.Ap, self.Ar, self.fp, self.fr, self.fs, self.HPoLP)
                Response = super().FIR(self.Filtro)
            
            self.MostrarSecciones()
            self.ActualizaCanvas(Response)
        
        except ZeroDivisionError:
            self.MostrarSecciones("Seleccione numeros mayores que cero.")
            
        except Exception as e:
            self.MostrarSecciones("Seleccione valores adecuados sin fuera de limite o que sobrepasen a las especificaciones.\n{}".format(e))
    
    def MostrarSecciones(self, mensaje = None):
        if mensaje:
            self.ui.plainTextEdit.setPlainText(mensaje)
        else:
            mensaje = "Secciones del Filtro: {}\n".format(len(self.Filtro))
            
            for sec in self.Filtro:
                mensaje += "{}\n".format(sec)
            
        self.ui.plainTextEdit.setPlainText(mensaje)
        
    def ActualizaCanvas(self, Response):
        self.ActualizaMag((Response[0],Response[1]))
        self.ActualizaFas((Response[0], Response[2]))
        self.ActualizaNy(Response[3])
        
    def ActualizaMag(self, Response):
        key = self.ui.Tfiltro.currentText()
        ax = self.ui.MagCanvas.axes[0]
        ax.clear()
        ax.semilogx(Response[0], Response[1])
        if key == "Butterworth" or key == "Chebyshev":
            ax.axis([2*self.fp*.1,self.fr*10/2,-self.Ar-self.Ar/2,10])
            ax.set_xlabel("f ($Hz$)")
            ax.axvline(self.cutf,linestyle=':',c='r',label='$f_c = ${}'.format(round(self.cutf,2)))
            ax.axvline(self.fr,linestyle=':',c='g',label='$f_r = ${}'.format(round(self.fr,2)))
            ax.axvline(self.fp,linestyle=':',c='c',label='$f_p = ${}'.format(round(self.fp,2)))
            
        elif key == "FIR":
            wp, wr = self.fp*2*pi/self.fs, self.fr*2*pi/self.fs
            ax.axis([3*wp*.1/pi,1,-self.Ar-self.Ar/2,10])
            ax.set_xlabel("'$\omega/\pi$ rad'")
            ax.axvline(self.cutf/pi,linestyle=':',c='r',label='$w_c = ${}'.format(round(self.cutf,2)))
            ax.axvline(wr/pi,linestyle=':',c='g',label='$w_r = ${}'.format(round(wr,2)))
            ax.axvline(wp/pi,linestyle=':',c='c',label='$w_p = ${}'.format(round(wp,2)))
        
        ax.axhline(-self.Ap,linestyle=':',c='c',label='$Ap = $ {}'.format(-self.Ap))
        ax.axhline(-self.Ar,linestyle=':',c='g',label='$Ar = $ {}'.format(-self.Ar))
        ax.axhline(-3,linestyle=':',c='r',label='-3 dB')
        ax.set_ylabel("Gain ($dB$)")
        ax.legend()
        ax.grid()
        self.ui.MagCanvas.draw()
    
    def ActualizaFas(self, Response):
        
        key = self.ui.Tfiltro.currentText()
        ax = self.ui.PhaseCanvas.axes[0]
        ax.clear()
        ax.semilogx(Response[0], Response[1]*180/pi)
        if key == "Butterworth" or key == "Chebyshev":
            ax.axis([2*self.fp*.1,self.fr*10/2,-200,200])
            ax.set_xlabel("f ($Hz$)")
            ax.axvline(self.cutf,linestyle=':',c='r',label='$f_c = ${}'.format(round(self.cutf,2)))
            
        elif key == "FIR":
            wp = self.fp*2*pi/self.fs
            ax.axis([3*wp*.1/pi,1,-200,200])
            ax.set_xlabel("'$\omega/\pi$ rad'")
            ax.axvline(self.cutf/pi,linestyle=':',c='r',label='$w_c = ${}'.format(round(self.cutf,2)))
        
        ax.set_ylabel("Phase ($deg$)")
        ax.legend()
        ax.grid()
        self.ui.PhaseCanvas.draw()
        
    def ActualizaNy(self,Response):
        ax = self.ui.NyCanvas.axes[0]
        ax.clear()
        ax.plot(Response.imag,Response.real, c = "#FF8300")
        ax.plot(Response.imag,-Response.real, c = "#FF8300")
        ax.set_xlabel("Real")
        ax.set_ylabel("Imag")
        ax.grid()
        self.ui.NyCanvas.draw()
    
    def Slider(self):
        self.Ap = 2*self.Ap_max*self.ui.Ap_slider.value()/100
        self.Ar = self.ui.Ar_slider.value()
        self.fp = self.ui.fp_slider.value()
        self.fr = self.ui.fr_slider.value()
        self.Generar()
    

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
