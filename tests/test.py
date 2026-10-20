import pathlib
from playwright.sync_api import sync_playwright
import pathlib; U=(pathlib.Path(__file__).resolve().parent.parent/'dist'/'german-grammar-fa.html').as_uri()
with sync_playwright() as p:
    b=p.chromium.launch(); errs=[]
    pg=b.new_page(viewport={'width':1440,'height':900})
    pg.on('pageerror',lambda e: errs.append(str(e))); pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
    pg.goto(U); pg.wait_for_timeout(400); pg.screenshot(path=str(pathlib.Path(__file__).resolve().parent.parent/'shots')+'/d-home.png')
    # search
    pg.click('#q'); pg.keyboard.type('Akkusativ را'); pg.wait_for_timeout(300); pg.screenshot(path=str(pathlib.Path(__file__).resolve().parent.parent/'shots')+'/d-search.png')
    print('results:', pg.locator('#sp a[data-k]').count())
    pg.keyboard.press('Enter'); pg.wait_for_timeout(500); print('hash after enter', pg.evaluate('location.hash'), 'marks', pg.locator('mark.hit').count())
    pg.screenshot(path=str(pathlib.Path(__file__).resolve().parent.parent/'shots')+'/d-searchjump.png')
    # xref follow + back fab
    pg.goto(U+'#/l/a21-weil'); pg.wait_for_timeout(300)
    pg.mouse.wheel(0,900); pg.wait_for_timeout(200)
    y0=pg.evaluate('scrollY')
    pg.locator('.l-body a.xref').first.click(); pg.wait_for_timeout(400)
    print('after xref', pg.evaluate('location.hash'), 'fab', pg.locator('#fab.show').count(), pg.locator('#fab span').inner_text())
    pg.screenshot(path=str(pathlib.Path(__file__).resolve().parent.parent/'shots')+'/d-xref.png')
    pg.click('#fab'); pg.wait_for_timeout(500)
    print('back to', pg.evaluate('location.hash'), 'scroll', pg.evaluate('scrollY'), 'was', y0, 'fab', pg.locator('#fab.show').count())
    # done button
    pg.click('#doneBtn'); pg.wait_for_timeout(200); print('done count', pg.evaluate("JSON.parse(localStorage.getItem('gg:done')).length"))
    # level page
    pg.goto(U+'#/v/B1.1'); pg.wait_for_timeout(300); pg.screenshot(path=str(pathlib.Path(__file__).resolve().parent.parent/'shots')+'/d-level.png')
    # dark
    pg.goto(U+'#/l/b11-genitiv'); pg.click('#themeBtn'); pg.wait_for_timeout(300); pg.screenshot(path=str(pathlib.Path(__file__).resolve().parent.parent/'shots')+'/d-dark.png')
    pg.mouse.wheel(0,2500); pg.wait_for_timeout(300); pg.screenshot(path=str(pathlib.Path(__file__).resolve().parent.parent/'shots')+'/d-dark2.png')
    # mobile
    m=b.new_page(viewport={'width':390,'height':844},device_scale_factor=2,is_mobile=True,has_touch=True)
    m.on('pageerror',lambda e: errs.append(str(e)))
    m.goto(U); m.wait_for_timeout(400); m.screenshot(path=str(pathlib.Path(__file__).resolve().parent.parent/'shots')+'/m-home.png')
    m.click('#menuBtn'); m.wait_for_timeout(400); m.screenshot(path=str(pathlib.Path(__file__).resolve().parent.parent/'shots')+'/m-drawer.png')
    m.locator('.d-lv summary').nth(3).click(); m.wait_for_timeout(200)
    m.locator('.d-list a[data-id="a22-relativ"]').click(); m.wait_for_timeout(400); m.screenshot(path=str(pathlib.Path(__file__).resolve().parent.parent/'shots')+'/m-lesson.png')
    m.mouse.wheel(0,1800); m.wait_for_timeout(300); m.screenshot(path=str(pathlib.Path(__file__).resolve().parent.parent/'shots')+'/m-lesson2.png')
    m.click('#searchOpen'); m.wait_for_timeout(200); m.keyboard.type('weil'); m.wait_for_timeout(300); m.screenshot(path=str(pathlib.Path(__file__).resolve().parent.parent/'shots')+'/m-search.png')
    m.goto(U+'#/l/x-verben'); m.wait_for_timeout(300); m.mouse.wheel(0,600); m.wait_for_timeout(200); m.screenshot(path=str(pathlib.Path(__file__).resolve().parent.parent/'shots')+'/m-table.png')
    print('overflow-x', m.evaluate('document.documentElement.scrollWidth'), m.evaluate('innerWidth'))
    print('errors:',errs)
