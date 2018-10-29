import sys
import common.basicApi as basicApi
from aseAutoAnalyzer.framework import AseFramework
from aseAutoAnalyzer.task import AseTask
from aseAutoAnalyzer.setup import AseSetup
from aseAutoAnalyzer.analysis import AseAnalysis
from aseAutoAnalyzer.summary import AseSummary
#from aseAutoAnalyzer.dbAccess import HanaAccess
from aseAutoAnalyzer.TFIDF.analyzer import TFIDF
from aseAutoAnalyzer.CNN.analyzer import CNN





if __name__ == '__main__':
    try:
        # argList = [workDir, testSet, tag, user, platform, bit, lockSch, pageSize, branch, tagTime]
        #argList = ['/remote/asepw_archive3/grid/project/zhaox_ase160sp03_s1_nt64/func.lam.demo/workdir/run_06_12_03_24/',
        #           'ckmats_carina',
        #           'tagAutoAnalyzer',
        #           'yuma',
        #           'lam',
        #           '64',
        #           'dr',
        #           '16k',
        #           'ase160sp02plx',
        #           '2017/5/14']
        argList = sys.argv[1:]
        tsk = AseTask(analyzers=[TFIDF, CNN])
        tsk.initial(argList)
        ####################
        print('Begin testing ...')
        clsList = [AseSetup, AseAnalysis, AseSummary]
        fw = AseFramework(clsList)
        fw.run(tsk)
        print('End testing ...')

    except basicApi.PROCESS_ERROR as err:
        print err

