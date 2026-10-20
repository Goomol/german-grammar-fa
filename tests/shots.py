import sys
import pathlib
from playwright.sync_api import sync_playwright
import pathlib; U=(pathlib.Path(__file__).resolve().parent.parent/'dist'/'german-grammar-fa.html').as_uri()
jobs=[a.split('=',1) for a in sys.argv[1:]]  # name=WxH#hash@scroll
with sync_playwright() as p:
    b=p.chromium.launch(); errs=[]
    for name,spec in jobs:
        size,_,rest=spec.partition('#'); h,_,sc=rest.partition('@')
        w,hh=map(int,size.split('x'))
        pg=b.new_page(viewport={'width':w,'height':hh},device_scale_factor=1 if w>600 else 2)
        pg.on('pageerror',lambda e: errs.append(str(e)))
        pg.goto(U+'#'+h); pg.wait_for_timeout(400)
        if sc: pg.mouse.wheel(0,int(sc)); pg.wait_for_timeout(300)
        pg.screenshot(path=fstr(pathlib.Path(__file__).resolve().parent.parent/'shots')+'/{name}.png'); pg.close()
    print('errors:',errs)
