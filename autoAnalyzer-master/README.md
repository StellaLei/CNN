Note:
1, This program can only be running on machine lsvxc0033.sjc.sap.corp.
   Because of tensorflow and yaml package are only installed on this machine.

2, We use config.yml as config file. This file can specify basic running env of our program.

3, We use main.py as the autoAnalyzer entry.
   Usage:
   python main.py <workdir> <test_set> <test_tag> <failure_analyzer)> <test_platform> <bit> <lock_schema> <page_size> <test_branch> <tag_date>
   Example:
   python main.py /remote/asepw_archive2/grid/project/bzheng_sp03pl02_lam/func.lam.demo/workdir/run_08_07_22_41 corona_imrs_encr ase160sp03pl02_c1 zfu lam 64 dp 2k ase160sp03plx 2017/08/05

5, We use busybox.py as action entry.
   Support following feature:
   * reCalculate - Update leanring mode for both CNN and TFIDF
   * test        - Testing new created features 

6, We must need ENV for calling some action from busybox:
   setenv SYBASE /remote/asepw_archive2/grid/autoAnalyzer/aseClient/ase160sp02plx_python_driver_libs
   setenv LD_LIBRARY_PATH /remote/asepw_archive2/grid/autoAnalyzer/aseClient/ase160sp02plx_python_driver_libs/OCS-16_0/lib
