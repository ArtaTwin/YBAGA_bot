#print("__init__ functions_reqwest")
from functions_reqwest import _info, _photo, form_controller
from functions_reqwest import others, ban_func


dict_function= {
    "info" : _info.info, "i" : _info.info,
    "map" : _photo.photo, "m" : _photo.photo,
    "form" : form_controller.form
}

list_function= list(dict_function)

dict_admin_function= {
    "ban" : ban_func.ban_user, "b" : ban_func.ban_user,
    "unban" : ban_func.unban_user, "ub" : ban_func.unban_user,
    "get_ban_list": ban_func.get_ban_list, "gbl" : ban_func.get_ban_list,
    "as" : others.get_all_SubId,
    "decoder" : others.dc, "dc" : others.dc,
    "get_log" : others.get_log, "glog" : others.get_log,
    "cleen_log" : others.cleen_log, "clog" : others.cleen_log,

}

list_admin_function= list(dict_admin_function)

list_my_tg_funcs= [_info.info, _photo.photo, form_controller.form]
