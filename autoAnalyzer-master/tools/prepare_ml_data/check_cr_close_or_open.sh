
#!/bin/sh

# $1 branch_name  $2 start_time $3 end_time

CR=$1
echo $CR



SAP_JRE7_64="/remote/aseqa_archive2/bzheng/sp63_lam/shared/SAPJRE-7_1_018_64BIT"
export SAP_JRE7_64

SYBASE_OCS="OCS-15_0"
export SYBASE_OCS

SAP_JRE7="/remote/aseqa_archive2/bzheng/sp63_lam/shared/SAPJRE-7_1_018_64BIT"
export SAP_JRE7

SAP_JRE7_32="/remote/aseqa_archive2/bzheng/sp63_lam/shared/SAPJRE-7_1_018_32BIT"
export SAP_JRE7_32

SCC_JAVA_HOME="/remote/aseqa_archive2/bzheng/sp63_lam/shared/SAPJRE-7_1_018_64BIT"
export SCC_JAVA_HOME

SYBASE_WS="WS-15_0"
export SYBASE_WS

INCLUDE="/remote/aseqa_archive2/bzheng/sp63_lam/OCS-15_0/include"
export INCLUDE

LIB="/remote/aseqa_archive2/bzheng/sp63_lam/OCS-15_0/lib"
export LIB

PATH="/remote/aseqa_archive2/bzheng/sp63_lam/OCS-15_0/bin:/remote/aseqa_archive2/bzheng/sp63_lam/DBISQL/bin:/remote/aseqa_archive2/bzheng/sp63_lam/ASE-15_0/bin:/remote/aseqa_archive2/bzheng/sp63_lam/ASE-15_0/install:/remote/aseqa_archive2/bzheng/sp63_lam/ASE-15_0/jobscheduler/bin;$PATH"
export PATH

LD_LIBRARY_PATH="/remote/aseqa_archive2/bzheng/sp63_lam/OCS-15_0/lib:/remote/aseqa_archive2/bzheng/sp63_lam/OCS-15_0/lib3p64:/remote/aseqa_archive2/bzheng/sp63_lam/OCS-15_0/lib3p:/remote/aseqa_archive2/bzheng/sp63_lam/DataAccess/ODBC/lib:/remote/aseqa_archive2/bzheng/sp63_lam/DataAccess64/ODBC/lib:/remote/aseqa_archive2/bzheng/sp63_lam/ASE-15_0/lib:$LD_LIBRARY_PATH"
export LD_LIBRARY_PATH

SYBASE="/remote/aseqa_archive2/bzheng/sp63_lam"
export SYBASE

SYBASE_ASE="ASE-15_0"
export SYBASE_ASE


isql -U tamqa -P only4qa -S lsvxc0132.sjc.sap.corp:5000 <<EOF
use qts_db
go

select res_status from resolution_search_vu where bug_id=$CR

go
EOF
