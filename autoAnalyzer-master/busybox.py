
from optparse import OptionParser
from aseAutoAnalyzer.action import AseAction


if __name__ == '__main__':
    parser = OptionParser()
    #Define options
    parser.add_option('-r', '--rcal', action='store_true', dest='rcal', default=False,
                      help='Re-calculate learning model for both TFIDF and CNN')
    parser.add_option('-t', '--utrd', action='store_true', dest='utrd', default=False,
                      help='Update TRD with autoAnalyzer predict result')
    parser.add_option('-u','--uitm', action='store_true', dest='uitm', default=False,
                      help='Manually update test case item with attached CR')
    parser.add_option('-d', '--ditm', action='store_true', dest='ditm', default=False,
                      help='Manually delete test case item')
    parser.add_option('-m', '--move', action='store_true', dest='move', default=False,
                      help='Manually remove the specific CR and related items')
    parser.add_option('-c', '--ccyc', action='store_true', dest='ccyc', default=False,
                      help='Sync and clean up autoAnalyzer database with cycle report')
    parser.add_option('-a', '--ausr', action='store_true', dest='ausr', default=False,
                      help='Re-assign user for specific test sets')
    parser.add_option('-s', '--ssum', action='store_true', dest='ssum', default=False,
                      help='Send mail to test set owner for failed test case summary')
    #Initial option and args
    (options, args) = parser.parse_args()
    #Initial action class
    action = AseAction()
    #Begin branch selection
    if options.rcal:
        #Call re-calculate function
        action.reCalculate()
    elif options.utrd:
        #Call update TRD function
        itemId, cr = args
        action.updTRD(itemId, cr)
    elif options.uitm:
        #Call update item function
        itemId, cr = args
        action.updateItem(itemId, cr)
    elif options.ditm:
        #Call delete item function
        itemId = args[0]
        action.deleteItem(itemId)
    elif options.move:
        #Call remove cr function
        cr = args[0]
        action.removeCR(cr)
    elif options.ccyc:
        #Clean cycle db after cycle finished
        action.cleanUp()
    elif options.ausr:
        #Call re-assign user function
        assignment = args[0]
        action.reAssignUsr(assignment)
    elif options.ssum:
        tag = args[0]
        #Send mail for test set summary
        action.sendMailSetSummary(tag)
    else:
        #Default show help
        parser.print_help()


