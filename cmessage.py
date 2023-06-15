from enum import Enum

class Cmessage(object):
    '''
    classdocs
    '''
    # Constance
    MCMDS = Enum('MCMDS', {'CRE8': 'CRE8', 'LGIN': 'LGIN', 'LOUT': 'LOUT', 'ADDM': 'ADDM', 'REFU': 'REFU',
                           'EXIT': 'EXIT', 'PAY2': 'PAY2', 'GOOD': 'GOOD', 'ERRO': 'ERRO', 'INTR': 'INTR',
                           'REQT': 'REQT', 'CANC': 'CANC', 'SHBL': 'SHBL', 'CKHI': 'CKHI', 'PROC': 'PROC'})

    PJOIN = '&'
    VJOIN = '{}={}'
    VJOIN1 = '='

    def __init__(self):
        '''
        Constructor
        '''
        self._type = Cmessage.MCMDS['GOOD']
        self._params = {}
    
    def __str__(self) -> str:
        '''
        Stringify - marshal
        '''
        return self.marshal()
    
    def reset(self):
        self._type = Cmessage.MCMDS['GOOD']
        self._params.clear()
        self._params = {}
    
    def setType(self, mtype: str):
        self._type = Cmessage.MCMDS[mtype]
        
    def getType(self) -> str:
        return self._type.value
    
    def addParam(self, name: str, value: str):
        self._params[name] = value
        
    def getParam(self, name: str) -> str:
        return self._params[name]
    
    def marshal(self) -> str:
        size = 0
        params = ''
        if (self._params):        
            pairs = [Cmessage.VJOIN.format(k,v) for (k, v) in self._params.items()]
            params = Cmessage.PJOIN.join(pairs)
            size = len(params)
        return '{:04}{}{}'.format(size,self._type.value,params)
    
    def unmarshal(self, value: str):
        self.reset()
        if value:
            params = value.split(Cmessage.PJOIN)
            for p in params:
                k,v = p.split(Cmessage.VJOIN1)
                self._params[k] = v