import pathlib
from playwright.sync_api import sync_playwright
import pathlib; U=(pathlib.Path(__file__).resolve().parent.parent/'dist'/'german-grammar-fa.html').as_uri()
qs=['Akkusativ را','را','شدن','weil','صفت ملکی','halb','doch','kein','لازم نیست','dass','Plusquamperfekt','ماضی بعید','موصولی','wo','zu','um zu','Genitiv','گذاشتن','strasse','fuer']
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1300,'height':900}); errs=[]
    pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.goto(U); pg.wait_for_timeout(300)
    for q in qs:
        pg.fill('#q',q); pg.wait_for_timeout(120)
        items=pg.locator('#sp a[data-k]')
        n=items.count()
        tops=[items.nth(i).get_attribute('href') for i in range(min(3,n))]
        print(f'{q!r:20} {n:3} ', tops)
    print(errs)
