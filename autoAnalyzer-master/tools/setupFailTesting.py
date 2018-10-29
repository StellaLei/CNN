from common.environment import Env
from actions.mail import SetupFailReport
from aseAutoAnalyzer.task import AseTask
import pdb


if __name__ == '__main__':
    task = AseTask()
    task.tag = 'asecorona_pw'
    task.branch = 'ase160sp03plx' 
    task.platform = 'lam,64'
    task.testSet = 'bharani_stmt_2M_O'
    task.aaLogDir = '/tmp'
    resultDir = '/remote/asepw_archive1/grid/project/fanf_SP03_PL02_RS_PW_lam/func.lam.demo/workdir/run_09_11_20_05/bharani_pll_cr_ind__dr_16k_SMP_09_11_22.49.36/result.bharani_pll_cr_ind'
    pdb.set_trace()
    sfr = SetupFailReport(task)
    sfr.execute(resultDir)
