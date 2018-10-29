#Please run this testing under /usr/u/haow/gitCheckout/framework directory
import common.basicApi as basicApi
from aseAutoAnalyzer.task import AseTask
from aseAutoAnalyzer.summary import AseSummary
import pdb


if __name__ == '__main__':
    #read file
    #dataList = basicApi.readFile('/usr/u/haow/gitCheckout/framework/tools/cnn_result.csv')
    #call function
    summary = AseSummary()
    task = AseTask()
    sql = 'select distinct TAG, PLATFORM, BRANCH, TESTSET from "AUTO_ANALYZER"."aseAutoAnalyzer.db.cnn.views::V_RESULT"'
    task.db.cur.execute(sql)
    rtlList = task.db.cur.fetchall()
    #pdb.set_trace()
    for row in rtlList:
        task.tag = row[0]
        task.platform = row[1]
        task.branch = row[2]
        task.testSet = row[3]
        task.aaLogDir = '/tmp'
        task.user = 'haow'
        task.workDir = '/usr/u/haow/gitCheckout/framework'
        sql = '''select ID, TESTCASE from "AUTO_ANALYZER"."aseAutoAnalyzer.db.cnn.views::V_RESULT"
                 where TAG = '%s' and PLATFORM = '%s' and BRANCH = '%s' and TESTSET = '%s' 
              ''' % (task.tag, task.platform, task.branch, task.testSet)
        task.db.cur.execute(sql)
        task.caseList = task.db.cur.fetchall()
	    #Begin test
        summary.run(task)
        
