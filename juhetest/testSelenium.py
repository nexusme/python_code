from selenium import webdriver
import selenium


def execute(script, args):
    driver.execute('executePhantomScript', {'script': script, 'args': args})


driver = webdriver.PhantomJS('/Users/nexus/phantomjs-2.1.1-macosx/bin/phantomjs')
# hack while the python interface lags
driver.command_executor._commands['executePhantomScript'] = ('POST', '/session/$sessionId/phantom/execute')
driver.get('http://10.0.32.28:7001/memberAnalysis/groups')
# set page format
# inside the execution script, webpage is "this"
pageFormat = '''this.paperSize = {format: "Legal", orientation: "portrait" };'''
execute(pageFormat, [])
# render current page
render = '''this.render("out.pdf")'''
execute(render, [])
print('已完成')