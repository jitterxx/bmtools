# -*- coding: utf-8 -*-


"""

"""

import sys

reload(sys)
sys.setdefaultencoding("utf-8")

import modules.bmtools_objects as BMTObjects
import cherrypy
import datetime
import json
import re
import py_expression_eval
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


class DepartmentWizard(object):
    """
    Мастер для заполнения карты подразделения.
    Какую карту заполнять, определяется по коду в переменной current_strategic_map.
    Значение переменной может быть изменено на первой странице Мастера, исходя из прав доступа.
    Если прав достаточно (т.е. можете редактировать любую карту), то меняется значение.
    Если прав недостаточн, т.е. текущий пользователь ответственный за конкретную карту, то изменить нельзя.
    Остальные шаги идут согласно основному мастеру.

    """

    @cherrypy.expose
    @require(member_of("users"))
    def index(self):
        # Проверка прав и выбор текущей карты, если это возможно
        tmpl = lookup.get_template("wizardfordepartment_main_page.html")
        step_desc = dict()
        step_desc['full_description'] = BMTObjects.get_desc("depwiz_start_full_description")
        step_desc['name'] = BMTObjects.get_desc("depwiz_start_name")
        step_desc['next_step'] = "1"

        maps = dict()
        try:
            for one in BMTObjects.get_all_maps():
                if BMTObjects.check_access(one.code, cherrypy.request.login)[0] and one.code != BMTObjects.enterprise_strategic_map:
                    maps[one.code] = one
        except Exception as e:
            return ShowError(e)

        return tmpl.render(step_desc=step_desc, maps=maps)

    @cherrypy.expose
    @require(member_of("users"))
    def start(self, code=None):
        # Запускаем Мастер для заполнения карты указанной в code.
        #  Меняем значения переменных, создаем настройки Мастера и переадресуем на первую или текущую страницу Мастера

        if code:
            # Если указана карта, то меняем карту после проверки прав
            try:
                if BMTObjects.check_access(code, cherrypy.request.login)[1]:
                    BMTObjects.current_strategic_map = code
            except Exception as e:
                return ShowError(e)
            # Проверяем наличие настроек для Мастера
            try:
                master = BMTObjects.wizard_conf_read(code)
            except Exception as e:
                return ShowError(e)

            # Переадресуем на нужную страницу
            if master:
                raise cherrypy.HTTPRedirect("/wizardfordepartment/" + str(master.cur_step))
            else:
                raise cherrypy.HTTPRedirect("/wizardfordepartment/step1")

        else:
            raise cherrypy.HTTPRedirect("/wizardfordepartment")

    @cherrypy.expose
    @require(member_of("users"))
    def step1(self):
        tmpl = lookup.get_template("wizardfordepartment_step1_page.html")
        step_desc = dict()
        step_desc['full_description'] = BMTObjects.get_desc("depwiz_step1_full_description")
        step_desc['name'] = "Шаг 1. Мастер по настройке карты департамента"
        step_desc['next_step'] = "2"

        print "Current MAP : %s" % BMTObjects.current_strategic_map

        try:
            cur_map_goals, cur_map_kpi, cur_map_events, cur_map_metrics = BMTObjects.load_cur_map_objects()
            link_goal_kpi = BMTObjects.load_custom_links()[1]
        except Exception as e:
            print "Ошибка %s " % str(e)
            return ShowError(e)

        print "Current MAP : %s" % BMTObjects.current_strategic_map
        print "Current MAP goals: %s" % cur_map_goals
        print "Current MAP KPI: %s" % cur_map_kpi
        print "Current MAP Events: %s" % cur_map_events
        print "Current MAP Metrics: %s" % cur_map_metrics

        # Создаем список показателей и связанных с ними целей
        kpi_linked_goals = dict()
        for goal in link_goal_kpi.keys():
            pass

        return tmpl.render(step_desc=step_desc,
                           current_map=BMTObjects.get_strategic_map_object(BMTObjects.current_strategic_map),
                           custom_goals=cur_map_goals, custom_kpi=cur_map_kpi, events=cur_map_events,
                           metrics=cur_map_metrics, kpi_linked_goals=kpi_linked_goals)


    @cherrypy.expose
    @require(member_of("users"))
    def step1remove(self, code=None):
        if not code:
            print "Step1remove code empty. Redirect to step1."
            raise cherrypy.HTTPRedirect("/wizardfordepartment/step1")

        try:
            BMTObjects.remove_goal_from_map(code, BMTObjects.current_strategic_map)
        except Exception as e:
            print "Ошибка %s " % str(e)
            return ShowError(e)
        else:
            raise cherrypy.HTTPRedirect("/wizardfordepartment/step1")



    @cherrypy.expose
    @require(member_of("users"))
    def step2(self):
        # Выбрать цели из стратегической карты компании и добавить их в текущую карту
        tmpl = lookup.get_template("wizardfordepartment_step2_page.html")
        step_desc = dict()
        step_desc['full_description'] = BMTObjects.get_desc("depwiz_step2_full_description")
        step_desc['name'] = BMTObjects.get_desc("depwiz_step2_name")
        step_desc['next_step'] = "3"

        print "Current MAP : %s" % BMTObjects.current_strategic_map

        try:
            cur_map_goals = BMTObjects.load_cur_map_objects(BMTObjects.current_strategic_map)[0]
            ent_goals = BMTObjects.load_cur_map_objects(BMTObjects.enterprise_strategic_map)[0]
        except Exception as e:
            print "Ошибка %s " % str(e)
            return ShowError(e)

        print "Current MAP goals: %s" % cur_map_goals
        print "Current ENT goals: %s" % ent_goals

        return tmpl.render(step_desc=step_desc,
                           current_map=BMTObjects.get_strategic_map_object(BMTObjects.current_strategic_map),
                           cur_map_goals=cur_map_goals, ent_goals=ent_goals)

    @cherrypy.expose
    @require(member_of("users"))
    def step2add(self, ent_goals=None):
        """
            Сохраняем выбранные цели в карту подразделения
        """

        if ent_goals is None:
            print "Step2save ent_goals empty. Redirect to step2."
            raise cherrypy.HTTPRedirect("step2")
        else:
            if not isinstance(ent_goals, list):
                ent_goals = [ent_goals]
            print "Step2save ent_goals not empty: %s \n Save data." % ent_goals

        try:
            # Сохраняем цели
            BMTObjects.save_goals_to_map(ent_goals)
        except Exception as e:
            print "Ошибка %s " % str(e)
            return ShowError(e)

        # Ищем связанные с выбранными целями kpi
        kpis = list()
        custom_linked_kpi = BMTObjects.load_custom_links()[1]
        for g in ent_goals:
            if custom_linked_kpi.get(g):
                kpis += custom_linked_kpi.get(g)

        print "Step2add linked KPI to DEPT MAP: %s " % kpis

        try:
            # Сохраняем показатели связанные с выбранными целями
            BMTObjects.save_kpi_to_map(kpis)
        except Exception as e:
            print "Ошибка %s " % str(e)
            return ShowError(e)

        raise cherrypy.HTTPRedirect("step2")

    @cherrypy.expose
    @require(member_of("users"))
    def step2new(self):
        # Добавить новую цель в карту подразделения. Подцель.
        tmpl = lookup.get_template("wizardfordepartment_step2new_page.html")
        step_desc = dict()
        step_desc['full_description'] = BMTObjects.get_desc("depwiz_step2new_full_description")
        step_desc['name'] = BMTObjects.get_desc("depwiz_step2new_name")
        step_desc['next_step'] = "3"

        try:
            cur_map_goals = BMTObjects.load_cur_map_objects(BMTObjects.current_strategic_map)[0]
        except Exception as e:
            print "Ошибка %s " % str(e)
            return ShowError(e)

        print "Current MAP : %s" % BMTObjects.current_strategic_map
        print "Current MAP goals: %s" % cur_map_goals

        return tmpl.render(step_desc=step_desc,
                           current_map=BMTObjects.get_strategic_map_object(BMTObjects.current_strategic_map),
                           cur_map_goals=cur_map_goals, perspectives=BMTObjects.perspectives)


    @cherrypy.expose
    @require(member_of("users"))
    def step2save(self, name=None, description=None, perspective=None, linked=None):
        """
            Сохраняем новую цель в кастомные цели и добавляем в карту подразделения
        """

        print "Wizard for DEP. Step 2 SAVE : %s " % cherrypy.request.params

        if None in [name, description, perspective]:
            print "Один из параметров не указан. Параметры: %s" % cherrypy.request.params
            raise cherrypy.HTTPRedirect("/wizardfordepartment/step2")

        goal_fields = dict()

        goal_fields['goal_name'] = name
        goal_fields['description'] = description
        goal_fields['perspective'] = perspective

        try:
            status = BMTObjects.create_new_custom_goal(goal_fields)
        except Exception as e:
            print "Ошибка при создании CUSTOM_GOAL. %s" % str(e)
            return ShowError(e)

        if linked:
            print "CREATE LINKS for %s and %s." % (status[1], linked)
            try:
                BMTObjects.create_custom_link_for_goals(status[1], linked)
            except Exception as e:
                print "Ошибка при создании LINK_FOR_CUSTOM_GOAL. %s" % str(e)
                return ShowError(e)

        raise cherrypy.HTTPRedirect("/wizardfordepartment/step2")

    @cherrypy.expose
    @require(member_of("users"))
    def step2delete(self, code=None):
        print "DELETE DEPT GOAL."
        raise cherrypy.HTTPRedirect("/wizardfordepartment/step2")

    @cherrypy.expose
    @require(member_of("users"))
    def step2update(self, code=None, name=None, description=None, perspective=None, linked=None):
        print "UPDATE DEPT GOAL."
        raise cherrypy.HTTPRedirect("/wizardfordepartment/step2")




    @cherrypy.expose
    @require(member_of("users"))
    def step3(self):
        """
            Функция добавления целей в кастомные таблицы компании
        """
        tmpl = lookup.get_template("wizardfordepartment_step3_page.html")
        params = cherrypy.request.headers
        step_desc = dict()
        step_desc['full_description'] = ""
        step_desc['name'] = "Шаг 3. Добавить цели из библиотеки в карту подразделения"
        step_desc['next_step'] = "step3stage1"

        try:
            all_custom_goals, all_custom_kpi = BMTObjects.load_custom_goals_kpi()
            map_custom_goals, map_custom_kpi = BMTObjects.load_cur_map_objects()[0:2]
            custom_linked_goals, custom_linked_kpi = BMTObjects.load_custom_links()
            lib_goals, lib_kpi = BMTObjects.load_lib_goals_kpi()
            lib_linked_goals, lib_linked_kpi = BMTObjects.load_lib_links()
        except Exception as e:
            return ShowError(e)

        return tmpl.render(params=params, step_desc=step_desc,
                           all_custom_goals=all_custom_goals, all_custom_kpi=all_custom_kpi,
                           map_custom_goals=map_custom_goals, map_custom_kpi=map_custom_kpi,
                           custom_linked_goals=custom_linked_goals, custom_linked_kpi=custom_linked_kpi,
                           lib_goals=lib_goals, lib_kpi=lib_kpi,
                           lib_linked_goals=lib_linked_goals, lib_linked_kpi=lib_linked_kpi)

    @cherrypy.expose
    @require(member_of("users"))
    def step3save(self, picked_lib_goals=None, picked_custom_goals=None):
        """
            Сохраняем выбранные цели из библиотеки в кастомные таблицы компании.
            ДОбавлем выбранные цели в карту подразделения.
        """

        if picked_lib_goals is None:
            print "DEPT picked_lib_goals empty. Check the picked_custom_goals."
        else:
            if not isinstance(picked_lib_goals, list):
                picked_lib_goals = [picked_lib_goals]
            print "DEPT picked_lib_goals not empty. Save data."

            try:
                BMTObjects.save_picked_goals_to_custom(picked_lib_goals)
                BMTObjects.save_goals_to_map(picked_lib_goals)
            except Exception as e:
                print "DEPT picked_lib_goals SAVE ERROR. %s" % str(e)
                return ShowError(e)
            else:
                print "DEPT picked_lib_goals SAVED."

        if picked_custom_goals is None:
            print "DEPT picked_custom_goals empty. Redirect to step3."
            raise cherrypy.HTTPRedirect("/wizardfordepartment/step3")
        else:
            if not isinstance(picked_custom_goals, list):
                picked_custom_goals = [picked_custom_goals]
            print "DEPT picked_custom_goals not empty. Save data."

            try:
                BMTObjects.save_goals_to_map(picked_custom_goals)
            except Exception as e:
                print "DEPT picked_custom_goals SAVE ERROR. %s" % str(e)
                return ShowError(e)
            else:
                print "DEPT picked_custom_goals SAVED."

        raise cherrypy.HTTPRedirect("/wizardfordepartment/step3")


    @cherrypy.expose
    @require(member_of("users"))
    def step3stage1(self):
        """
            Функция добавления связанных целей в карту подразделения.
            Ищем для выбранных раннее целей связанные с ними и предлагаем их добавить.
        """
        tmpl = lookup.get_template("wizardfordepartment_step3stage1_page.html")
        params = cherrypy.request.headers
        step_desc = dict()
        step_desc['full_description'] = "<p>Функция добавления связанных целей в карту подразделения.</p>" \
                                        "<p>Ищем для выбранных раннее целей связанные с ними и предлагаем их добавить.</p>"
        step_desc['name'] = "Шаг 3. Связанные цели."
        step_desc['subheader'] = BMTObjects.get_desc("step3_subheader")
        step_desc['next_step'] = "step3stage2"

        try:
            map_custom_goals = BMTObjects.load_cur_map_objects()[0]
            all_custom_goals = BMTObjects.load_custom_goals_kpi()[0]
            custom_linked_goals, custom_linked_kpi = BMTObjects.load_custom_links()
            lib_goals, lib_kpi = BMTObjects.load_lib_goals_kpi()
            lib_linked_goals, lib_linked_kpi = BMTObjects.load_lib_links()
        except Exception as e:
            return ShowError(e)

        # Опеределяем, надо ли выводить предложение о дополнительных связанных целях
        # Если нет, то переходим на выбор показателей. Если да, то показываем связанные невыбранные цели. ДЛя этого
        # формируем список таких целей и с каким из выбранных они связаны.
        lib_missing_goals = dict()
        custom_missing_goals = dict()
        cg = map_custom_goals.keys()

        print "DEPT map goals: %s" % map_custom_goals
        print "ALL CUSTOM goals: %s" % all_custom_goals
        print "LIB goals: %s" % lib_goals

        for custom in cg:
            # Если цель кастомная и ее нет в библиотеке, то пропущенные цели = 0
            # если цель кастомная и ее связи есть в кастомной таблице, то считаем связи из кастомной
            if lib_linked_goals.get(custom):
                missed = list(set(lib_linked_goals[custom]) - set(cg))
                print "Цели связанные с выбранной ** %s **  : %s" % (custom, lib_linked_goals[custom])

                if custom in lib_linked_goals.keys() and missed:
                    print "Цели связанные с выбранной ** %s **, но не выбранные: %s" % (custom, missed)
                    for one in missed:
                        if lib_missing_goals.get(one):
                            lib_missing_goals[one].append(custom)
                        else:
                            lib_missing_goals[one] = list()
                            lib_missing_goals[one].append(custom)

            elif custom_linked_goals.get(custom):
                missed = list(set(custom_linked_goals[custom]) - set(cg))
                print "Цели связанные с выбранной ** %s **  : %s" % (custom, custom_linked_goals[custom])

                if custom in custom_linked_goals.keys() and missed:
                    print "Цели связанные с выбранной ** %s **, но не выбранные: %s" % (custom, missed)
                    for one in missed:
                        if custom_missing_goals.get(one):
                            custom_missing_goals[one].append(custom)
                        else:
                            custom_missing_goals[one] = list()
                            custom_missing_goals[one].append(custom)

        if lib_missing_goals or custom_missing_goals:
            print "Есть пропущенные цели. Выводим список."
            print lib_missing_goals
            print custom_missing_goals
        else:
            print "Нет пропущенных целей. Переходим на следующий шаг."
            #raise cherrypy.HTTPRedirect("step3stage2")

        return tmpl.render(params=params, step_desc=step_desc, all_custom_goals=all_custom_goals, lib_goals=lib_goals,
                           lib_missing_goals=lib_missing_goals, map_custom_goals=map_custom_goals,
                           custom_missing_goals=custom_missing_goals)


    @cherrypy.expose
    @require(member_of("users"))
    def step3stage1save(self, picked_lib_goals=None, picked_custom_goals=None):
        """
            Сохраняем выбранные цели из библиотеки в кастомные таблицы компании.
            ДОбавлем выбранные цели в карту подразделения.
        """

        if picked_lib_goals is None:
            print "DEPT picked_lib_goals empty. Check the picked_custom_goals."
        else:
            if not isinstance(picked_lib_goals, list):
                picked_lib_goals = [picked_lib_goals]
            print "DEPT picked_lib_goals not empty. Save data."

            try:
                BMTObjects.save_picked_goals_to_custom(picked_lib_goals)
                BMTObjects.save_goals_to_map(picked_lib_goals)
            except Exception as e:
                print "DEPT picked_lib_goals SAVE ERROR. %s" % str(e)
                return ShowError(e)
            else:
                print "DEPT picked_lib_goals SAVED."

        if picked_custom_goals is None:
            print "DEPT picked_custom_goals empty. Redirect to step3."
            raise cherrypy.HTTPRedirect("/wizardfordepartment/step3stage1")
        else:
            if not isinstance(picked_custom_goals, list):
                picked_custom_goals = [picked_custom_goals]
            print "DEPT picked_custom_goals not empty. Save data."

            try:
                BMTObjects.save_goals_to_map(picked_custom_goals)
            except Exception as e:
                print "DEPT picked_custom_goals SAVE ERROR. %s" % str(e)
                return ShowError(e)
            else:
                print "DEPT picked_custom_goals SAVED."

        raise cherrypy.HTTPRedirect("/wizardfordepartment/step3stage1")


    @cherrypy.expose
    @require(member_of("users"))
    def step3stage2(self):
        """
            Функция добавления связанных целей в кастомные таблицы компании
        """
        tmpl = lookup.get_template("wizardfordepartment_step3stage2_page.html")
        params = cherrypy.request.headers
        step_desc = dict()
        step_desc['stage3_description'] = BMTObjects.get_desc("step3_stage3_description")
        step_desc['name'] = "Шаг 3." + BMTObjects.get_desc("step3_name")
        step_desc['subheader'] = BMTObjects.get_desc("step3_stage3_subheader")
        step_desc['next_step'] = "step4"

        try:
            map_custom_goals, map_custom_kpi = BMTObjects.load_cur_map_objects()[0:2]
            all_custom_goals, all_custom_kpi = BMTObjects.load_custom_goals_kpi()
            lib_kpi = BMTObjects.load_lib_goals_kpi()[1]
            lib_linked_kpi = BMTObjects.load_lib_links()[1]
            custom_linked_kpi = BMTObjects.load_custom_links()[1]
        except Exception as e:
            ShowError(e)

        print "Custom MAP goals: %s" % map_custom_goals
        print "Custom MAP KPI: %s" % map_custom_kpi
        print "Custom linked KPI: %s" % custom_linked_kpi
        print "LIB KPI: %s" % lib_kpi
        print "LIB linked KPI: %s" % lib_linked_kpi

        return tmpl.render(params=params, step_desc=step_desc, map_custom_goals=map_custom_goals, lib_kpi=lib_kpi,
                           lib_linked_kpi=lib_linked_kpi, map_custom_kpi=map_custom_kpi,
                           custom_linked_kpi=custom_linked_kpi,
                           all_custom_goals=all_custom_goals, all_custom_kpi=all_custom_kpi)


    @cherrypy.expose
    @require(member_of("users"))
    def step3stage2save(self, picked_lib_kpi=None, picked_custom_kpi=None):
        """
            Сохраняем выбранные показатели в кастомные таблицы компании
        """

        if picked_lib_kpi is None:
            print "picked_lib_kpi empty. Check picked_custom_kpi."
        else:
            if not isinstance(picked_lib_kpi, list):
                picked_lib_kpi = [picked_lib_kpi]
            print "picked_lib_kpi not empty. Save data."

            try:
                BMTObjects.save_picked_kpi_to_custom(picked_lib_kpi)
                BMTObjects.save_kpi_to_map(picked_lib_kpi)
            except Exception as e:
                return ShowError(e)

        if picked_custom_kpi is None:
            print "picked_custom_kpi empty. Redirect to step3stage3."
            raise cherrypy.HTTPRedirect("/wizardfordepartment/step3stage2")
        else:
            if not isinstance(picked_custom_kpi, list):
                picked_custom_kpi = [picked_custom_kpi]
            print "picked_custom_kpi not empty. Save data."

            try:
                BMTObjects.save_kpi_to_map(picked_custom_kpi)
            except Exception as e:
                return ShowError(e)
            else:
                raise cherrypy.HTTPRedirect("/wizardfordepartment/step3stage2")

        raise cherrypy.HTTPRedirect("/wizardfordepartment/step3stage2")

    @cherrypy.expose
    @require(member_of("users"))
    def step4(self):
        # добавление мероприятий
        tmpl = lookup.get_template("wizardfordepartment_step4_page.html")

        step_desc = dict()
        step_desc['full_description'] = BMTObjects.get_desc("depwiz_step4_full_description")
        step_desc['name'] = BMTObjects.get_desc("depwiz_step4_name")
        step_desc['subheader'] = BMTObjects.get_desc("depwiz_step4_subheader")
        step_desc['next_step'] = "step5"

        try:
            events = BMTObjects.get_events()
            map_custom_goals, a, map_custom_events = BMTObjects.load_cur_map_objects()[0:3]
        except Exception as e:
            return ShowError(e)

        print events

        return tmpl.render(current_map=BMTObjects.get_strategic_map_object(BMTObjects.current_strategic_map),
                           step_desc=step_desc, events=events, map_custom_goals=map_custom_goals,
                           map_custom_events=map_custom_events)

    @cherrypy.expose
    @require(member_of("users"))
    def step4new(self):
        tmpl = lookup.get_template("wizardfordepartment_step4new_page.html")
        step_desc = dict()
        step_desc['full_description'] = BMTObjects.get_desc("depwiz_step4_full_description")
        step_desc['name'] = BMTObjects.get_desc("depwiz_step4_name")
        step_desc['next_step'] = "step5"
        step_desc['subheader'] = BMTObjects.get_desc("depwiz_step4_subheader")

        # Получаем список кастомных целей компании
        try:
            (map_goals,) = BMTObjects.load_cur_map_objects()[0:1]
        except Exception as e:
            return ShowError(e)

        return tmpl.render(current_map=BMTObjects.get_strategic_map_object(BMTObjects.current_strategic_map),
                           step_desc=step_desc, persons=BMTObjects.persons, map_goals=map_goals)

    @cherrypy.expose
    @require(member_of("users"))
    def step4save(self, goal=None, name=None, description=None, planres=None,
                  responsible=None, actors=None, start_date=None, end_date=None):
        """
            Сохраняем выбранные значения
        """
        print "DEPT Step 4 SAVE : %s " % cherrypy.request.params

        if None in cherrypy.request.params.values():
            print "DEPT. Один из параметров не указан. Параметры: %s" % cherrypy.request.params
            raise cherrypy.HTTPRedirect("step4new")
        event_fields = dict()

        event_fields['actors'] = ",".join(actors)
        event_fields['description'] = description
        event_fields['end_date'] = datetime.datetime.strptime(end_date, "%d.%m.%Y").date()
        event_fields['start_date'] = datetime.datetime.strptime(start_date, "%d.%m.%Y").date()
        event_fields['name'] = name
        event_fields['plan_result'] = planres
        event_fields['linked_goal_code'] = goal
        event_fields['responsible'] = responsible

        try:
            BMTObjects.create_new_event(event_fields)
        except Exception as e:
            return ShowError(e)
        else:
            raise cherrypy.HTTPRedirect("/wizardfordepartment/step4")

    @cherrypy.expose
    @require(member_of("users"))
    def step4edit(self, event_code=None):
        """
            Сохраняем выбранные значения
        """
        print "DEPT Step 4 EDIT : %s " % cherrypy.request.params

        if None in cherrypy.request.params.values():
            print "Один из параметров не указан. Параметры: %s" % cherrypy.request.params
            raise cherrypy.HTTPRedirect("/wizardfordepartment/step4")

        tmpl = lookup.get_template("wizardfordepartment_step4edit_page.html")
        step_desc = dict()
        step_desc['full_description'] = BMTObjects.get_desc("step4_full_description")
        step_desc['name'] = BMTObjects.get_desc("step4_name")
        step_desc['next_step'] = "step5"
        step_desc['subheader'] = BMTObjects.get_desc("step6_subheader")

        try:
            (goals, a, events) = BMTObjects.load_cur_map_objects()[0:3]
        except Exception as e:
            return ShowError(e)

        event=events[event_code]
        actors = re.split(",", event.actors)
        print "GOALS FOR EVENT: %s" % goals

        return tmpl.render(current_map=BMTObjects.get_strategic_map_object(BMTObjects.current_strategic_map),
                           step_desc=step_desc, persons=BMTObjects.persons,
                           goals=goals, event=event, actors=actors)

    @cherrypy.expose
    @require(member_of("users"))
    def step4update(self, event_code=None, goal=None, name=None, description=None, planres=None,
                  responsible=None, actors=None, start_date=None, end_date=None):
        """
            Сохраняем выбранные значения
        """
        print "DEPT Step 4 UPDATE : %s " % cherrypy.request.params

        if None in cherrypy.request.params.values():
            print "Step4 UPDATE. Один из параметров не указан. Параметры: %s" % cherrypy.request.params
            raise cherrypy.HTTPRedirect("step4")
        event_fields = dict()

        event_fields['actors'] = ",".join(actors)
        event_fields['description'] = description
        event_fields['end_date'] = datetime.datetime.strptime(end_date, "%d.%m.%Y").date()
        event_fields['start_date'] = datetime.datetime.strptime(start_date, "%d.%m.%Y").date()
        event_fields['name'] = name
        event_fields['plan_result'] = planres
        event_fields['linked_goal_code'] = goal
        event_fields['responsible'] = responsible

        try:
            BMTObjects.update_event(event_code, event_fields)
        except Exception as e:
            return ShowError(e)
        else:
            raise cherrypy.HTTPRedirect("/wizardfordepartment/step4")

    @cherrypy.expose
    @require(member_of("users"))
    def step4delete(self, event_code=None):

        print "DEPT Step 4 DELETE : %s " % cherrypy.request.params

        if None in cherrypy.request.params.values():
            print "DEPT Step4 DELETE. Один из параметров не указан. Параметры: %s" % cherrypy.request.params
            raise cherrypy.HTTPRedirect("step6")

        try:
            BMTObjects.delete_event(event_code)
        except Exception as e:
            return ShowError(e)
        else:
            raise cherrypy.HTTPRedirect("/wizardfordepartment/step4")


class Wizard(object):

    @cherrypy.expose
    @require(member_of("users"))
    def index(self):
        tmpl = lookup.get_template("wizard_main_page.html")
        params = cherrypy.request.headers

        # check wizard configuration exist
        session = BMTObjects.Session()
        wiz_conf = BMTObjects.wizard_conf_read_old(session)
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
        wiz_conf = BMTObjects.wizard_conf_read_old(session)

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
            op_status = BMTObjects.wizard_conf_save_old(session)

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
        BMTObjects.change_current_strategic_map(BMTObjects.enterprise_strategic_map)
        params = cherrypy.request.headers
        step_desc = dict()
        step_desc['full_description'] = BMTObjects.get_desc("step3_full_description")
        step_desc['name'] = "Шаг 3." + BMTObjects.get_desc("step3_name")
        step_desc['next_step'] = "4"

        try:
            custom_goals, custom_kpi = BMTObjects.load_cur_map_objects()[0:2]
        except Exception as e:
            return ShowError(e)

        print "Custom goals: %s" % custom_goals.keys()
        print "Custom KPI: %s" % custom_kpi.keys()

        return tmpl.render(params=params, step_desc=step_desc, custom_goals=custom_goals, custom_kpi=custom_kpi,
                           current_map=BMTObjects.get_strategic_map_object(BMTObjects.current_strategic_map))


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
            custom_goals, custom_kpi = BMTObjects.load_cur_map_objects()[0:2]
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
            custom_goals, custom_kpi = BMTObjects.load_cur_map_objects()[0:2]
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
            custom_goals, custom_kpi = BMTObjects.load_cur_map_objects()[0:2]
            lib_kpi = BMTObjects.load_lib_goals_kpi()[1]
            lib_linked_kpi = BMTObjects.load_lib_links()[1]
        except Exception as e:
            ShowError(e)

        print "Custom goals: %s" % custom_goals
        print "Custom KPI: %s" % custom_kpi
        print "LIB KPI: %s" % lib_kpi
        print "LIB linked KPI: %s" % lib_linked_kpi

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
            custom_goals = BMTObjects.load_custom_goals_kpi()[0]
        except Exception as e:
            return ShowError(e)

        print events

        return tmpl.render(params=params, step_desc=step_desc, events=events, custom_goals=custom_goals)

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
            (goals,) = BMTObjects.load_cur_map_objects()[0:1]
        except Exception as e:
            return ShowError(e)

        return tmpl.render(params=params, step_desc=step_desc, persons=BMTObjects.persons, goals=goals)

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
        event_fields['end_date'] = datetime.datetime.strptime(end_date, "%d.%m.%Y").date()
        event_fields['start_date'] = datetime.datetime.strptime(start_date, "%d.%m.%Y").date()
        event_fields['name'] = name
        event_fields['plan_result'] = planres
        event_fields['linked_goal_code'] = goal
        event_fields['responsible'] = responsible

        try:
            BMTObjects.create_new_event(event_fields)
        except Exception as e:
            return ShowError(e)
        else:
            raise cherrypy.HTTPRedirect("/wizard/step6")

    @cherrypy.expose
    @require(member_of("users"))
    def step6edit(self, event_code=None):
        """
            Сохраняем выбранные значения
        """
        print "Step 6 EDIT : %s " % cherrypy.request.params

        if None in cherrypy.request.params.values():
            print "Один из параметров не указан. Параметры: %s" % cherrypy.request.params
            raise cherrypy.HTTPRedirect("step6")

        tmpl = lookup.get_template("wizard_step6edit_page.html")
        params = cherrypy.request.headers
        step_desc = dict()
        step_desc['full_description'] = BMTObjects.get_desc("step6_full_description")
        step_desc['name'] = "Шаг 6. " + BMTObjects.get_desc("step6_name")
        step_desc['next_step'] = "7"
        step_desc['subheader'] = BMTObjects.get_desc("step6_subheader")

        try:
            events = BMTObjects.get_events()
            (goals,) = BMTObjects.load_cur_map_objects()[0:1]
        except Exception as e:
            return ShowError(e)
        event=events[event_code]
        actors = re.split(",", event.actors)
        print "GOALS FOR EVENT: %s" % goals

        return tmpl.render(params=params, step_desc=step_desc, persons=BMTObjects.persons,
                           goals=goals, event=event, actors=actors)

    @cherrypy.expose
    @require(member_of("users"))
    def step6update(self, event_code=None, goal=None, name=None, description=None, planres=None,
                  responsible=None, actors=None, start_date=None, end_date=None):
        """
            Сохраняем выбранные значения
        """
        print "Step 6 UPDATE : %s " % cherrypy.request.params

        if None in cherrypy.request.params.values():
            print "Step6 UPDATE. Один из параметров не указан. Параметры: %s" % cherrypy.request.params
            raise cherrypy.HTTPRedirect("step6")
        event_fields = dict()

        event_fields['actors'] = ",".join(actors)
        event_fields['description'] = description
        event_fields['end_date'] = datetime.datetime.strptime(end_date, "%d.%m.%Y").date()
        event_fields['start_date'] = datetime.datetime.strptime(start_date, "%d.%m.%Y").date()
        event_fields['name'] = name
        event_fields['plan_result'] = planres
        event_fields['linked_goal_code'] = goal
        event_fields['responsible'] = responsible

        try:
            BMTObjects.update_event(event_code, event_fields)
        except Exception as e:
            return ShowError(e)
        else:
            raise cherrypy.HTTPRedirect("/wizard/step6")

    @cherrypy.expose
    @require(member_of("users"))
    def step6delete(self, event_code=None):

        print "Step 6 DELETE : %s " % cherrypy.request.params

        if None in cherrypy.request.params.values():
            print "Step6 DELETE. Один из параметров не указан. Параметры: %s" % cherrypy.request.params
            raise cherrypy.HTTPRedirect("step6")

        try:
            BMTObjects.delete_event(event_code)
        except Exception as e:
            return ShowError(e)
        else:
            raise cherrypy.HTTPRedirect("/wizard/step6")

    @cherrypy.expose
    @require(member_of("users"))
    def step7(self):
        # Выбор подразделений из орг структуры которые будут создавать свои стратегические карты
        # Надо вывести все подразделения с возможностью отметить их. Если у подразделения есть карта,
        # то галка выбора не должна быть доступна.
        # Данные для сохранения передаются по адресу step7save
        tmpl = lookup.get_template("wizard_step7_page.html")
        params = cherrypy.request.headers
        step_desc = dict()
        step_desc['full_description'] = BMTObjects.get_desc("step7_full_description")
        step_desc['name'] = "Шаг 7." + BMTObjects.get_desc("step7_name")
        step_desc['subheader'] = BMTObjects.get_desc("step7_subheader")
        step_desc['next_step'] = "8"

        try:
            org, shift = BMTObjects.get_structure_sorted()
            current_map = BMTObjects.get_strategic_map_object(BMTObjects.current_strategic_map)
        except Exception as e:
            ShowError(e)

        departments = list()
        for one in org:
            answer = BMTObjects.get_map_for_dep(one.id)
            if answer:
                departments.append(answer)
            else:
                departments.append(None)

        return tmpl.render(params=params, step_desc=step_desc, org=org, shift=shift, persons=BMTObjects.persons,
                           departments=departments, current_map=current_map)

    @cherrypy.expose
    @require(member_of("users"))
    def step7save(self, org=None):
        """
            Сохраняем выбранные значения
        """
        print "Step 7 SAVE : %s " % cherrypy.request.params
        if not isinstance(org, list):
            org = [org]

        if None in org:
            print "Step7 SAVE. Один из параметров не указан. Параметры: %s" % cherrypy.request.params
            raise cherrypy.HTTPRedirect("/wizard/step7")

        orgs = dict()
        for one in BMTObjects.get_structure_sorted()[0]:
            orgs[one.id] = one
        try:

            for one in org:
                BMTObjects.create_strategic_map(int(one), name="Стратегическая карта: %s" % orgs[int(one)].org_name,
                                                owner=orgs[int(one)].director)
        except Exception as e:
            print "Step7 SAVE. Ошибка: %s" % str(e)
            ShowError(e)

        raise cherrypy.HTTPRedirect("/wizard/step7")

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


class Library(object):

    @cherrypy.expose
    @require(member_of("users"))
    def index(self):
        # Работа с бибилиотекой данных: просмотр
        # Работа с касмтоными данными: просмотр, добавление, редактирование, удаление, связывание
        tmpl = lookup.get_template("library_main_page.html")
        step_desc = dict()
        step_desc['full_description'] = "Работа с данными: просмотр, добавление, редактирование, удаление, связывание."
        step_desc['name'] = "Библиотека"
        try:
            lib_goals, lib_kpi = BMTObjects.load_lib_goals_kpi()
            custom_goals, custom_kpi = BMTObjects.load_custom_goals_kpi()
            events = BMTObjects.get_events()
        except Exception as e:
            return ShowError(e)

        return tmpl.render(current_map=BMTObjects.get_strategic_map_object(BMTObjects.current_strategic_map),
                           step_desc=step_desc, lib_goals=lib_goals, lib_kpi=lib_kpi, events=events,
                           custom_kpi=custom_kpi, custom_goals=custom_goals, perspectives=BMTObjects.perspectives)


class Goals(object):

    @cherrypy.expose
    @require(member_of("users"))
    def new(self):
        # TODO: Переделать форму выбора связанных целей, из select на галки.
        # Создание новой цели
        tmpl = lookup.get_template("goals_new_page.html")
        step_desc = dict()
        step_desc['full_description'] = "Создание новой цели"
        step_desc['name'] = "Создание новой цели"
        step_desc['next_step'] = "/maps?code=%s" % BMTObjects.current_strategic_map

        try:
            cur_map_goals = BMTObjects.load_cur_map_objects(BMTObjects.current_strategic_map)[0]
        except Exception as e:
            print "Ошибка %s " % str(e)
            return ShowError(e)

        print "Current MAP : %s" % BMTObjects.current_strategic_map
        print "Current MAP goals: %s" % cur_map_goals

        return tmpl.render(step_desc=step_desc,
                           current_map=BMTObjects.get_strategic_map_object(BMTObjects.current_strategic_map),
                           cur_map_goals=cur_map_goals, perspectives=BMTObjects.perspectives)


    @cherrypy.expose
    @require(member_of("users"))
    def save(self, name=None, description=None, perspective=None, linked=None):
        """
            Сохраняем новую цель в кастомные цели и добавляем в текущую карту
        """

        print "New GOAL SAVE : %s " % cherrypy.request.params

        if None in [name, description, perspective]:
            print "Один из параметров не указан. Параметры: %s" % cherrypy.request.params
            raise cherrypy.HTTPRedirect("/maps?code=%s" % BMTObjects.current_strategic_map)

        goal_fields = dict()

        goal_fields['goal_name'] = name
        goal_fields['description'] = description
        goal_fields['perspective'] = perspective

        try:
            # Записываем новую цель и ждем возврата ее кода
            status = BMTObjects.create_new_custom_goal(goal_fields)
        except Exception as e:
            print "Ошибка при создании CUSTOM_GOAL. %s" % str(e)
            return ShowError(e)

        if linked:
            print "CREATE LINKS for %s and %s." % (status[1], linked)
            try:
                BMTObjects.create_custom_link_for_goals(status[1], linked)
            except Exception as e:
                print "Ошибка при создании LINK_FOR_CUSTOM_GOAL. %s" % str(e)
                return ShowError(e)

        raise cherrypy.HTTPRedirect("/maps?code=%s" % BMTObjects.current_strategic_map)

    @cherrypy.expose
    @require(member_of("users"))
    def edit(self, code=None):
        # TODO: Переделать форму выбора связанных целей, из select на галки.
        # выводим страницу редактирования цели
        print "EDIT GOAL."
        tmpl = lookup.get_template("goals_edit_page.html")
        step_desc = dict()
        step_desc['full_description'] = "Редактирование цели"
        step_desc['name'] = "Редактирование цели"
        step_desc['next_step'] = "/maps?code=%s" % BMTObjects.current_strategic_map

        if not code:
            print "Параметр code указан. Параметры: %s" % cherrypy.request.params
            raise cherrypy.HTTPRedirect("/maps?code=%s" % BMTObjects.current_strategic_map)

        try:
            cur_map_goals = BMTObjects.load_cur_map_objects(BMTObjects.current_strategic_map)[0]
            linked_goals = BMTObjects.load_custom_links()[0]
        except Exception as e:
            print "Ошибка %s " % str(e)
            return ShowError(e)
        else:
            if code in linked_goals.keys():
                linked_goals = linked_goals[code]
            else:
                linked_goals = []

        # Удалем выбранную цель из списка целей
        goal = cur_map_goals[code]
        del cur_map_goals[code]

        print "Current MAP : %s" % BMTObjects.current_strategic_map
        print "Current MAP goals: %s" % cur_map_goals
        print "Linked goals: %s" % linked_goals

        return tmpl.render(step_desc=step_desc,
                           current_map=BMTObjects.get_strategic_map_object(BMTObjects.current_strategic_map),
                           cur_map_goals=cur_map_goals, perspectives=BMTObjects.perspectives,
                           goal=goal, linked_goals=linked_goals, escapef=BMTObjects.escape)


    @cherrypy.expose
    @require(member_of("users"))
    def delete(self, code=None):
        # Удаляем цель из текущей карты. Цель не удаляется из базы, остается в кастомных и видна в библиотеке.
        print "DELETE GOAL."
        if not code:
            print "GOAL code empty. Redirect to /maps?code=%s" % BMTObjects.current_strategic_map
            raise cherrypy.HTTPRedirect("/maps?code=%s" % BMTObjects.current_strategic_map)

        try:
            BMTObjects.remove_goal_from_map(code, BMTObjects.current_strategic_map)
        except Exception as e:
            print "Ошибка %s " % str(e)
            return ShowError(e)
        else:
            raise cherrypy.HTTPRedirect("/maps?code=%s" % BMTObjects.current_strategic_map)

    @cherrypy.expose
    @require(member_of("users"))
    def update(self, code=None, name=None, description=None, perspective=None, linked=None):
        # Сохраняем данные после редактирования цели
        print "UPDATE GOAL."

        if None in [code, name, description, perspective]:
            print "Один из параметров не указан. Параметры: %s" % cherrypy.request.params
            raise cherrypy.HTTPRedirect("/maps?code=%s" % BMTObjects.current_strategic_map)

        goal_fields = dict()

        goal_fields['goal_name'] = name
        goal_fields['description'] = description
        goal_fields['perspective'] = perspective

        print "UPDATE FIELDS: %s" % goal_fields
        print "UPDATE linked: %s" % linked

        try:
            # Обновляем цель
            BMTObjects.update_custom_goal(code, goal_fields)
        except Exception as e:
            print "Ошибка при обновлении CUSTOM GOAL %s. Ошибка: %s" % (code, str(e))
            return ShowError(e)

        if linked:
            print "CREATE LINKS for %s and %s." % (code, linked)
            delete_all = False
        else:
            print "DELETE ALL links for %s." % code
            delete_all = True

        try:
            BMTObjects.update_custom_link_for_goals(code, linked, delete_all=delete_all)
        except Exception as e:
            print "Ошибка при обновлении LINK_FOR_CUSTOM_GOAL. %s" % str(e)
            return ShowError(e)

        raise cherrypy.HTTPRedirect("/maps?code=%s" % BMTObjects.current_strategic_map)


class KPIs(object):

    @cherrypy.expose
    # @require(member_of("users"))
    def new(self):
        # Создание нового показателя
        tmpl = lookup.get_template("kpi_new_page.html")
        step_desc = dict()
        step_desc['full_description'] = ""
        step_desc['name'] = "Создание нового показателя"
        step_desc['next_step'] = "/maps?code=%s" % BMTObjects.current_strategic_map

        try:
            cur_map_goals = BMTObjects.load_cur_map_objects(BMTObjects.current_strategic_map)[0]
        except Exception as e:
            print "Ошибка %s " % str(e)
            return ShowError(e)

        print "Current MAP : %s" % BMTObjects.current_strategic_map
        print "Current MAP kpi: %s" % cur_map_goals

        return tmpl.render(step_desc=step_desc,
                           current_map=BMTObjects.get_strategic_map_object(BMTObjects.current_strategic_map),
                           cur_map_goals=cur_map_goals, perspectives=BMTObjects.perspectives,
                           persons=BMTObjects.persons, kpi_scale_type=BMTObjects.KPI_SCALE_TYPE,
                           measures=BMTObjects.MEASURES, cycles=BMTObjects.CYCLES)

    @cherrypy.expose
    # @require(member_of("users"))
    def save(self, name=None, description=None, kpi_linked_goal=None, data_source=None,
             target_responsible=None, fact_responsible=None, formula=None, link_to_desc=None,
             measures=None, cycles=None, kpi_scale_type=None, plan_period=None, start_date=None):
        """
        Сохраняем новый показатель,добавляем в текущую карту,
        готовим объекты целевых значений для заполнения на втором шаге

        :param name:
        :param description:
        :param kpi_linked_goal:
        :param data_source:
        :param target_responsible:
        :param fact_responsible:
        :param formula:
        :param link_to_desc:
        :param measures:
        :param cycles:
        :param kpi_scale_type:
        :param plan_period:
        :param start_date:
        :return:
        """

        print "New KPI SAVE : %s " % cherrypy.request.params

        # Если не указана цель к которой привязан показатель, тогда это операционный показатель. Для него не нужны:
        #  kpi_linked_goal, target_responsible, plan_period, cycles, start_date.

        if None in [name, kpi_linked_goal, measures, data_source, target_responsible, plan_period, cycles, start_date]:
            print "Один из параметров не указан. Параметры: %s" % cherrypy.request.params
            raise cherrypy.HTTPRedirect("/kpi/new")

        kpi_fields = dict()
        kpi_target = dict()

        try:
            kpi_fields['name'] = str(name)
            kpi_fields['description'] = str(description)
            kpi_fields['formula'] = str(formula)
            kpi_fields['link_to_desc'] = str(link_to_desc)
            kpi_fields['measure'] = int(measures)
            kpi_fields['target_responsible'] = int(target_responsible)
            kpi_fields['fact_responsible'] = int(fact_responsible)
            kpi_fields['cycles'] = int(cycles)
            kpi_fields['data_source'] = str(data_source)
            kpi_fields['kpi_scale_type'] = int(kpi_scale_type)
        except Exception as e:
            print "New KPI SAVE. Ошибка при обработке параметров запроса. %s" % str(e)
            return ShowError(e)

        try:
            # Записываем новый показатель и ждем возврата его кода
            status = BMTObjects.create_new_custom_kpi(kpi_fields)
        except Exception as e:
            print "Ошибка при создании CUSTOM KPI. %s" % str(e)
            return ShowError(e)
        else:
            # привязываем новый показатель к цели
            if kpi_linked_goal == "0":
                print "Операционный показатель. Возвращаемся обратно."
                raise cherrypy.HTTPRedirect("/maps?code=%s" % BMTObjects.current_strategic_map)
            else:
                print "Стратегический показатель. Создаем связь с целью и целевые значения."
                try:
                    BMTObjects.create_custom_link_kpi_to_goal(kpi_linked_goal, status[1])
                except Exception as e:
                    print "Ошибка при создании связи KPI to GOAL. %s" % str(e)
                    return ShowError(e)

                start_date = datetime.datetime.strptime(start_date, "%d.%m.%Y").date()
                print "Количество периодов: %s" % int(plan_period)
                print "Стартовая дата: %s" % start_date
                period_date = dict()
                period_name = dict()

                for one in range(1, int(plan_period) + 1):
                    print "Период: %s" % one
                    period_date[one] = datetime.datetime(start_date.year + (start_date.month / 12),
                                                         ((start_date.month % 12) + one), 1)
                    if (period_date[one].month - 1) == 0:
                        period_name[one] = str(BMTObjects.PERIOD_NAME[period_date[one].month - 1]) + " " + \
                                           str(period_date[one].year - 1)
                    else:
                        period_name[one] = str(BMTObjects.PERIOD_NAME[period_date[one].month - 1]) + " " + \
                                           str(period_date[one].year)

                    print "Отчетная дата периода: %s" % period_date[one]
                    print "Название отчетного периода: %s" % period_name[one]

                print period_date

                # Считаем даты периодов, создаем записи для KPI Target
                # даты отчета по целевым значениям назначаются на следующий день после окончания перида, т.е. 1 число
                # следующего месяца.

                for one in period_date.keys():
                    kpi_target['kpi_code'] = str(status[1])
                    kpi_target['date'] = period_date[one]
                    kpi_target['period_code'] = str(period_date[one].month) + str(period_date[one].year)
                    kpi_target['period_name'] = period_name[one]
                    try:
                        BMTObjects.save_kpi_target_value(kpi_target)
                    except Exception as e:
                        print "Ошибка при создании KPI TARGET. %s" % str(e)
                        return ShowError(e)

                raise cherrypy.HTTPRedirect("/kpi/newstage2?code=%s" % status[1])


    @cherrypy.expose
    # @require(member_of("users"))
    def newstage2(self, code=None):
        # Планирование целевых значений для нового показателя
        tmpl = lookup.get_template("kpi_newstage2_page.html")
        step_desc = dict()
        step_desc['full_description'] = ""
        step_desc['name'] = "Целевые значения"
        step_desc['next_step'] = "/maps?code=%s" % BMTObjects.current_strategic_map

        try:
            goal, kpi = BMTObjects.load_custom_goals_kpi(kpi_code=code,
                                                         goal_code=BMTObjects.load_custom_links(for_kpi=code).goal_code)
            target_values = BMTObjects.get_kpi_target_value(code)
        except Exception as e:
            print "Ошибка %s " % str(e)
            return ShowError(e)

        print "Current KPI: %s" % kpi
        print "Goal for KPI: %s" % goal
        print "Current KPI TARGETS: %s" % target_values

        return tmpl.render(step_desc=step_desc,
                           current_map=BMTObjects.get_strategic_map_object(BMTObjects.current_strategic_map),
                           kpi=kpi, target_values=target_values, goal=goal, perspectives=BMTObjects.perspectives,
                           persons=BMTObjects.persons, kpi_scale_type=BMTObjects.KPI_SCALE_TYPE,
                           measures=BMTObjects.MEASURES, cycles=BMTObjects.CYCLES)

    @cherrypy.expose
    # @require(member_of("users"))
    def savestage2(self, kpi_code=None, period_code=None, target_value=None):
        """
        Сохраняем новый показатель,добавляем в текущую карту,
        готовим объекты целевых значений для заполнения на втором шаге

        :param kpi_code:
        :param period_code:
        :param target_value:
        :return:
        """

        print kpi_code
        print period_code
        print target_value

        kpi_target = dict()
        kpi_target['kpi_code'] = str(kpi_code)
        kpi_target['period_code'] = str(re.split("_",period_code)[1])
        kpi_target['first_value'] = float(target_value)
        try:
            BMTObjects.save_kpi_target_value(kpi_target)
        except Exception as e:
            print "Ошибка при обновлении KPI TARGET. %s" % str(e)
            return ShowError(e)

        return "ok"

    @cherrypy.expose
    #@require(member_of("users"))
    def edit(self, code=None):
        # выводим страницу редактирования показателя, без целевых значений 0 это отдельный этап
        print "EDIT KPI."
        tmpl = lookup.get_template("kpi_edit_page.html")
        step_desc = dict()
        step_desc['full_description'] = ""
        step_desc['name'] = "Редактирование показателя"
        step_desc['next_step'] = "/maps?code=%s" % BMTObjects.current_strategic_map

        if not code:
            print "Параметр code указан. Параметры: %s" % cherrypy.request.params
            raise cherrypy.HTTPRedirect("/maps?code=%s" % BMTObjects.current_strategic_map)

        try:
            cur_map_goals = BMTObjects.load_cur_map_objects(BMTObjects.current_strategic_map)[0]
            (map_kpi, ) = BMTObjects.load_cur_map_objects(BMTObjects.current_strategic_map)[1:2]
            # Возвращает цель или None
            g = BMTObjects.load_custom_links(for_kpi=code)
            if g:
                goal, kpi = BMTObjects.load_custom_goals_kpi(kpi_code=code, goal_code=g.goal_code)
            else:
                goal, kpi = BMTObjects.load_custom_goals_kpi(kpi_code=code, goal_code="0")
            print "kpi", kpi.code
            print "goal", goal
        except Exception as e:
            print "Ошибка при открытии на редактирование показателя %s. Ошибка: %s " % (code, str(e.args))
            return ShowError(e)

        # print "Current MAP : %s" % BMTObjects.current_strategic_map
        # print "Current MAP kpi: %s" % cur_map_goals

        return tmpl.render(step_desc=step_desc,
                           current_map=BMTObjects.get_strategic_map_object(BMTObjects.current_strategic_map),
                           cur_map_goals=cur_map_goals, perspectives=BMTObjects.perspectives,
                           goal=goal, kpi=kpi, persons=BMTObjects.persons, kpi_scale_type=BMTObjects.KPI_SCALE_TYPE,
                           measures=BMTObjects.MEASURES, cycles=BMTObjects.CYCLES, map_kpi=map_kpi)

    @cherrypy.expose
    # @require(member_of("users"))
    def editstage2(self, code=None):
        # Редактирование целевых значений для показателя
        tmpl = lookup.get_template("kpi_editstage2_page.html")
        step_desc = dict()
        step_desc['full_description'] = ""
        step_desc['name'] = "Целевые значения"
        step_desc['next_step'] = "/maps?code=%s" % BMTObjects.current_strategic_map

        try:
            goal, kpi = BMTObjects.load_custom_goals_kpi(kpi_code=code,
                                                         goal_code=BMTObjects.load_custom_links(for_kpi=code).goal_code)
            target_values = BMTObjects.get_kpi_target_value(code)
        except Exception as e:
            print "Ошибка %s " % str(e)
            return ShowError(e)

        print "Current KPI: %s" % kpi
        print "Goal for KPI: %s" % goal
        print "Current KPI TARGETS: %s" % target_values

        return tmpl.render(step_desc=step_desc,
                           current_map=BMTObjects.get_strategic_map_object(BMTObjects.current_strategic_map),
                           kpi=kpi, target_values=target_values, goal=goal, perspectives=BMTObjects.perspectives,
                           persons=BMTObjects.persons, kpi_scale_type=BMTObjects.KPI_SCALE_TYPE,
                           measures=BMTObjects.MEASURES, cycles=BMTObjects.CYCLES)

    @cherrypy.expose
    # @require(member_of("users"))
    def delete(self, code=None):
        # Удаляем показатель из текущей карты. Он не удаляется из базы, остается в кастомных и виден в библиотеке.
        print "DELETE KPI."
        if not code:
            print "KPI code empty. Redirect to /maps?code=%s" % BMTObjects.current_strategic_map
            raise cherrypy.HTTPRedirect("/maps?code=%s" % BMTObjects.current_strategic_map)

        try:
            BMTObjects.remove_kpi_from_map(code, BMTObjects.current_strategic_map)
        except Exception as e:
            print "Ошибка %s " % str(e)
            return ShowError(e)
        else:
            raise cherrypy.HTTPRedirect("/maps?code=%s" % BMTObjects.current_strategic_map)

    @cherrypy.expose
    #@require(member_of("users"))
    def update(self, code=None, name=None, description=None, kpi_linked_goal=None, data_source=None,
               target_responsible=None, fact_responsible=None, formula=None, link_to_desc=None,
               measures=None, cycles=None, kpi_scale_type=None):
        """
        Обновление свойств показателя.
        Сохраняем данные после редактирования показателя.

        :param code:
        :param name:
        :param description:
        :param kpi_linked_goal:
        :param data_source:
        :param target_responsible:
        :param fact_responsible:
        :param formula:
        :param link_to_desc:
        :param measures:
        :param cycles:
        :param kpi_scale_type:
        :return:
        """

        print "UPDATE KPI."

        if None in [code, name, kpi_linked_goal, measures, data_source, target_responsible, cycles]:
            print "Один из параметров не указан. Параметры: %s" % cherrypy.request.params
            raise cherrypy.HTTPRedirect("/kpi/edit?code=%s" % code)

        kpi_fields = dict()

        kpi_fields['code'] = str(code)
        kpi_fields['linked_goal'] = str(kpi_linked_goal)
        kpi_fields['name'] = str(name)
        kpi_fields['description'] = str(description)
        kpi_fields['formula'] = str(formula)
        kpi_fields['link_to_desc'] = str(link_to_desc)
        kpi_fields['measure'] = int(measures)
        kpi_fields['target_responsible'] = int(target_responsible)
        kpi_fields['fact_responsible'] = int(fact_responsible)
        kpi_fields['cycle'] = int(cycles)
        kpi_fields['data_source'] = str(data_source)
        kpi_fields['kpi_scale_type'] = int(kpi_scale_type)

        try:
            # Обновляем показатель
            BMTObjects.update_custom_kpi(kpi_fields)
        except Exception as e:
            print "Ошибка при обновлении CUSTOM KPI. %s" % str(e)
            return ShowError(e)

        raise cherrypy.HTTPRedirect("/maps?code=%s" % BMTObjects.current_strategic_map)

    @cherrypy.expose
    # @require(member_of("users"))
    def updatestage2(self, kpi_code=None, period_code=None, target_value=None, plan_period=None, start_date=None,
                     cycles=None):
        """
        Сохраняем новый показатель,добавляем в текущую карту,
        готовим объекты целевых значений для заполнения на втором шаге

        :param kpi_code:
        :param period_code:
        :param target_value:
        :return:
        """

        print "UPDATE stage2 for KPI"
        print "Параметры запроса: %s" % cherrypy.request.params

        if kpi_code and plan_period and start_date and cycles:
            # Создаем новые таргет

            kpi_target = dict()
            start_date = datetime.datetime.strptime(start_date, "%d.%m.%Y").date()
            print "Количество периодов: %s" % int(plan_period)
            print "Стартовая дата: %s" % start_date
            period_date = dict()
            period_name = dict()

            for one in range(1, int(plan_period) + 1):
                print "Период: %s" % one
                period_date[one] = datetime.datetime(start_date.year + (start_date.month / 12),
                                                     ((start_date.month % 12) + one), 1)
                if (period_date[one].month - 1) == 0:
                    period_name[one] = str(BMTObjects.PERIOD_NAME[period_date[one].month - 1]) + " " + \
                                       str(period_date[one].year - 1)
                else:
                    period_name[one] = str(BMTObjects.PERIOD_NAME[period_date[one].month - 1]) + " " + \
                                       str(period_date[one].year)

                print "Отчетная дата периода: %s" % period_date[one]
                print "Название отчетного периода: %s" % period_name[one]

            # Считаем даты периодов, создаем записи для KPI Target
            # даты отчета по целевым значениям назначаются на следующий день после окончания перида, т.е. 1 число
            # следующего месяца.

            for one in period_date.keys():
                kpi_target['kpi_code'] = str(kpi_code)
                kpi_target['date'] = period_date[one]
                kpi_target['period_code'] = str(period_date[one].month) + str(period_date[one].year)
                kpi_target['period_name'] = period_name[one]
                try:
                    BMTObjects.save_kpi_target_value(kpi_target)
                except Exception as e:
                    print "Ошибка при создании KPI TARGET. %s" % str(e)
                    return ShowError(e)
            raise cherrypy.HTTPRedirect("/kpi/editstage2?code=%s" % kpi_code)

        if kpi_code and period_code and target_value:
            # Обновляем значения
            print kpi_code
            print period_code
            print target_value

            kpi_target = dict()
            kpi_target['kpi_code'] = str(kpi_code)
            kpi_target['period_code'] = str(re.split("_",period_code)[1])
            kpi_target['first_value'] = float(target_value)
            try:
                BMTObjects.save_kpi_target_value(kpi_target)
            except Exception as e:
                print "Ошибка при обновлении KPI TARGET. %s" % str(e)
                return ShowError(e)

            return "ok"


class Root(object):

    auth = AuthController()
    wizard = Wizard()
    wizardfordepartment = DepartmentWizard()
    library = Library()
    goals = Goals()
    kpi = KPIs()

    @cherrypy.expose
    @require(member_of("users"))
    def index(self):
        tmpl = lookup.get_template("main_page.html")
        maps = dict()
        try:
            maps = BMTObjects.get_all_maps()
        except Exception as e:
            return ShowError(e)

        return tmpl.render(current_map=BMTObjects.get_strategic_map_object(BMTObjects.current_strategic_map),
                           maps=maps, ent_map=BMTObjects.enterprise_strategic_map)

    @cherrypy.expose
    @require(member_of("users"))
    def changemap(self, map=None):
        # Проверка прав и выбор текущей карты, если это возможно
        tmpl = lookup.get_template("changemap_page.html")
        step_desc = dict()
        step_desc['full_description'] = ""
        step_desc['name'] = "Выберите стратегическую карту для работы"
        step_desc['next_step'] = ""
        maps = dict()

        if map:
            # Если указана карта, то меняем карту после проверки прав
            try:
                if BMTObjects.check_access(map, cherrypy.request.login)[1]:
                    BMTObjects.current_strategic_map = map
            except Exception as e:
                return ShowError(e)

        try:
            for one in BMTObjects.get_all_maps():
                if BMTObjects.check_access(one.code, cherrypy.request.login)[1]:
                    maps[one.code] = one
        except Exception as e:
            return ShowError(e)

        try:
            current_map = BMTObjects.get_strategic_map_object(BMTObjects.current_strategic_map)
        except Exception as e:
            return ShowError(e)

        return tmpl.render(step_desc=step_desc, maps=maps, cur_map=BMTObjects.current_strategic_map,
                           current_map=current_map)

    @cherrypy.expose
    # @require(member_of("users"))
    def maps(self, code=None):
        step_desc = dict()
        step_desc['full_description'] = ""
        step_desc['name'] = "Просмотр карты"
        step_desc['next_step'] = ""
        print "Show MAP: %s" % code

        if code:
            # TODO: по двойному клику на цель переходить к показу свойств.
            tmpl = lookup.get_template("show_map_page.html")
            try:
                BMTObjects.change_current_strategic_map(code)
                map_goals, map_kpi, map_events, map_opkpi = BMTObjects.load_cur_map_objects(code)
                custom_linked_goals = BMTObjects.load_custom_links()[0]
                draw_data = BMTObjects.load_map_draw_data(code)
            except Exception as e:
                return ShowError(e)

            # print "MAP goals: %s " % map_goals
            # print "MAP kpi: %s " % map_kpi
            # print "MAP linked goals: %s" % custom_linked_goals

            custom_linked_goals_in_json = dict()
            for one in map_goals.values():
                if one.code in custom_linked_goals.keys():
                    custom_linked_goals_in_json[one.code] = custom_linked_goals[one.code]

            custom_linked_goals_in_json = json.dumps(custom_linked_goals_in_json)
            # print "MAP linked goals in JSON: %s" % custom_linked_goals_in_json

            try:
                custom_kpi_links = BMTObjects.load_map_links(for_goals=map_goals.keys(), for_kpi=map_kpi.keys())
            except Exception as e:
                return ShowError(e)

            # print "KPI links: %s" % custom_kpi_links

            kpi_target_values = dict()
            kpi_target_formula_values = dict()
            for one in map_kpi.keys():
                target = BMTObjects.get_kpi_target_value(one)
                if target:
                    kpi_target_values[one] = target

            for one in map_kpi.values():
                # Считаем значения по формуле, если она есть
                if one.formula:
                    print "Есть формула для KPI: %s. Формула: %s" % (one, one.formula)
                    try:
                        formula = py_expression_eval.Parser().parse(one.formula)
                    except Exception as e:
                        print "Формула некорректная. %s" % str(e)
                    else:
                        fsum = dict()
                        var = dict()
                        for e in kpi_target_values[one.code]:
                            fsum[e.period_code] = 0
                            var[e.period_code] = dict()

                        for v in formula.variables():
                            print v
                            for k in kpi_target_values[v]:
                                var[k.period_code][v] = k.first_value
                        print var

                        for e in kpi_target_values[one.code]:
                            fsum[e.period_code] = formula.evaluate(var[e.period_code])

                        kpi_target_formula_values[one.code] = fsum

            print "KPI formula values: %s" % kpi_target_formula_values
            # print "KPI targets: %s" % kpi_target_values

            # Группируем цели по перспективами и порядку расположения
            group_goals = BMTObjects.group_goals(map_goals)
            # print "Grouped goals: %s" % group_goals

            return tmpl.render(step_desc=step_desc, current_map=BMTObjects.get_strategic_map_object(code),
                               map_goals=map_goals, map_kpi=map_kpi, map_events=map_events, map_opkpi=map_opkpi,
                               custom_linked_goals_in_json=custom_linked_goals_in_json,
                               draw_data=draw_data, colors=BMTObjects.PERSPECTIVE_COLORS,
                               persons=BMTObjects.persons, cycles=BMTObjects.CYCLES, measures=BMTObjects.MEASURES,
                               kpi_scale=BMTObjects.KPI_SCALE_TYPE, custom_kpi_links=custom_kpi_links,
                               kpi_target_values=kpi_target_values, group_goals=group_goals,
                               perspectives=BMTObjects.perspectives, fval=kpi_target_formula_values)

        else:
            tmpl = lookup.get_template("maps_page.html")
            maps = dict()
            try:
                maps = BMTObjects.get_all_maps()
            except Exception as e:
                return ShowError(e)

            return tmpl.render(current_map=BMTObjects.get_strategic_map_object(BMTObjects.current_strategic_map),
                               maps=maps, ent_map=BMTObjects.enterprise_strategic_map)

    @cherrypy.expose
    @require(member_of("users"))
    def save_map_draw(self, json_string=None, map_code=None):
        # Сохранение данных для отрисовки карты. Координаты объектов.
        print cherrypy.request.params
        print "Строка для сохранения: %s " % json_string
        print "Код карты: %s " % map_code

        try:
            BMTObjects.save_map_draw_data(map_code, json_string)
        except Exception as e:
            print "Ошибка сохранения данных отрисовки. %s" % str(e)
            return "Ошибка сохранения данных отрисовки. %s" % str(e)

        return "ok"

    @cherrypy.expose
    #@require(member_of("users"))
    def formulaeditor(self):
        tmpl = lookup.get_template("formula_editor_test.html")
        step_desc = dict()
        step_desc['full_description'] = ""
        step_desc['name'] = "Редактор формул"
        step_desc['next_step'] = ""

        print BMTObjects.current_strategic_map

        try:
            current_map = BMTObjects.get_strategic_map_object(BMTObjects.current_strategic_map)
            map_goal, map_kpi = BMTObjects.load_cur_map_objects(BMTObjects.current_strategic_map)[0:2]
        except Exception as e:
            print "Ошибка %s" % str(e)
            return ShowError(e)

        return tmpl.render(step_desc=step_desc, cur_map=BMTObjects.current_strategic_map,
                           current_map=current_map, map_kpi=map_kpi)


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

