import common.basicApi as basicApi
import time
import glob
import os

class Mail(object):
    def __init__(self, task):
        self.task = task
        self.title = ''
        self.body = []

    def execute(self):
        pass

    def _composeHead(self):
        self.body.append('Subject: %s\n' % self.title)
        self.body.append('From: AutoAnalyzer@sybase.com\n')
        self.body.append('To: %s@sybase.com\n' % self.task.user)
        self.body.append('Cc: bzheng@sybase.com,jingyaz@sybase.com,clei@sybase.com\n')
        self.body.append('MIME-VERSION: 1.0\n')
        self.body.append('Content-Type: multipart/mixed; boundary="GvXjxJ+pjyke8COw"\n')
        self.body.append('--GvXjxJ+pjyke8COw\n')
        self.body.append('Content-type: text/html; charset=utf-8\n')
        self.body.append('Content-Transfer-Encoding: 7bit\n')
        self.body.append('\n')
        self.body.append('<html>\n')
        self.body.append('<head>\n')
        self.body.append('<style type="text/css">h1 {color: red}</style>\n')
        self.body.append('</head>\n')
        self.body.append('\n')

    def _sendOut(self):
        mailFilePath = '%s/mail%s' % (self.task.aaLogDir, time.time())
        #Write back to disk
        basicApi.writeFile(mailFilePath, self.body)
        #clean mail body
        self.body = []
        #send out mail
        basicApi.execCmd('/usr/sbin/sendmail -t < ' + mailFilePath)
        pass


class TestsetReport(Mail):
    def __init__(self, task):
        super(TestsetReport, self).__init__(task)
        self.webSvr = 'http://winpw06.sjc.sap.corp:8080'
        self.bugSvr = 'http://www-dse.sjc.sap.corp/cgi-bin/websql/websql.dir/QTS/bugsheet.hts'

    def execute(self):
        #Find out all item from data base and send email.
        self._setTital()
        self._composeHead()
        self._composeBody()
        self._sendOut()

    def _setTital(self):
        self.title = 'Analysis summary of testset: %s ( %s, %s, %s)' % \
                     (self.task.testSet, self.task.tag, self.task.branch, self.task.platform)

    def _composeBody(self):
        self.body.append('<body>')
        self.body.append('Working directory: %s' % self.task.workDir)
        #Get related data from database 
        rtl = self.task.db.cateSummary.searchAutoAnalysisSummary([self.task.tag,
                                                                  self.task.platform,
                                                                  self.task.branch,
                                                                  self.task.testSet,
                                                                  self.task.tagTime])
        setSummaryList = rtl.getUnchangable()
        #Check auto attached failed case and manual attached failed case
        if setSummaryList:
            for row in setSummaryList:
                self._genRowReport(row)
        self.body.append('</body>\n')
        self.body.append('</html>\n')

    def _genRowReport(self, row):
        itemId = row[0]
        caseName = row[1]
        cr = row[2]
        user = row[3]
        casePathList = caseName.split('/')
        shortCaseName = casePathList[-1]
        jnlFile = self.task.getJnlStoreName(itemId)
        #Check if CR exist
        if cr == 'new':
            #CR does exist, so judge as new issue
            self.body.append('<p>\n')
            self.body.append('<b><a href="%s/ui5/getFile.html?filepath=%s">%s</a>:</b>\n' % (self.webSvr, jnlFile, caseName))
            self.body.append('<a href="%s/box/Analizer/getTRDInfo?testcase=%s">History</a>\n' % (self.webSvr, shortCaseName))
            self.body.append('<blockquote>\n')
            self.body.append('This failure is likely a new issue. please double check.<br>\n')
            openCrLink = '<a href="%s/ui5/openCR.html?itemId=%s">' % (self.webSvr, itemId)
            attachCrLink = '<a href="%s/ui5/connectedCR.html?itemId=%s">' % (self.webSvr, itemId)
            rerunCrLink = '<a href="%s/box/Analizer/runAnaFail?username=%s&itemId=%s">' % (self.webSvr, user, itemId)
            self.body.append('You can %sFile CR</a>, %sAttach CR</a> or %sRe-run</a>.\n' % (openCrLink, attachCrLink, rerunCrLink))
            self.body.append('</blockquote>\n')
            self.body.append('</p>\n')
            self.body.append('<br>\n')
        else:
            #CR exist, so auto attached
            self.body.append('<p style="color: LimeGreen">\n')
            getFileLink = '<a href="%s/ui5/getFile.html?filepath=%s">%s</a>' % (self.webSvr, jnlFile, caseName)
            self.body.append('<b>%s:</b>\n' % (getFileLink))
            self.body.append('<a href="%s/box/Analizer/getTRDInfo?testcase=%s">History</a>\n' % (self.webSvr, shortCaseName))
            self.body.append('<blockquote style="color: LimeGreen">\n')
            self.body.append('Test case has been attached to\n')
            self.body.append('<a href="%s?bugid=%s">CR%s</a> automatically.\n' % (self.bugSvr, cr, cr))
            self.body.append('</blockquote>\n')
            self.body.append('</p>\n')
            self.body.append('<br>\n')

    pass


class CycleReport(Mail):
    def __init__(self, task):
        super(CycleReport, self).__init__(task)
        pass
    pass


class SetupFailReport(Mail):
    def __init__(self, task):
        super(SetupFailReport, self).__init__(task)
        self.task.user = 'bzheng'

    def _setTital(self):
        self.title = 'Quasr setup failed for testset: %s ( %s, %s, %s)' % \
                     (self.task.testSet, self.task.tag, self.task.branch, self.task.platform)

    def _composeBody(self, resultDir):
        self.body.append('<body>')
        self.body.append('Working directory: %s<br><br>' % resultDir)
        self.body.append('Detail Summary of this failure:<br>')
        self.body.append('<blockquote style="color: red">\n')
        #Read setup failure summary
        for failureFile in glob.glob('%s/journal.setup.*' % resultDir):
            if os.path.exists(failureFile):
                for line in basicApi.readFile(failureFile):
                    self.body.append('%s<br>' % line)
        self.body.append('</blockquote>\n')
        self.body.append('</body>\n')
        self.body.append('</html>\n')
        pass

    def execute(self, resultDir):
        self._setTital()
        self._composeHead()
        self._composeBody(resultDir)
        self._sendOut()

    pass
