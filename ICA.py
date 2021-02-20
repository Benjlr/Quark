
from IBpyFuncs import IBapi
from datetime import datetime, timedelta


etfs = [ 'EEM', 'EFA', 'EWA', 'EWC', 'EWJ', 'EWZ', 'FAS', 'FAZ', 'FXI',
'GDX', 'GLD', 'IGE', 'IWM', 'IYR', 'QID', 'QQQ', 'SDS', 'SKF','SPY', 'SSO', 'TZA', 'UNG',
'USO', 'VWO', 'VXX', 'XLE', 'XLF', 'XLI', 'XRT' ]

etfs2 = [ 'EWA', 'EWC']
#from the year of 2013–2015

app = IBapi()
#for e in etfs2:
app.createStockContract('60 D','', '15 mins', 'EWA', exch='ARCA' )



app.disconnect()