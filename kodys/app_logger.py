# -*- coding: utf-8 -*-

import sys


def _fn():
    '''
    returns current function name
    '''
    func_name = sys._getframe(1).f_code.co_name
    return func_name


def _setmsg(success_msg,error_msg, flag):
    '''construct and return success or error messages based on the flag
        success_msg : success message
        error_msg : error message
        flag : result flag
    '''
    msg=''
    if flag:
        msg = success_msg
    else:
        msg = error_msg
    return flag, msg


def get_template_name(request, template_name, options=dict()):
    '''
        return function with .html
    '''
    if request.resolver_match.app_names:
        tn= request.resolver_match.app_names[-1]+"/"+template_name+'.html'
    else:
        tn= template_name+'.html'

    if 'common_template' in options and options['common_template']:
        tn= template_name+'.html'

    # if settings.SA_UTILAPP_IS_MOBILE_TEMPLATE_NEEDED:
    #     if request.is_mobile:
    #         tn = settings.SA_UTILAPP_MOBILE_TEMPLATE_STARTS_WITH+tn

    return tn


def start_log(request, fn):
    '''
        print current function loading msg
    '''
    log_msg = "{0} method is loading....".format(fn)
    return log_msg


def end_log(request, fn):
    '''
        print current function loading done msg
    '''
    log_msg = "{0} method is loading done....".format(fn)
    return log_msg


def error_log(request,line_no, exp):
    '''
        print error message with line number
    '''
    err_msg = 'Error at %s:%s' %(line_no,exp)
    return err_msg


def internal_log(request, msg):
    '''
        print developer logs
    '''
    if request:
        internal_msg = "{0} {1}".format(request.resolver_match.app_name, msg)
    else:
        internal_msg = "{0}".format(msg)
    return internal_msg


def warning_log(request, msg):
    '''
        print warning logs
    '''
    warning_msg = "{0}".format(msg)
    return warning_msg

