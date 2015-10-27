# -*- coding: utf-8 -*-


"""

"""

import sys

reload(sys)
sys.setdefaultencoding("utf-8")

import modules.bmtools_objects as BMTObjects
import cherrypy
from bs4 import BeautifulSoup
from auth import AuthController, require, member_of, name_is, all_of, any_of
from mako.lookup import TemplateLookup

lookup = TemplateLookup(directories=["./templates"], output_encoding="utf-8",
                        input_encoding="utf-8", encoding_errors="replace")


class Wizard(object):

    @cherrypy.expose
    @require(member_of("users"))
    def index(self):
        tmpl = lookup.get_template("wizard_main_page.html")
        params = cherrypy.request.headers

        return tmpl.render(params=params, wizard_steps=[x for x in range(1, 15)])

    @cherrypy.expose
    @require(member_of("users"))
    def step1(self, industry=None):
        tmpl = lookup.get_template("wizard_step1_page.html")
        params = cherrypy.request.headers
        step_desc = dict()
        step_desc['full_description'] = BMTObjects.get_desc("step1_full_description")
        step_desc['name'] = "Шаг 1. " + BMTObjects.get_desc("step1_name")
        step_desc['next_step'] = "2"
        def_industry = {"1": "Дистрибьюция"}
        status = ""

        if industry:
            print "Сохраняем отрасль: %s" % industry
            status = "ok"

        return tmpl.render(params=params, step_desc=step_desc, industry=def_industry, status=status)

    @cherrypy.expose
    @require(member_of("users"))
    def step2(self):
        tmpl = lookup.get_template("wizard_step_page.html")
        params = cherrypy.request.headers
        step_desc = dict()
        step_desc['full_description'] = """
            <p>Дерево отражающее организационную структуру компании, в которое можно
            добавлять подчиненные единицы.<p>Каждая ветка означает организационную единицу. </p>

            <p>Переход на следующий шаг, после составления структуры.
            Должна быть создана хотя бы одна организационная единица.
            </p>
            """
        step_desc['name'] = "Шаг 2. Оганизационная структура компании"
        step_desc['next_step'] = "3"

        return tmpl.render(params=params, step_desc=step_desc)

    @cherrypy.expose
    @require(member_of("users"))
    def step3(self):
        tmpl = lookup.get_template("wizard_step_page.html")
        params = cherrypy.request.headers
        step_desc = dict()
        step_desc['full_description'] = ""
        step_desc['name'] = "Шаг 3. Формирование стратегической карты компании"
        step_desc['next_step'] = "4"

        return tmpl.render(params=params, step_desc=step_desc)

    @cherrypy.expose
    @require(member_of("users"))
    def step4(self):
        tmpl = lookup.get_template("wizard_step_page.html")
        params = cherrypy.request.headers
        step_desc = dict()
        step_desc['full_description'] = ""
        step_desc['name'] = "Шаг 4. Добавление дополнительных связей"
        step_desc['next_step'] = "5"

        return tmpl.render(params=params, step_desc=step_desc)

    @cherrypy.expose
    @require(member_of("users"))
    def step5(self):
        tmpl = lookup.get_template("wizard_step_page.html")
        params = cherrypy.request.headers
        step_desc = dict()
        step_desc['full_description'] = ""
        step_desc['name'] = "Шаг 5. Выбор показателей и целевых значений"
        step_desc['next_step'] = "6"

        return tmpl.render(params=params, step_desc=step_desc)

    @cherrypy.expose
    @require(member_of("users"))
    def step6(self):
        tmpl = lookup.get_template("wizard_step_page.html")
        params = cherrypy.request.headers
        step_desc = dict()
        step_desc['full_description'] = ""
        step_desc['name'] = "Шаг 6. Выбор мероприятий"
        step_desc['next_step'] = "7"

        return tmpl.render(params=params, step_desc=step_desc)

    @cherrypy.expose
    @require(member_of("users"))
    def step7(self):
        tmpl = lookup.get_template("wizard_step_page.html")
        params = cherrypy.request.headers
        step_desc = dict()
        step_desc['full_description'] = ""
        step_desc['name'] = "Шаг 7. Выбор организационных единиц для составления стратегических карт подразделений"
        step_desc['next_step'] = "8"

        return tmpl.render(params=params, step_desc=step_desc)

    @cherrypy.expose
    @require(member_of("users"))
    def step8(self):
        tmpl = lookup.get_template("wizard_step_page.html")
        params = cherrypy.request.headers
        step_desc = dict()
        step_desc['full_description'] = ""
        step_desc['name'] = "Шаг 8. Выбор целей, которые имеют отношение к подразделению, из карты предприятия"
        step_desc['next_step'] = "9"

        return tmpl.render(params=params, step_desc=step_desc)

    @cherrypy.expose
    @require(member_of("users"))
    def step9(self):
        tmpl = lookup.get_template("wizard_step_page.html")
        params = cherrypy.request.headers
        step_desc = dict()
        step_desc['full_description'] = ""
        step_desc['name'] = "Шаг 9. Добавление подцелей на стратегические карты подразделений"
        step_desc['next_step'] = "10"

        return tmpl.render(params=params, step_desc=step_desc)

    @cherrypy.expose
    @require(member_of("users"))
    def step10(self):
        tmpl = lookup.get_template("wizard_step_page.html")
        params = cherrypy.request.headers
        step_desc = dict()
        step_desc['full_description'] = ""
        step_desc['name'] = "Шаг 10. Выбор показателей и целевых значений для стратегических карт подразделений"
        step_desc['next_step'] = "11"

        return tmpl.render(params=params, step_desc=step_desc)

    @cherrypy.expose
    @require(member_of("users"))
    def step11(self):
        tmpl = lookup.get_template("wizard_step_page.html")
        params = cherrypy.request.headers
        step_desc = dict()
        step_desc['full_description'] = ""
        step_desc['name'] = "Шаг 11. Выбор мероприятий для подразделений"
        step_desc['next_step'] = "12"

        return tmpl.render(params=params, step_desc=step_desc)

    @cherrypy.expose
    @require(member_of("users"))
    def step12(self):
        tmpl = lookup.get_template("wizard_step_page.html")
        params = cherrypy.request.headers
        step_desc = dict()
        step_desc['full_description'] = ""
        step_desc['name'] = "Шаг 12. Согласование счетных карт подразделений"
        step_desc['next_step'] = "13"

        return tmpl.render(params=params, step_desc=step_desc)

    @cherrypy.expose
    @require(member_of("users"))
    def step13(self):
        tmpl = lookup.get_template("wizard_step_page.html")
        params = cherrypy.request.headers
        step_desc = dict()
        step_desc['full_description'] = ""
        step_desc['name'] = "Шаг 13. Создание мониторов"
        step_desc['next_step'] = "14"

        return tmpl.render(params=params, step_desc=step_desc)

    @cherrypy.expose
    @require(member_of("users"))
    def step14(self):
        tmpl = lookup.get_template("wizard_step_page.html")
        params = cherrypy.request.headers
        step_desc = dict()
        step_desc['full_description'] = ""
        step_desc['name'] = "Шаг 14. Создание схемы мотивации"
        step_desc['next_step'] = "1"

        return tmpl.render(params=params, step_desc=step_desc)



class Root(object):

    auth = AuthController()
    wizard = Wizard()
    @cherrypy.expose
    @require(member_of("users"))
    def index(self):
        tmpl = lookup.get_template("main_page.html")
        params = cherrypy.request.headers

        return tmpl.render(params=params)


"""
def get_session_context(login):
    context = cherrypy.session.get('session_context')
    # print "user login : %s" % login
    user = rwObjects.get_employee_by_login(login)
    # print "user attrs: %s" % user.get_attrs()
    for key in user.get_attrs():
        context[key] = user.__dict__[key]

    context['company'] = rwObjects.get_company_by_id(user.comp_id).name
    context['company_uuid'] = rwObjects.get_company_by_id(user.comp_id).uuid
    context['company_prefix'] = rwObjects.get_company_by_id(user.comp_id).prefix
    context['groups'] = list()
    context['back_ref'] = "/"
    context['menu'] = "main"
    context['username'] = context['login'].split("@", 1)[0]
    context['groups'] = user.access_groups
    context['message_to_user'] = ""

    cherrypy.session['session_context'] = context

    return context
"""

cherrypy.config.update("server.config")

if __name__ == '__main__':
    cherrypy.quickstart(Root(), '/', "app.config")

