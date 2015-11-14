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


def ShowError(e):
    tmpl = lookup.get_template("wizard_error_page.html")
    params = cherrypy.request.headers
    msg = "Ошибка при выполнении. \n" + str(e)

    return tmpl.render(params=params, msg=msg)


class Wizard(object):

    @cherrypy.expose
    @require(member_of("users"))
    def index(self):
        tmpl = lookup.get_template("wizard_main_page.html")
        params = cherrypy.request.headers

        # check wizard configuration exist
        session = BMTObjects.Session()
        wiz_conf = BMTObjects.wizard_conf_read(session)
        if wiz_conf:
            print "Wizard configuration exist"
        else:
            print "Wizard configuration NOT exist"
            wiz_conf = BMTObjects.WizardConfiguration()
            try:
                session.add(wiz_conf)
                session.commit()
            except:
                pass
            else:
                print "Wizard configuration created."
            finally:
                session.close()

        return tmpl.render(params=params, wizard_steps=[x for x in range(1, 15)])

    @cherrypy.expose
    @require(member_of("users"))
    def step1(self, industry=None,action=None):
        tmpl = lookup.get_template("wizard_step1_page.html")
        params = cherrypy.request.headers
        step_desc = dict()
        step_desc['full_description'] = BMTObjects.get_desc("step1_full_description")
        step_desc['name'] = "Шаг 1. " + BMTObjects.get_desc("step1_name")
        step_desc['next_step'] = "2"

        session = BMTObjects.Session()
        wiz_conf = BMTObjects.wizard_conf_read(session)

        if wiz_conf.industry == "":
            status = "new"
        else:
            status = "show"

        op_status = None
        if industry:
            status = "save"
            print "Сохраняем отрасль: %s" % industry
            wiz_conf.industry = industry
            wiz_conf.cur_step = "1"
            wiz_conf.status = "Выполняется шаг 1"
            op_status = BMTObjects.wizard_conf_save(session)

        if action == "edit":
            status = "edit"

        print("status: %s" % status)
        print("op_status: %s" % op_status)
        print("industry: %s" % wiz_conf.industry)

        session.close()
        return tmpl.render(params=params, step_desc=step_desc, industry=BMTObjects.def_industry,
                           status=status, wiz_conf=wiz_conf,op_status=op_status)

    @cherrypy.expose
    @require(member_of("users"))
    def step2(self, action=None, org_id=None, parentid=None, org_name=None, director=None):
        tmpl = lookup.get_template("wizard_step2_page.html")
        params = cherrypy.request.headers
        step_desc = dict()
        step_desc['full_description'] = BMTObjects.get_desc("step2_full_description")
        step_desc['name'] = "Шаг 2. " + BMTObjects.get_desc("step2_name")
        step_desc['next_step'] = "3"
        status = ""
        org_edit = ""

        if action == "new":
            # show current structure
            pass
        elif action == "add":
            # page with form for add new org object to structure
            pass
        elif action == "delete":
            print "org_id: %s" % org_id
            status = BMTObjects.delete_org_structure(org_id)
            action = "show"
        elif action == "edit":
            print "org_id: %s" % org_id
            for one in BMTObjects.get_org_structure():
                if one.id == int(org_id):
                    org_edit = one
            print "Org for edit : %s" % org_edit.id
            pass
        elif action == "save_edit":
            # edit object from structure
            print "Parent ID: %s" % parentid
            print "Director: %s" % director
            print "Org name: %s" % org_name
            print "org_id: %s" % org_id
            if parentid and director and org_name and org_id:
                print "Data for edit org object READY"
                status = BMTObjects.save_edit_org_structure(parentid, director, org_name, org_id)
                action = "show"
            else:
                print "Data for edit Org object NOT READY"
        elif action == "save":
            # save object to structure
            print "Parent ID: %s" % parentid
            print "Director: %s" % director
            print "Org name: %s" % org_name
            if parentid and director and org_name:
                print "Data for new org object READY"
                status = BMTObjects.save_new_org_structure(parentid, director, org_name)
                action = "show"
            else:
                print "Data for new Org object NOT READY"

        else:
            # if action is None: show the org structure
            action = "show"

        org_structure, shift = BMTObjects.get_structure_sorted()

        print org_structure

        return tmpl.render(params=params, step_desc=step_desc, action=action,
                           org_structure=org_structure, persons=BMTObjects.persons,
                           status=status, org_edit=org_edit, shift=shift)

    @cherrypy.expose
    @require(member_of("users"))
    def step3(self):
        tmpl = lookup.get_template("wizard_step3_page.html")
        params = cherrypy.request.headers
        step_desc = dict()
        step_desc['full_description'] = BMTObjects.get_desc("step3_full_description")
        step_desc['name'] = "Шаг 3." + BMTObjects.get_desc("step3_name")
        step_desc['next_step'] = "4"

        try:
            custom_goals, custom_kpi = BMTObjects.load_custom_goals_kpi()
        except Exception as e:
            return ShowError(e)

        print "Custom goals: %s" % custom_goals.keys()
        print "Custom KPI: %s" % custom_kpi.keys()

        return tmpl.render(params=params, step_desc=step_desc, custom_goals=custom_goals, custom_kpi=custom_kpi)


    @cherrypy.expose
    @require(member_of("users"))
    def step3stage1(self):
        """
            Функция добавления целей в кастомные таблицы компании
        """
        tmpl = lookup.get_template("wizard_step3stage1_page.html")
        params = cherrypy.request.headers
        step_desc = dict()
        step_desc['stage1_description'] = BMTObjects.get_desc("step3_stage1_description")
        step_desc['name'] = "Шаг 3." + BMTObjects.get_desc("step3_name")
        step_desc['next_step'] = "4"

        try:
            custom_goals, custom_kpi = BMTObjects.load_custom_goals_kpi()
            custom_linked_goals, custom_linked_kpi = BMTObjects.load_custom_links()
            lib_goals, lib_kpi = BMTObjects.load_lib_goals_kpi()
            lib_linked_goals, lib_linked_kpi = BMTObjects.load_lib_links()
        except Exception as e:
            return ShowError(e)

        return tmpl.render(params=params, step_desc=step_desc, custom_goals=custom_goals, custom_kpi=custom_kpi,
                           custom_linked_goals=custom_linked_goals, custom_linked_kpi=custom_linked_kpi,
                           lib_goals=lib_goals, lib_kpi=lib_kpi,
                           lib_linked_goals=lib_linked_goals, lib_linked_kpi=lib_linked_kpi)

    @cherrypy.expose
    @require(member_of("users"))
    def step3stage1save(self, picked_goals=None):
        """
            Сохраняем выбранные цели в кастомные таблицы компании
        """

        if picked_goals is None:
            print "picked_goals empty. Redirect to step3stage1."
            raise cherrypy.HTTPRedirect("step3stage1")
        else:
            if not isinstance(picked_goals, list):
                picked_goals = [picked_goals]
            print "picked_goals not empty. Save data."

        params = cherrypy.request.headers

        # Проверяем, есть ли уже в кастомных целях выбранные

        try:
            BMTObjects.save_picked_goals_to_custom(picked_goals)
        except Exception as e:
            return ShowError(e)
        else:
            raise cherrypy.HTTPRedirect("step3stage1")


    @cherrypy.expose
    @require(member_of("users"))
    def step3stage2(self):
        """
            Функция добавления связанных целей в кастомные таблицы компании
        """
        tmpl = lookup.get_template("wizard_step3stage2_page.html")
        params = cherrypy.request.headers
        step_desc = dict()
        step_desc['stage2_description'] = BMTObjects.get_desc("step3_stage2_description")
        step_desc['name'] = "Шаг 3." + BMTObjects.get_desc("step3_name")
        step_desc['subheader'] = BMTObjects.get_desc("step3_subheader")
        step_desc['next_step'] = "4"

        try:
            custom_goals, custom_kpi = BMTObjects.load_custom_goals_kpi()
            custom_linked_goals, custom_linked_kpi = BMTObjects.load_custom_links()
            lib_goals, lib_kpi = BMTObjects.load_lib_goals_kpi()
            lib_linked_goals, lib_linked_kpi = BMTObjects.load_lib_links()
        except Exception as e:
            return ShowError(e)

        # Опеределяем, надо ли выводить предложение о дополнительных связанных целях
        # Если нет, то переходим на выбор показателей. Если да, то показываем связанные невыбранные цели. ДЛя этого
        # формируем список таких целей и с каким из выбранных они связаны.
        missing_linked = dict()
        cg = custom_goals.keys()
        for custom in cg:
            missed = list(set(lib_linked_goals[custom]) - set(cg))
            print "Цели связанные с выбранной ** %s **  : %s" % (custom, lib_linked_goals[custom])
            if custom in lib_linked_goals.keys() and missed:
                print "Цели связанные с выбранной ** %s **, но не выбранные: %s" % (custom, missed)
                for one in missed:
                    if missing_linked.get(one):
                        missing_linked[one].append(custom)
                    else:
                        missing_linked[one] = list()
                        missing_linked[one].append(custom)

        if missing_linked:
            print "Есть пропущенные цели. Выводим список."
            print missing_linked
        else:
            print "Нет пропущенных целей. Переходим на следующий шаг."
            raise cherrypy.HTTPRedirect("step3stage3")

        return tmpl.render(params=params, step_desc=step_desc, custom_goals=custom_goals, lib_goals=lib_goals,
                           missing_linked=missing_linked)


    @cherrypy.expose
    @require(member_of("users"))
    def step3stage2save(self, picked_goals=None):
        """
            Сохраняем добполнительно выбранные цели в кастомные таблицы компании
        """

        if picked_goals is None:
            print "picked_goals empty. Redirect to step3stage2."
            raise cherrypy.HTTPRedirect("step3stage2")
        else:
            if not isinstance(picked_goals, list):
                picked_goals = [picked_goals]
            print "Picked goals: %s" % picked_goals
            print "picked_goals not empty. Save data."

        # Проверяем, есть ли уже в кастомных целях выбранные
        try:
            BMTObjects.save_picked_goals_to_custom(picked_goals)
        except Exception as e:
            return ShowError(e)
        else:
            raise cherrypy.HTTPRedirect("step3stage2")


    @cherrypy.expose
    @require(member_of("users"))
    def step3stage3(self):
        """
            Функция добавления связанных целей в кастомные таблицы компании
        """
        tmpl = lookup.get_template("wizard_step3stage3_page.html")
        params = cherrypy.request.headers
        step_desc = dict()
        step_desc['stage3_description'] = BMTObjects.get_desc("step3_stage3_description")
        step_desc['name'] = "Шаг 3." + BMTObjects.get_desc("step3_name")
        step_desc['subheader'] = BMTObjects.get_desc("step3_stage3_subheader")
        step_desc['next_step'] = "4"

        try:
            custom_goals, custom_kpi = BMTObjects.load_custom_goals_kpi()
            lib_kpi = BMTObjects.load_lib_goals_kpi()[1]
            lib_linked_kpi = BMTObjects.load_lib_links()[1]
        except Exception as e:
            ShowError(e)

        return tmpl.render(params=params, step_desc=step_desc, custom_goals=custom_goals, lib_kpi=lib_kpi,
                           lib_linked_kpi=lib_linked_kpi, custom_kpi=custom_kpi)


    @cherrypy.expose
    @require(member_of("users"))
    def step3stage3save(self, picked_kpi=None):
        """
            Сохраняем выбранные показатели в кастомные таблицы компании
        """

        if picked_kpi is None:
            print "picked_kpi empty. Redirect to step3stage3."
            raise cherrypy.HTTPRedirect("step3stage3")
        else:
            if not isinstance(picked_kpi, list):
                picked_kpi = [picked_kpi]
            print "picked_kpi not empty. Save data."

        # Проверяем, есть ли уже в кастомных показателях выбранные

        try:
            BMTObjects.save_picked_kpi_to_custom(picked_kpi)
        except Exception as e:
            return ShowError(e)
        else:
            raise cherrypy.HTTPRedirect("step3stage3")



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
        tmpl = lookup.get_template("wizard_step5_page.html")
        params = cherrypy.request.headers
        step_desc = dict()
        step_desc['full_description'] = BMTObjects.get_desc("step5_full_description")
        step_desc['name'] = "Шаг 5. " + BMTObjects.get_desc("step5_name")
        step_desc['subheader'] = BMTObjects.get_desc("step5_subheader")
        step_desc['next_step'] = "6"

        try:
            custom_goals, custom_kpi = BMTObjects.load_custom_goals_kpi()
            custom_kpi_links = BMTObjects.load_custom_links()[1]
        except Exception as e:
            return ShowError(e)

        kpi_target_values = dict()
        for one in custom_kpi.keys():
            target = BMTObjects.get_kpi_target_value(one)
            if target:
                kpi_target_values[one] = target

        return tmpl.render(params=params, step_desc=step_desc, custom_goals=custom_goals, custom_kpi=custom_kpi,
                           persons=BMTObjects.persons, cycles=BMTObjects.CYCLES, measures=BMTObjects.MEASURES,
                           kpi_scale=BMTObjects.KPI_SCALE_TYPE, custom_kpi_links=custom_kpi_links,
                           kpi_target_values=kpi_target_values)



    @cherrypy.expose
    @require(member_of("users"))
    def step5edit(self, picked_kpi=None):
        tmpl = lookup.get_template("wizard_step5edit_page.html")
        params = cherrypy.request.headers
        step_desc = dict()
        step_desc['full_description'] = BMTObjects.get_desc("step5_full_description")
        step_desc['name'] = "Шаг 5. " + BMTObjects.get_desc("step5_name")
        step_desc['subheader'] = "Шаг 5. " + BMTObjects.get_desc("step5_subheader")
        step_desc['next_step'] = "6"

        if picked_kpi is None:
            print "kpi empty. Redirect to step5."
            raise cherrypy.HTTPRedirect("step5")

        try:
            custom_goals, custom_kpi = BMTObjects.load_custom_goals_kpi()
            custom_kpi_links = BMTObjects.load_custom_links()[1]
        except Exception as e:
            return ShowError(e)

        kpi_target_values = dict()
        for one in custom_kpi.keys():
            target = BMTObjects.get_kpi_target_value(one)
            if target:
                kpi_target_values[one] = target

        return tmpl.render(params=params, step_desc=step_desc, custom_goals=custom_goals, custom_kpi=custom_kpi,
                           persons=BMTObjects.persons, cycles=BMTObjects.CYCLES, measures=BMTObjects.MEASURES,
                           kpi_scale=BMTObjects.KPI_SCALE_TYPE, custom_kpi_links=custom_kpi_links,
                           kpi_target_values=kpi_target_values, picked_kpi=picked_kpi)


    @cherrypy.expose
    @require(member_of("users"))
    def step5save(self, picked_kpi=None, target_responsible=None, measure=None, cycle=None, kpi_scale_type=None,
                  first_value=None, second_value=None, fact_responsible=None, data_source=None):
        """
            Сохраняем выбранные значения
        """
        print "Step 5 SAVE : %s " % cherrypy.request.params

        if None in cherrypy.request.params.values():
            print "Один из параметров не указан. Параметры: %s" % cherrypy.request.params
            raise cherrypy.HTTPRedirect("step5edit?picked_kpi=%s" % picked_kpi)

        if first_value == "":
            first_value = 0

        if second_value == "":
            second_value     = 0


        kpi_target_values = dict()
        custom_kpi_update = dict()

        kpi_target_values["kpi_code"] = picked_kpi
        kpi_target_values["first_value"] = float(first_value)
        kpi_target_values["second_value"] = float(second_value)
        kpi_target_values["kpi_scale_type"] = int(kpi_scale_type)
        kpi_target_values["version"] = BMTObjects.VERSION
        kpi_target_values["data_source"] = data_source

        custom_kpi_update["code"] = picked_kpi
        custom_kpi_update["target_responsible"] = int(target_responsible)
        custom_kpi_update["fact_responsible"] = int(fact_responsible)
        custom_kpi_update["measure"] = int(measure)
        custom_kpi_update["cycle"] = int(cycle)

        try:
            BMTObjects.save_kpi_target_value(kpi_target_values)
            BMTObjects.update_custom_kpi(custom_kpi_update)
        except Exception as e:
            return ShowError(e)
        else:
            raise cherrypy.HTTPRedirect("step5")


    @cherrypy.expose
    @require(member_of("users"))
    def step6(self):
        tmpl = lookup.get_template("wizard_step6_page.html")
        params = cherrypy.request.headers
        step_desc = dict()
        step_desc['full_description'] = BMTObjects.get_desc("step6_full_description")
        step_desc['name'] = "Шаг 6. " + BMTObjects.get_desc("step6_name")
        step_desc['next_step'] = "7"
        step_desc['subheader'] = BMTObjects.get_desc("step6_subheader")
        try:
            events = BMTObjects.get_events()
        except Exception as e:
            return ShowError(e)

        print events

        return tmpl.render(params=params, step_desc=step_desc, events=events)

    @cherrypy.expose
    @require(member_of("users"))
    def step6new(self):
        tmpl = lookup.get_template("wizard_step6new_page.html")
        params = cherrypy.request.headers
        step_desc = dict()
        step_desc['full_description'] = BMTObjects.get_desc("step6_full_description")
        step_desc['name'] = "Шаг 6. " + BMTObjects.get_desc("step6_name")
        step_desc['next_step'] = "7"
        step_desc['subheader'] = BMTObjects.get_desc("step6_subheader")

        # Получаем список кастомных целей компании
        try:
            custom_goals = BMTObjects.load_custom_goals_kpi()[0]
        except Exception as e:
            return ShowError(e)

        return tmpl.render(params=params, step_desc=step_desc, persons=BMTObjects.persons, goals=custom_goals)

    @cherrypy.expose
    @require(member_of("users"))
    def step6save(self, goal=None, name=None, description=None, planres=None,
                  responsible=None, actors=None, start_date=None, end_date=None):
        """
            Сохраняем выбранные значения
        """
        print "Step 6 SAVE : %s " % cherrypy.request.params

        if None in cherrypy.request.params.values():
            print "Один из параметров не указан. Параметры: %s" % cherrypy.request.params
            raise cherrypy.HTTPRedirect("step6new")
        event_fields = dict()

        event_fields['actors'] = ",".join(actors)
        event_fields['description'] = description
        event_fields['end_date'] = end_date
        event_fields['start_date'] = start_date
        event_fields['name'] = name
        event_fields['plan_result'] = planres
        event_fields['linked_goal_code'] = goal
        event_fields['responsible'] = responsible

        try:
            BMTObjects.create_new_event(event_fields)
        except Exception as e:
            return ShowError(e)
        else:
            raise cherrypy.HTTPRedirect("step5")


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

