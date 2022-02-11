# -*- coding: utf-8 -*-
import enum
import numpy as np
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d
from scipy.interpolate import splrep, splev

class LogicODVariant(enum.Enum):
    useBlackOD = 1
    useWhiteOD = 2
    useBlackAndWhite = 3
    useDummy = 99

class LogicCurveVariants(enum.Enum):
    useCurveFit = 1
    useInterp1d = 2
    useSplev = 3
    useScikit = 4

class LogicCurveFitsVariant(enum.Enum):
    useSerejaVariant = 1
    usePol3 = 3
    usePol4 = 4
    usePol5 = 5

def fitFuncSereja(od, a, b, c):
    return (a / (od - b)) + c

def fitFuncPol3(od, a, b, c, d):
    func = np.poly1d([a,b,c, d])
    return func(od)

def fitFuncPol4(od, a, b, c, d, e):
    func = np.poly1d([a,b,c, d, e])
    return func(od)

def fitFuncPol5(od, a, b, c, d, e, f):
    func = np.poly1d([a,b,c, d, e, f])
    return func(od)

class LogicParser(object):
    def __init__(self, ods, doses, odVariant=LogicODVariant.useWhiteOD, curveVariant=LogicCurveVariants.useInterp1d, **kwargs):
        self.__dict__['odVariant'] = odVariant
        self.__dict__['curveVariant'] = curveVariant
        if curveVariant == LogicCurveVariants.useCurveFit:
            self.__dict__['fitFunc'] = kwargs.get('curveFitVariant', LogicCurveFitsVariant.usePol5)

        self.calibOds = ods
        self.calibDoses = doses
        self._prepare()

    def _prepare(self):
        # p_opt, p_cov = curve_fit(fit_func2, x, y)
        if self.__dict__['curveVariant'] == LogicCurveVariants.useCurveFit:
            if self.__dict__['fitFunc'] == LogicCurveFitsVariant.useSerejaVariant:
                self._popt, self._pcov = curve_fit(fitFuncSereja, self.calibOds, self.calibDoses)
            elif self.__dict__['fitFunc'] == LogicCurveFitsVariant.usePol3:
                self._popt, self._pcov = curve_fit(fitFuncPol3, self.calibOds, self.calibDoses)
            elif self.__dict__['fitFunc'] == LogicCurveFitsVariant.usePol4:
                self._popt, self._pcov = curve_fit(fitFuncPol4, self.calibOds, self.calibDoses)
            elif self.__dict__['fitFunc'] == LogicCurveFitsVariant.usePol5:
                self._popt, self._pcov = curve_fit(fitFuncPol5, self.calibOds, self.calibDoses)
        elif self.__dict__['curveVariant'] == LogicCurveVariants.useInterp1d:
            self.interp = interp1d(self.calibOds, self.calibDoses)
        elif self.__dict__['curveVariant'] == LogicCurveVariants.useSplev:
            self.splrep = splrep(self.calibOds, self.calibDoses)
            #f2a = splrep(x, y, s=0)
            #f2 = splev(np.linspace(0.0, 21.0, 1000), f2a, der=0)
        pass

    def preparePixValue(self, PV):
        if self.__dict__['odVariant'] == LogicODVariant.useBlackOD:
            medBckg = 2392.0
            medUnexp = 41087.0 # @todo: get
            return np.log10((medUnexp - medBckg) / (PV - medBckg))
        elif self.__dict__['odVariant'] == LogicODVariant.useWhiteOD:
            medWhite = 65525.0
            medUnexp = 41202.0 # @todo: get
            return np.log10(medWhite / PV) - np.log10(medWhite / medUnexp)
        elif self.__dict__['odVariant'] == LogicODVariant.useDummy:
            return np.log10(1./ PV)


    def evaluate(self, value):
        od = self.preparePixValue(value)
        if self.__dict__['curveVariant'] == LogicCurveVariants.useCurveFit:
            if self.__dict__['fitFunc'] == LogicCurveFitsVariant.useSerejaVariant:
                return fitFuncSereja(od, *self._popt)
            elif self.__dict__['fitFunc'] == LogicCurveFitsVariant.usePol3:
                return fitFuncPol3(od, *self._popt)
            elif self.__dict__['fitFunc'] == LogicCurveFitsVariant.usePol4:
                return fitFuncPol4(od, *self._popt)
            elif self.__dict__['fitFunc'] == LogicCurveFitsVariant.usePol5:
                return fitFuncPol5(od, *self._popt)
        elif self.__dict__['curveVariant'] == LogicCurveVariants.useInterp1d:
            return self.interp(od)
        elif self.__dict__['curveVariant'] == LogicCurveVariants.useSplev:
            return splev(od, self.splrep, der=0)
        pass

if __name__ == '__main__':
    from database import dbProxy
    from pymongo import MongoClient

    client = MongoClient('mongodb://10.1.30.32:27017/')
    db = client['EBT_films_dose']
    collectionTifProvider = db['tifProvider']

    vl = dbProxy.getData4CalibrationCurveWithDoseHighLimit(collectionTifProvider, 'Co-60 (MRRC)',
                                                           '05062003', 24, 50.0)
    doses = []
    ods = []
    for dose, od in enumerate(vl):
        doses.append(dose)
        ods.append(od)

    obj1 = LogicParser(ods, doses, LogicODVariant.useWhiteOD, LogicCurveVariants.useInterp1d)
    print(obj1.evaluate(0.4))

    obj2 = LogicParser(ods, doses, LogicODVariant.useWhiteOD, LogicCurveVariants.useCurveFit, fitFunc=LogicCurveFitsVariant.useSerejaVariant)
    print(obj2.evaluate(0.4))