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

"""
Переменная хранит историю переходов по страницам приложения.

Каждая функция записывает в конец ссылку на саму себя.
"""

history = list()


def add_to_history(href=None):
    """
    Добавление в историю пеерходов новой страницы

    :param href:
    :return:
    """
    global history

    if not history:
        a = ""
    else:
        a = history.pop()

    if href:
        if a != href:
            # если последний элемент не такой же как новый, добавляем его в список, иначе пропускаем.
            # Это сделано, чтобы при обновлении страницы история не дублировалась
            history.append(a)
            history.append(href)
        else:
            history.append(a)

    print history


def history_back():

    global history
    print "Current history list: %s" % history
    back = str()
    try:
        back = history.pop()
    except IndexError:
        back = "/"
    finally:
        return back


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
            # Проверяем права доступа к картам, выводим только те к которым есть доступ у текущего пользователя
            for one in BMTObjects.get_all_maps():
                if BMTObjects.check_access(one.code, cherrypy.request.login)[0] and one.code != BMTObjects.enterprise_strategic_map:
                    maps[one.code] = one
        except Exception as e:
            return ShowError(e)

        try:
            # Получаем орг структуру для вывода подразделений
            org, shift = BMTObjects.get_structure_sorted()
            # Получаем текущую карту
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

        add_to_history("/wizardfordepartment")
        return tmpl.render(step_desc=step_desc, maps=maps, org=org, shift=shift, persons=BMTObjects.persons,
                           departments=departments, current_map=current_map)

    @cherrypy.expose
    #@require(member_of("users"))
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
    #@require(member_of("users"))
    def step1(self):
        tmpl = lookup.get_template("wizardfordepartment_step1_page.html")
        step_desc = dict()
        step_desc['name'] = "Шаг 1. Мастер по настройке карты подразделения"
        step_desc['next_step'] = "2"

        try:
            current_map = BMTObjects.get_strategic_map_object(BMTObjects.current_strategic_map)
            # cur_map_goals, cur_map_kpi, cur_map_events, cur_map_metrics = BMTObjects.load_cur_map_objects(current_map.code)
            # link_goal_kpi = BMTObjects.load_custom_links()[1]
        except Exception as e:
            print "Ошибка %s " % str(e)
            return ShowError(e)

        print "Current MAP : %s" % current_map.code
        if current_map.code == BMTObjects.enterprise_strategic_map:
            raise cherrypy.HTTPRedirect("/wizardfordepartment")

        print "Current MAP : %s" % current_map
        # print "Current MAP goals: %s" % cur_map_goals
        # print "Current MAP KPI: %s" % cur_map_kpi
        # print "Current MAP Events: %s" % cur_map_events
        # print "Current MAP Metrics: %s" % cur_map_metrics

        # Создаем список показателей и связанных с ними целей
        try:
            # BMTObjects.change_current_strategic_map(code)
            map_goals, map_kpi, map_events, map_opkpi = BMTObjects.load_cur_map_objects(current_map.code)
            custom_linked_goals = BMTObjects.load_custom_links()[0]
        except Exception as e:
            return ShowError(e)


        try:
            custom_kpi_links = BMTObjects.load_map_links(for_goals=map_goals.keys(), for_kpi=map_kpi.keys())
        except Exception as e:
            return ShowError(e)

        grouped_goals = BMTObjects.group_goals(map_goals)

        department = BMTObjects.get_org_structure(int(current_map.department))
        step_desc['full_description'] = """
            <p>Вы находитесь в первом шаге мастера по настройке стратегической карты подразделения <b> %s </b>.</p>
            <p>На следующих шагах масте вам будет предложено добавить в карту цели, показатели и мероприятия из
            стратегической карты Компании. </p>
            <p>Так же вы сможете добавить новые цели, показатели и мероприятия относящиеся только к этому подразделению.</p>
            <p>Для перехода на следующий шаг нажмите Дальше.</p>
        """ % department.org_name

        add_to_history("/wizardfordepartment/step1")
        return tmpl.render(step_desc=step_desc, current_map=current_map, grouped_goals=grouped_goals,
                           custom_goals=map_goals, custom_kpi=map_kpi, events=map_events,
                           metrics=map_opkpi, kpi_linked_goals=custom_kpi_links,
                           perspectives=BMTObjects.perspectives, colors=BMTObjects.PERSPECTIVE_COLORS)


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
    # @require(member_of("users"))
    def step2(self):
        # Выбрать цели из стратегической карты компании и добавить их в текущую карту
        tmpl = lookup.get_template("wizardfordepartment_step2_page.html")
        step_desc = dict()
        step_desc['full_description'] = """
                <p>На этом шаге вам необходимо сформировать цели для подразделения.</p>
                </p>Вы можете добавить некоторые цели из карты компании. Для этого выберите их из списка слева и нажмите кнопку
                <a href="#add_dep">Добавить выделенные в карту подразделения</a>,
                выбранные цели появятся в списке справа.</p>
                <p>Если добавлять ничего не надо, создайте новые цели. Для этого нажмите в боковом меню
                <a href="#">Добавить новую цель</a></p>
        """
        current_map = BMTObjects.get_strategic_map_object(BMTObjects.current_strategic_map)
        print "Current MAP : %s" % current_map.code
        if current_map.code == BMTObjects.enterprise_strategic_map:
            raise cherrypy.HTTPRedirect("/wizardfordepartment")

        department = BMTObjects.get_org_structure(int(current_map.department))
        step_desc['name'] = "Шаг 2. Добавьте цели в стратегическую карту подразделения \"%s\"" % department.org_name
        step_desc['next_step'] = "3"

        try:
            cur_map_goals = BMTObjects.load_cur_map_objects(BMTObjects.current_strategic_map)[0]
            ent_goals = BMTObjects.load_cur_map_objects(BMTObjects.enterprise_strategic_map)[0]
        except Exception as e:
            print "Ошибка %s " % str(e)
            return ShowError(e)

        # print "Current MAP goals: %s" % cur_map_goals
        # print "Current ENT goals: %s" % ent_goals

        ent_grouped_goals = BMTObjects.group_goals(ent_goals)
        map_grouped_goals = BMTObjects.group_goals(cur_map_goals)

        add_to_history("/wizardfordepartment/step2")
        return tmpl.render(step_desc=step_desc,
                           current_map=current_map,
                           cur_map_goals=cur_map_goals, ent_goals=ent_goals, ent_grouped_goals=ent_grouped_goals,
                           perspectives=BMTObjects.perspectives, colors=BMTObjects.PERSPECTIVE_COLORS,
                           map_grouped_goals=map_grouped_goals)

    @cherrypy.expose
    # @require(member_of("users"))
    def step2add(self, ent_goals=None):
        """
            Сохраняем выбранные цели в карту подразделения
        """

        if ent_goals is None:
            print "Step2save ent_goals empty. Redirect to step2."
            raise cherrypy.HTTPRedirect("/wizardfordepartment/step2")
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
        """
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
        """

        raise cherrypy.HTTPRedirect("/wizardfordepartment/step2")

    """
    @cherrypy.expose
    # @require(member_of("users"))
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
        ""
            Сохраняем новую цель в кастомные цели и добавляем в карту подразделения
        ""

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

    """

    @cherrypy.expose
    # @require(member_of("users"))
    def step3(self):
        """
            Функция добавления целей в кастомные таблицы компании
        """
        tmpl = lookup.get_template("wizardfordepartment_step3_page.html")
        params = cherrypy.request.headers
        step_desc = dict()
        step_desc['full_description'] = ""
        step_desc['name'] = "Шаг 3. Добавить цели из библиотеки в карту подразделения"
        step_desc['next_step'] = "4"

        current_map = BMTObjects.get_strategic_map_object(BMTObjects.current_strategic_map)
        print "STEP3. Current MAP: %s" % current_map.name
        if BMTObjects.current_strategic_map == BMTObjects.enterprise_strategic_map:
            # Выбрана карта компании, необходимо выбрать карту подразделения
            raise cherrypy.HTTPRedirect("/wizardfordepartment")

        try:
            all_custom_goals = BMTObjects.load_custom_goals_kpi()[0]
            map_custom_goals = BMTObjects.load_cur_map_objects()[0]
            custom_linked_goals = BMTObjects.load_custom_links()[0]
            lib_goals = BMTObjects.load_lib_goals_kpi()[0]
            lib_linked_goals = BMTObjects.load_lib_links()[0]
            ent_goals = BMTObjects.load_cur_map_objects(BMTObjects.enterprise_strategic_map)[0]
        except Exception as e:
            return ShowError(e)

        map_grouped_goals = BMTObjects.group_goals(map_custom_goals)
        lib_grouped_goals = BMTObjects.group_goals(lib_goals)
        all_grouped_goals = BMTObjects.group_goals(all_custom_goals)
        return tmpl.render(params=params, step_desc=step_desc, current_map=current_map,
                           all_custom_goals=all_custom_goals, map_custom_goals=map_custom_goals,
                           custom_linked_goals=custom_linked_goals, lib_goals=lib_goals,
                           lib_linked_goals=lib_linked_goals, map_grouped_goals=map_grouped_goals,
                           lib_grouped_goals=lib_grouped_goals, all_grouped_goals=all_grouped_goals,
                           ent_goals=ent_goals, perspectives=BMTObjects.perspectives,
                           colors=BMTObjects.PERSPECTIVE_COLORS)

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
    # @require(member_of("users"))
    def step4(self):
        """
            Функция добавления связанных целей в карту подразделения.
            Ищем для выбранных раннее целей связанные с ними и предлагаем их добавить.
        """
        tmpl = lookup.get_template("wizardfordepartment_step4_page.html")
        params = cherrypy.request.headers
        step_desc = dict()
        step_desc['full_description'] = """
            <p>На предыдущих шагах вы выбрали цели из карты компании и дополнительные из библиотеки.
            Эти цели так же связаны с некоторыми целями, которые не были выбраны.</p>
            <p>Мы предлагаем вам посмотреть на связанные цели и выбрать, те из них которые могут быть полезны.</p>
            <p>Предлагаемые цели выведены черным шрифтом, в скобках указана перспектива к которой они относятся.</p>
            """

        step_desc['name'] = "Шаг 4. Связанные цели"
        step_desc['subheader'] = BMTObjects.get_desc("step3_subheader")
        step_desc['next_step'] = "5"

        current_map = BMTObjects.get_strategic_map_object(BMTObjects.current_strategic_map)
        print "STEP4. Current MAP: %s" % current_map.name
        if BMTObjects.current_strategic_map == BMTObjects.enterprise_strategic_map:
            # Выбрана карта компании, необходимо выбрать карту подразделения
            raise cherrypy.HTTPRedirect("/wizardfordepartment")

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
        lib_missing_goals2 = dict()
        custom_missing_goals2 = dict()
        cg = map_custom_goals.keys()

        # print "DEPT map goals: %s" % map_custom_goals
        # print "ALL CUSTOM goals: %s" % all_custom_goals
        # print "LIB goals: %s" % lib_goals

        for custom in cg:
            # набор связанных, но не выбранных целе, для каждой цели в текущей карте. Если таких нет, то пустой []
            lib_missing_goals2[custom] = list()
            custom_missing_goals2[custom] = list()
            # Если цель кастомная и ее нет в библиотеке, то пропущенные цели = 0
            # если цель кастомная и ее связи есть в кастомной таблице, то считаем связи из кастомной
            if lib_linked_goals.get(custom):
                missed = list(set(lib_linked_goals[custom]) - set(cg))
                # print "Цели связанные с выбранной ** %s **  : %s" % (custom, lib_linked_goals[custom])

                lib_missing_goals2[custom] = missed

                if custom in lib_linked_goals.keys() and missed:
                    # print "Цели связанные с выбранной ** %s **, но не выбранные: %s" % (custom, missed)
                    for one in missed:
                        if lib_missing_goals.get(one):
                            lib_missing_goals[one].append(custom)
                        else:
                            lib_missing_goals[one] = list()
                            lib_missing_goals[one].append(custom)

            elif custom_linked_goals.get(custom):
                missed = list(set(custom_linked_goals[custom]) - set(cg))
                # print "Цели связанные с выбранной ** %s **  : %s" % (custom, custom_linked_goals[custom])

                custom_missing_goals2[custom] = missed

                if custom in custom_linked_goals.keys() and missed:
                    # print "Цели связанные с выбранной ** %s **, но не выбранные: %s" % (custom, missed)
                    for one in missed:
                        if custom_missing_goals.get(one):
                            custom_missing_goals[one].append(custom)
                        else:
                            custom_missing_goals[one] = list()
                            custom_missing_goals[one].append(custom)

        if lib_missing_goals or custom_missing_goals:
            print "Есть пропущенные цели. Выводим список."
            # print lib_missing_goals2
            # print custom_missing_goals2
        else:
            print "Нет пропущенных целей. Переходим на следующий шаг."
            # raise cherrypy.HTTPRedirect("step3stage2")

        grouped_goals = BMTObjects.group_goals(map_custom_goals)

        return tmpl.render(params=params, step_desc=step_desc, all_custom_goals=all_custom_goals, lib_goals=lib_goals,
                           map_custom_goals=map_custom_goals, perspectives=BMTObjects.perspectives,
                           colors=BMTObjects.PERSPECTIVE_COLORS, grouped_goals=grouped_goals,
                           lib_missing_goals2=lib_missing_goals2, custom_missing_goals2=custom_missing_goals2,
                           current_map=current_map)


    @cherrypy.expose
    @require(member_of("users"))
    def step4save(self, picked_lib_goals=None, picked_custom_goals=None):
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
            raise cherrypy.HTTPRedirect("/wizardfordepartment/step4")
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

        raise cherrypy.HTTPRedirect("/wizardfordepartment/step4")


    @cherrypy.expose
    @require(member_of("users"))
    def step5(self):
        """
            Функция добавления связанных целей в кастомные таблицы компании
        """
        tmpl = lookup.get_template("wizardfordepartment_step5_page.html")
        params = cherrypy.request.headers
        step_desc = dict()
        step_desc['stage3_description'] = """
                <p>На предыдущих шаг вы сформировали спикок целей для подразделения, чтобы можно было измерить
                прогресс дстижения целей, необходимо добавить к ним показатели.</p>
                <p>Для каждой цели подобраны показатели, которые наиболее объективно отражают прогресс.</p>
                <p>Чтобы добавить показатель поставьте галочку напротив названия и нажмите
                <a href="#save_btn">Сохранить</a>.</p>
        """

        step_desc['name'] = "Шаг 5. Добавьте к выбранным целям показатели"
        step_desc['subheader'] = "" #  BMTObjects.get_desc("step3_stage3_subheader")
        step_desc['next_step'] = "6"

        current_map = BMTObjects.get_strategic_map_object(BMTObjects.current_strategic_map)
        print "STEP5. Current MAP: %s" % current_map.name
        if BMTObjects.current_strategic_map == BMTObjects.enterprise_strategic_map:
            # Выбрана карта компании, необходимо выбрать карту подразделения
            raise cherrypy.HTTPRedirect("/wizardfordepartment")

        try:
            map_custom_goals, map_custom_kpi = BMTObjects.load_cur_map_objects()[0:2]
            all_custom_goals, all_custom_kpi = BMTObjects.load_custom_goals_kpi()
            lib_kpi = BMTObjects.load_lib_goals_kpi()[1]
            lib_linked_kpi = BMTObjects.load_lib_links()[1]
            custom_linked_kpi = BMTObjects.load_custom_links()[1]
        except Exception as e:
            ShowError(e)

        #print "Custom MAP goals: %s" % map_custom_goals
        #print "Custom MAP KPI: %s" % map_custom_kpi
        #print "Custom linked KPI: %s" % custom_linked_kpi
        #print "LIB KPI: %s" % lib_kpi
        #print "LIB linked KPI: %s" % lib_linked_kpi

        grouped_goals = BMTObjects.group_goals(map_custom_goals)

        return tmpl.render(params=params, step_desc=step_desc, map_custom_goals=map_custom_goals, lib_kpi=lib_kpi,
                           lib_linked_kpi=lib_linked_kpi, map_custom_kpi=map_custom_kpi,
                           custom_linked_kpi=custom_linked_kpi, current_map=current_map,
                           all_custom_goals=all_custom_goals, all_custom_kpi=all_custom_kpi,
                           grouped_goals=grouped_goals, perspectives=BMTObjects.perspectives,
                           colors=BMTObjects.PERSPECTIVE_COLORS)


    @cherrypy.expose
    @require(member_of("users"))
    def step5save(self, picked_lib_kpi=None, picked_custom_kpi=None):
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
            raise cherrypy.HTTPRedirect("/wizardfordepartment/step5")
        else:
            if not isinstance(picked_custom_kpi, list):
                picked_custom_kpi = [picked_custom_kpi]
            print "picked_custom_kpi not empty. Save data."

            try:
                BMTObjects.save_kpi_to_map(picked_custom_kpi)
            except Exception as e:
                return ShowError(e)
            else:
                raise cherrypy.HTTPRedirect("/wizardfordepartment/step5")

        raise cherrypy.HTTPRedirect("/wizardfordepartment/step5")

    @cherrypy.expose
    @require(member_of("users"))
    def step6(self):
        # добавление мероприятий
        tmpl = lookup.get_template("wizardfordepartment_step6_page.html")

        step_desc = dict()
        step_desc['full_description'] = """
                <p>Все действия и задачи которые необходимо выполнить для достижения целей, мы предлагаем записать в
                виде Мероприятий.</p>
                <p>Обратите внимание, что мероприятие может быть длительным и включать много участников. Рекомендуем
                заполняйть поля мероприятий как можно более полно, чтобы любому участнику было понятно о чем идет
                речь.</p>
                <p>Так же рекомендуем обязательно заполнить поле <b>Плановый результат</b>.
                Это поможет в будущем однозначно трактовать полученные результаты.</p>

        """
        step_desc['name'] = "Шаг 6. Добавить мероприятия для подразделения"
        step_desc['subheader'] = ""
        step_desc['next_step'] = "7"

        current_map = BMTObjects.get_strategic_map_object(BMTObjects.current_strategic_map)
        print "STEP6. Current MAP: %s" % current_map.name
        if BMTObjects.current_strategic_map == BMTObjects.enterprise_strategic_map:
            # Выбрана карта компании, необходимо выбрать карту подразделения
            raise cherrypy.HTTPRedirect("/wizardfordepartment")

        try:
            map_custom_goals, a, map_custom_events = BMTObjects.load_cur_map_objects()[0:3]
        except Exception as e:
            return ShowError(e)

        grouped_goals = BMTObjects.group_goals(map_custom_goals)

        # Группируем мероприятия по целям и сортируем по различным условиям
        grouped_events = dict()
        for one in map_custom_events.values():
            if grouped_events.get(one.linked_goal_code):  # Если такая цель уже имеет мероприятия, то добавляем новое
                grouped_events[one.linked_goal_code].append(one.event_code)
            else:  # иначе создаем список, и добавлем первое
                grouped_events[one.linked_goal_code] = list()
                grouped_events[one.linked_goal_code].append(one.event_code)

        add_to_history("/wizardfordepartment/step6")
        return tmpl.render(current_map=current_map, grouped_goals=grouped_goals, perspectives=BMTObjects.perspectives,
                           colors=BMTObjects.PERSPECTIVE_COLORS, map_custom_goals=map_custom_goals,
                           step_desc=step_desc, map_custom_events=map_custom_events,
                           grouped_events=grouped_events)

    @cherrypy.expose
    @require(member_of("users"))
    def step7(self):
        tmpl = lookup.get_template("wizardfordepartment_step7_page.html")

        current_map = BMTObjects.get_strategic_map_object(BMTObjects.current_strategic_map)
        print "STEP6. Current MAP: %s" % current_map.name
        if BMTObjects.current_strategic_map == BMTObjects.enterprise_strategic_map:
            # Выбрана карта компании, необходимо выбрать карту подразделения
            raise cherrypy.HTTPRedirect("/wizardfordepartment")

        step_desc = dict()
        step_desc['full_description'] = """
            <p>Вы завершили создание стратегической карты для подразделения.</p>
            <p>Сделать уточнения, отредактировать, удалить данные в карте вы можете в разделе
            <a href="/maps/map?code=%s">Карты.</a></p>
            <p>Так же вы можете <a href="/wizardfordepartment">Создать карту для другого подразделения</a>.</p>
        """ % current_map.code
        step_desc['name'] = "Поздравляем!"
        step_desc['next_step'] = ""
        step_desc['subheader'] = ""

        return tmpl.render(current_map=current_map, step_desc=step_desc)

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
        try:
            org_structure, shift = BMTObjects.get_structure_sorted()
        except Exception as e:
            print "Ошибка при получении отсортированной орг. структуры. %s" % str(e)
            return ShowError(e)

        print "Орг. Структура компании: %s" % org_structure

        add_to_history("/wizard/step2")
        return tmpl.render(params=params, step_desc=step_desc, action=action,
                           org_structure=org_structure, persons=BMTObjects.persons,
                           status=status, org_edit=org_edit, shift=shift)

    @cherrypy.expose
    @require(member_of("users"))
    def step3(self):
        tmpl = lookup.get_template("wizard_step3_page.html")
        # Проверяем наличие основной карты компании, если нет - создаем со стандартными настройками
        if not BMTObjects.get_strategic_map_object(BMTObjects.enterprise_strategic_map):
            root = BMTObjects.get_org_structure_root()
            if root:
                BMTObjects.create_ent_strategic_map(owner=root.director, cycle=1, cycle_count=3)

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
        print "MAP: %s" %  BMTObjects.get_strategic_map_object(BMTObjects.current_strategic_map)

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
        # TODO: заменить шаги мастера по созданию стндартных объектов на универсальные действия
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

        add_to_history("/wizard/step7")

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
                BMTObjects.create_dep_strategic_map(int(one), name="Стратегическая карта: %s" % orgs[int(one)].org_name,
                                                    owner=orgs[int(one)].director)
        except Exception as e:
            print "Step7 SAVE. Ошибка: %s" % str(e)
            ShowError(e)

        raise cherrypy.HTTPRedirect(history_back())

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


class OrgStructure(object):

    @cherrypy.expose
    @require(member_of("users"))
    def index(self):
        raise cherrypy.HTTPRedirect("/wizard/step2")


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
        group_goals = BMTObjects.group_goals(cur_map_goals)

        return tmpl.render(step_desc=step_desc,
                           current_map=BMTObjects.get_strategic_map_object(BMTObjects.current_strategic_map),
                           cur_map_goals=cur_map_goals, perspectives=BMTObjects.perspectives,
                           group_goals=group_goals)


    @cherrypy.expose
    @require(member_of("users"))
    def save(self, name=None, description=None, perspective=None, linked=None):
        """
            Сохраняем новую цель в кастомные цели и добавляем в текущую карту
        """

        print "New GOAL SAVE : %s " % cherrypy.request.params

        if None in [name, description, perspective]:
            print "Один из параметров не указан. Параметры: %s" % cherrypy.request.params
            raise cherrypy.HTTPRedirect(history.pop())

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

        raise cherrypy.HTTPRedirect(history.pop())

    @cherrypy.expose
    @require(member_of("users"))
    def edit(self, code=None):
        # выводим страницу редактирования цели
        print "EDIT GOAL."
        tmpl = lookup.get_template("goals_edit_page.html")
        step_desc = dict()
        step_desc['full_description'] = "Редактирование цели"
        step_desc['name'] = "Редактирование цели"
        step_desc['next_step'] = "/maps?code=%s" % BMTObjects.current_strategic_map

        if not code:
            print "Параметр code указан. Параметры: %s" % cherrypy.request.params
            raise cherrypy.HTTPRedirect(history.pop())

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
        group_goals = BMTObjects.group_goals(cur_map_goals)

        print "Current MAP : %s" % BMTObjects.current_strategic_map
        print "Current MAP goals: %s" % cur_map_goals
        print "Linked goals: %s" % linked_goals

        return tmpl.render(step_desc=step_desc,
                           current_map=BMTObjects.get_strategic_map_object(BMTObjects.current_strategic_map),
                           cur_map_goals=cur_map_goals, perspectives=BMTObjects.perspectives,
                           goal=goal, linked_goals=linked_goals, escapef=BMTObjects.escape,
                           group_goals=group_goals)

    @cherrypy.expose
    @require(member_of("users"))
    def delete(self, code=None):
        # Удаляем цель из текущей карты. Цель не удаляется из базы, остается в кастомных и видна в библиотеке.
        print "DELETE GOAL."
        if not code:
            print "GOAL code empty. Redirect to /maps?code=%s" % BMTObjects.current_strategic_map
            raise cherrypy.HTTPRedirect(history.pop())

        try:
            BMTObjects.remove_goal_from_map(code, BMTObjects.current_strategic_map)
        except Exception as e:
            print "Ошибка %s " % str(e)
            return ShowError(e)
        else:
            raise cherrypy.HTTPRedirect(history.pop())

    @cherrypy.expose
    @require(member_of("users"))
    def update(self, code=None, name=None, description=None, perspective=None, linked=None):
        # Сохраняем данные после редактирования цели
        print "UPDATE GOAL."

        if None in [code, name, description, perspective]:
            print "Один из параметров не указан. Параметры: %s" % cherrypy.request.params
            raise cherrypy.HTTPRedirect(history.pop())

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

        raise cherrypy.HTTPRedirect(history.pop())


class KPIs(object):

    @cherrypy.expose
    @require(member_of("users"))
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
        group_goals = BMTObjects.group_goals(cur_map_goals)

        return tmpl.render(step_desc=step_desc,
                           current_map=BMTObjects.get_strategic_map_object(BMTObjects.current_strategic_map),
                           cur_map_goals=cur_map_goals, perspectives=BMTObjects.perspectives,
                           persons=BMTObjects.persons, kpi_scale_type=BMTObjects.KPI_SCALE_TYPE,
                           measures=BMTObjects.MEASURES, cycles=BMTObjects.CYCLES, group_goals=group_goals)

    @cherrypy.expose
    @require(member_of("users"))
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
            raise cherrypy.HTTPRedirect(history_back())

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
            kpi_fields['cycle'] = int(cycles)
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
                raise cherrypy.HTTPRedirect(history_back())
            else:
                print "Стратегический показатель. Создаем связь с целью и целевые значения."
                try:
                    BMTObjects.create_custom_link_kpi_to_goal(kpi_linked_goal, status[1])
                except Exception as e:
                    print "Ошибка при создании связи KPI to GOAL. %s" % str(e)
                    return ShowError(e)

                start_date = datetime.datetime.strptime(start_date, "%d.%m.%Y").date()
                """
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
                """
                # period_date, period_name = BMTObjects.make_periods_for_kpi(start_date, int(plan_period))
                periods = BMTObjects.make_periods_for_kpi_new(start_date, int(plan_period))

                # Считаем даты периодов, создаем записи для KPI Target
                # даты отчета по целевым значениям назначаются на следующий день после окончания перида, т.е. 1 число
                # следующего месяца.

                for one in periods.values():
                    kpi_target['kpi_code'] = str(status[1])
                    kpi_target['date'] = one[2]
                    kpi_target['period_code'] = one[0]
                    kpi_target['period_name'] = one[1]
                    try:
                        BMTObjects.save_kpi_target_value(kpi_target)
                    except Exception as e:
                        print "Ошибка при создании KPI TARGET. %s" % str(e)
                        return ShowError(e)

                # создаем авто периоды для целевых значений
                try:
                    BMTObjects.create_auto_target_values(str(status[1]))
                except Exception as e:
                    print "Ошибка при создании AUTO PERIOD for TARGET. /kpi/save(). %s" % str(e)
                    return ShowError(e)

                raise cherrypy.HTTPRedirect("/kpi/newstage2?code=%s" % status[1])


    @cherrypy.expose
    @require(member_of("users"))
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
    @require(member_of("users"))
    def savestage2(self, kpi_code=None, period_code=None, target_value=None):
        """

        :param kpi_code:
        :param period_code:
        :param target_value:
        :return:
        """

        #print kpi_code
        #print period_code
        #print target_value

        kpi_target = dict()
        kpi_target['kpi_code'] = str(kpi_code)
        kpi_target['period_code'] = str(re.split("_",period_code)[1])
        kpi_target['first_value'] = float(target_value)
        kpi_target['second_value'] = float(target_value)
        try:
            BMTObjects.save_kpi_target_value(kpi_target)
        except Exception as e:
            print "Ошибка при обновлении KPI TARGET. %s" % str(e)
            return ShowError(e)
        else:
            # пересчет значений для авто периодов целевых значений
            try:
                BMTObjects.calculate_auto_target_values(for_kpi=str(kpi_code))
            except Exception as e:
                print "Ошибка при вычислении AUTO KPI for TARGET. /kpi/savestage2(). %s" % str(e)
                return ShowError(e)

        return "ok"

    @cherrypy.expose
    @require(member_of("users"))
    def edit(self, code=None):
        # выводим страницу редактирования показателя, без целевых значений, это отдельный этап
        print "EDIT KPI."
        tmpl = lookup.get_template("kpi_edit_page.html")
        step_desc = dict()
        step_desc['full_description'] = ""
        step_desc['name'] = "Редактирование показателя"
        step_desc['next_step'] = "/maps?code=%s" % BMTObjects.current_strategic_map

        if not code:
            print "Параметр code указан. Параметры: %s" % cherrypy.request.params
            raise cherrypy.HTTPRedirect(history.pop())

        try:
            cur_map_goals, map_kpi, events, map_opkpi = BMTObjects.load_cur_map_objects(BMTObjects.current_strategic_map)
            # Возвращает цель или None
            g = BMTObjects.load_custom_links(for_kpi=code)
            if g:
                goal, kpi = BMTObjects.load_custom_goals_kpi(kpi_code=code, goal_code=g.goal_code)
            else:
                goal, kpi = BMTObjects.load_custom_goals_kpi(kpi_code=code, goal_code="0")
            print "kpi", kpi.code
            print "goal", goal
            group_goals = BMTObjects.group_goals(cur_map_goals)
        except Exception as e:
            print "Ошибка при открытии на редактирование показателя %s. Ошибка: %s " % (code, str(e.args))
            return ShowError(e)

        # print "Current MAP : %s" % BMTObjects.current_strategic_map
        # print "Current MAP kpi: %s" % cur_map_goals

        try:
            # Загружаем связи цель - показатели
            linked_kpi = BMTObjects.load_custom_links()[1]
        except Exception as e:
            print "Ошибка при загрузке данных для редактирования показателя %s. Ошибка: %s " % (code, str(e.args))
            return ShowError(e)

        if goal:
            add_to_history("/maps/kpi#%s" % goal.code)
        else:
            add_to_history("/maps/kpi#%s" % kpi.code)
        return tmpl.render(step_desc=step_desc,
                           current_map=BMTObjects.get_strategic_map_object(BMTObjects.current_strategic_map),
                           cur_map_goals=cur_map_goals, perspectives=BMTObjects.perspectives,
                           goal=goal, kpi=kpi, persons=BMTObjects.persons, kpi_scale_type=BMTObjects.KPI_SCALE_TYPE,
                           measures=BMTObjects.MEASURES, cycles=BMTObjects.CYCLES, map_kpi=map_kpi,
                           group_goals=group_goals, linked_kpi=linked_kpi, map_opkpi=map_opkpi)

    @cherrypy.expose
    @require(member_of("users"))
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

        raise cherrypy.HTTPRedirect(history_back())

    @cherrypy.expose
    @require(member_of("users"))
    def editstage2(self, code=None):
        # Редактирование целевых значений для показателя
        tmpl = lookup.get_template("kpi_editstage2_page.html")
        step_desc = dict()
        step_desc['full_description'] = ""
        step_desc['name'] = "Целевые значения"
        step_desc['next_step'] = "/maps?code=%s" % BMTObjects.current_strategic_map

        try:
            # Возвращает цель или None
            g = BMTObjects.load_custom_links(for_kpi=code)
            if g:
                goal, kpi = BMTObjects.load_custom_goals_kpi(kpi_code=code, goal_code=g.goal_code)
            else:
                goal, kpi = BMTObjects.load_custom_goals_kpi(kpi_code=code, goal_code="0")
            print "kpi", kpi.code
            print "goal", goal
            target_values = BMTObjects.get_kpi_target_value(code)
        except Exception as e:
            print "Ошибка: %s " % str(e)
            return ShowError(e)

        print "Current KPI: %s" % kpi
        print "Goal for KPI: %s" % goal
        print "Current KPI TARGETS: %s" % target_values

        add_to_history("/maps/kpi#%s" % goal.code)
        return tmpl.render(step_desc=step_desc,
                           current_map=BMTObjects.get_strategic_map_object(BMTObjects.current_strategic_map),
                           kpi=kpi, target_values=target_values, goal=goal, perspectives=BMTObjects.perspectives,
                           persons=BMTObjects.persons, kpi_scale_type=BMTObjects.KPI_SCALE_TYPE,
                           measures=BMTObjects.MEASURES, cycles=BMTObjects.CYCLES)

    @cherrypy.expose
    @require(member_of("users"))
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
            # print "Количество периодов: %s" % int(plan_period)
            # print "Стартовая дата: %s" % start_date
            """
            period_date = dict()
            period_name = dict()

            for one in range(1, int(plan_period) + 1):
                print "Период: %s" % one

                year = start_date.year + ((start_date.month + one - 1) // 12)
                month = ((start_date.month % 12) + one) - 12 * ((start_date.month + one) // 12)
                if not month:
                    month = 12

                print year, month

                period_date[one] = datetime.datetime(year, month, 1)
                if (period_date[one].month - 1) == 0:
                    period_name[one] = str(BMTObjects.PERIOD_NAME[period_date[one].month - 1]) + " " + \
                                       str(period_date[one].year - 1)
                else:
                    period_name[one] = str(BMTObjects.PERIOD_NAME[period_date[one].month - 1]) + " " + \
                                       str(period_date[one].year)

                print "Отчетная дата периода: %s" % period_date[one]
                print "Название отчетного периода: %s" % period_name[one]
            """
            # period_date, period_name = BMTObjects.make_periods_for_kpi(start_date, int(plan_period))
            periods = BMTObjects.make_periods_for_kpi_new(start_date, int(plan_period))

            # Считаем даты периодов, создаем записи для KPI Target
            # даты отчета по целевым значениям назначаются на следующий день после окончания перида, т.е. 1 число
            # следующего месяца.

            for one in periods.values():
                kpi_target['kpi_code'] = str(kpi_code)
                kpi_target['date'] = one[2]
                kpi_target['period_code'] = one[0]
                kpi_target['period_name'] = one[1]
                try:
                    BMTObjects.save_kpi_target_value(kpi_target)
                except Exception as e:
                    print "Ошибка при создании KPI TARGET. %s" % str(e)
                    return ShowError(e)

            # создаем авто периоды для целевых значений
            try:
                BMTObjects.create_auto_target_values(kpi_code)
            except Exception as e:
                print "Ошибка при создании AUTO PERIOD for TARGET. updatestage2(). %s" % str(e)
                return ShowError(e)
            try:
                BMTObjects.calculate_auto_target_values(for_kpi=kpi_code)
            except Exception as e:
                print "Ошибка при вычислении AUTO KPI for TARGET. updatestage2(). %s" % str(e)
                return ShowError(e)


            raise cherrypy.HTTPRedirect("/kpi/editstage2?code=%s" % kpi_code)

        if kpi_code and period_code and target_value:
            # Обновляем значения
            # print kpi_code
            # print period_code
            # print target_value

            kpi_target = dict()
            kpi_target['kpi_code'] = str(kpi_code)
            kpi_target['period_code'] = str(re.split("_",period_code)[1])
            kpi_target['first_value'] = float(target_value)
            kpi_target['second_value'] = float(target_value)
            try:
                BMTObjects.save_kpi_target_value(kpi_target)
            except Exception as e:
                print "Ошибка при обновлении KPI TARGET. %s" % str(e)
                return ShowError(e)
            else:
                try:
                    BMTObjects.calculate_auto_target_values(for_kpi=kpi_code)
                except Exception as e:
                    print "Ошибка при вычислении AUTO KPI for TARGET. updatestage2(). %s" % str(e)
                    return ShowError(e)

            return "ok"

    @cherrypy.expose
    @require(member_of("users"))
    def updatestage2_one(self, kpi_code=None, plan_period=None, start_date=None, cycles=None):
        """
        Сохраняем новый отчетный период, готовим объекты целевых значений для заполнения

        :param kpi_code:
        :param plan_period:
        :param start_date:
        :param cycles:
        :return:
        """

        print "KPI UPDATE stage2 new TARGET period"
        print "Параметры запроса: %s" % cherrypy.request.params

        start_date = datetime.datetime.strptime(start_date, "%m.%Y").date()
        print "Количество периодов: %s" % int(plan_period)
        print "Стартовая дата: %s" % start_date

        # Стандартная схема расчета периодов не годится
        """
        print "Период: %s" % one
        period_date[one] = datetime.datetime(start_date.year + (start_date.month // 12),
                                             ((start_date.month % 12) + one) - 12*(one // 12), 1)
        if (period_date[one].month - 1) == 0:
            period_name[one] = str(BMTObjects.PERIOD_NAME[period_date[one].month - 1]) + " " + \
                               str(period_date[one].year - 1)
        else:
            period_name[one] = str(BMTObjects.PERIOD_NAME[period_date[one].month - 1]) + " " + \
                               str(period_date[one].year)

        print "Отчетная дата периода: %s" % period_date[one]
        print "Название отчетного периода: %s" % period_name[one]
        """
        if int(plan_period) == 1:
            periods = BMTObjects.define_period_new(start_date)
        else:
            print "/kpi/updatestage2_one(). Количество периодов больше 1. Plan_period = %s" % plan_period
            raise cherrypy.HTTPRedirect("/kpi/editstage2?code=%s" % kpi_code)

        kpi_target = dict()
        kpi_target['kpi_code'] = str(kpi_code)
        kpi_target['date'] = periods[2]
        kpi_target['period_code'] = periods[0]
        kpi_target['period_name'] = periods[1]

        try:
            BMTObjects.save_kpi_target_value(kpi_target)
        except Exception as e:
            print "Ошибка при создании KPI TARGET. updatestage2_one(). %s" % str(e)
            return ShowError(e)
        else:
            # создаем авто периоды для целевых значений
            try:
                BMTObjects.create_auto_target_values(kpi_code)
            except Exception as e:
                print "Ошибка при создании AUTO PERIOD for TARGET. /kpi/updatestage2_one(). %s" % str(e)
                return ShowError(e)
            # рассчитываем данные для авто периодов
            try:
                BMTObjects.calculate_auto_target_values(for_kpi=kpi_code)
            except Exception as e:
                print "Ошибка при вычислении AUTO PERIOD for TARGET. /kpi/updatestage2_one(). %s" % str(e)
                return ShowError(e)

        raise cherrypy.HTTPRedirect("/kpi/editstage2?code=%s" % kpi_code)

    @cherrypy.expose
    @require(member_of("users"))
    def delete_target(self, code=None, period_code=None):
        """
        Удаляем целевое значение для указанного показателя и периода

        :param code:
        :param period_code:
        :return:
        """

        print "DELETE TARGET for KPI: %s" % code
        if not code:
            print "KPI code empty. Redirect."
            raise cherrypy.HTTPRedirect(history_back())

        try:
            BMTObjects.delete_kpi_target_value(kpi_code=code, period_code=period_code)
        except Exception as e:
            print "Ошибка %s " % str(e)
            return ShowError(e)
        else:
            # пересоздаем авто периоды для целевых значений
            try:
                BMTObjects.create_auto_target_values(code)
            except Exception as e:
                print "Ошибка при создании AUTO PERIOD for TARGET. delete_target(). %s" % str(e)
                return ShowError(e)
            # пересчитываем данные для авто периодов
            try:
                BMTObjects.calculate_auto_target_values(for_kpi=code)
            except Exception as e:
                print "Ошибка при вычислении AUTO PERIOD for TARGET. /kpi/delete_target(). %s" % str(e)
                return ShowError(e)

            raise cherrypy.HTTPRedirect("/kpi/editstage2?code=%s" % code)

    @cherrypy.expose
    @require(member_of("users"))
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
            raise cherrypy.HTTPRedirect(history_back())

    @cherrypy.expose
    @require(member_of("users"))
    def copy(self, code=None):
        """
        Создаем копию показателя

        :param code: код показателя, который надо скопировать
        :return:
        """

        kpi_fields = dict()

        try:
            kpi = BMTObjects.load_custom_goals_kpi(kpi_code=code)[1]
            kpi_linked_goal = BMTObjects.load_custom_links(for_kpi=code)
            kpi_fields['name'] = str(kpi.name)
            kpi_fields['description'] = str(kpi.description)
            kpi_fields['formula'] = str(kpi.formula)
            kpi_fields['link_to_desc'] = str(kpi.link_to_desc)
            kpi_fields['measure'] = int(kpi.measure)
            kpi_fields['target_responsible'] = int(kpi.target_responsible)
            kpi_fields['fact_responsible'] = int(kpi.fact_responsible)
            kpi_fields['cycle'] = int(kpi.cycle)
            kpi_fields['data_source'] = str(kpi.data_source)
            kpi_fields['kpi_scale_type'] = int(kpi.kpi_scale_type)
        except Exception as e:
            print "Copy KPI. Ошибка при обработке параметров запроса. %s" % str(e)
            return ShowError(e)

        if not kpi_linked_goal or not kpi:
            print "Copy KPI. Пустые значения KPI и KPI_LINKED_GOAL."
            return ShowError("Ошибка при копировании. Не найдены данные или не указана связанная цель, для KPI: %s"
                             % code)

        try:
            # Записываем новый показатель и ждем возврата его кода
            status = BMTObjects.create_new_custom_kpi(kpi_fields)
        except Exception as e:
            print "Copy KPI. Ошибка при создании CUSTOM KPI. %s" % str(e)
            return ShowError(e)
        else:
            # привязываем новый показатель к цели
            if kpi_linked_goal.goal_code == "0":
                print "Copy KPI. Операционный показатель. Возвращаемся обратно."
                raise cherrypy.HTTPRedirect(history_back())
            else:
                print "Copy KPI. Стратегический показатель. Создаем связь с целью и целевые значения."
                try:
                    BMTObjects.create_custom_link_kpi_to_goal(kpi_linked_goal.goal_code, status[1])
                except Exception as e:
                    print "Copy KPI. Ошибка при создании связи KPI to GOAL. %s" % str(e)
                    return ShowError(e)

                # Получаем целевые значения для оригинала
                # Если они есть - копируем  в новый, если нет - ничего не делаем
                try:
                    kpi_target = BMTObjects.get_kpi_target_value(kpi_code=code)
                except Exception as e:
                    print "Copy KPI. Ошибка при получении KPI TARGET. %s" % str(e)
                    return ShowError(e)

                if kpi_target:
                    for one in kpi_target:
                        target = dict()
                        target['kpi_code'] = str(status[1])
                        target['date'] = one.date
                        target['period_code'] = one.period_code
                        target['period_name'] = one.period_name
                        target['first_value'] = one.first_value
                        try:
                            BMTObjects.save_kpi_target_value(target)
                        except Exception as e:
                            print "Copy KPI. Ошибка при копировании KPI TARGET. %s" % str(e)
                            return ShowError(e)
                    # создаем авто периоды для целевых значений
                    try:
                        BMTObjects.create_auto_target_values(str(status[1]))
                    except Exception as e:
                        print "Ошибка при создании AUTO PERIOD for TARGET. /kpi/copy. %s" % str(e)
                        return ShowError(e)
                    # рассчитываем данные для авто периодов
                    try:
                        BMTObjects.calculate_auto_target_values(for_kpi=str(status[1]))
                    except Exception as e:
                        print "Ошибка при вычислении AUTO PERIOD for TARGET. /kpi/copy. %s" % str(e)
                        return ShowError(e)

            raise cherrypy.HTTPRedirect("/kpi/edit?code=%s" % status[1])

    @cherrypy.expose
    #@require(member_of("users"))
    def fact(self, code=None):
        # Редактирование фактических значений для показателя
        tmpl = lookup.get_template("kpi_fact_page.html")
        step_desc = dict()
        step_desc['full_description'] = ""
        step_desc['name'] = "Фактические значения"
        step_desc['next_step'] = "/maps?code=%s" % BMTObjects.current_strategic_map

        try:
            # Возвращает цель или None
            target_values = BMTObjects.get_kpi_target_value(code)
            print "target_values"
            fact_values = BMTObjects.get_kpi_fact_values(code)
            print fact_values
            goal, kpi = BMTObjects.load_custom_goals_kpi(kpi_code=code)
            print "goal, kpi"
        except Exception as e:
            print "/kpi/fact(). Ошибка при получении фактических значений показателя. KPI : %s. %s " % (code, str(e))
            return ShowError(e)

        add_to_history("/maps/kpi#%s" % code)
        return tmpl.render(step_desc=step_desc,
                           current_map=BMTObjects.get_strategic_map_object(BMTObjects.current_strategic_map),
                           target_values=target_values, perspectives=BMTObjects.perspectives,
                           persons=BMTObjects.persons, kpi_scale_type=BMTObjects.KPI_SCALE_TYPE,
                           measures=BMTObjects.MEASURES, cycles=BMTObjects.CYCLES,
                           fact_values=fact_values, kpi=kpi)

    @cherrypy.expose
    #@require(member_of("users"))
    def add_fact(self, kpi_code=None, fact_value=None, fact_date=None, period_code=None):
        """
        Сохраняем фактические данные показателя

        :param kpi_code:
        :param fact_value:
        :param fact_date:
        :param period_code:
        :return:
        """

        print kpi_code
        print period_code
        print fact_value
        print fact_date

        kpi_fact = dict()
        if kpi_code and fact_date and fact_value and period_code:
            kpi_fact['kpi_code'] = str(kpi_code)
            kpi_fact['fact_value'] = float(fact_value)
            kpi_fact['create_date'] = datetime.datetime.strptime(fact_date, "%d.%m.%Y").date()
        else:
            print "Не указаны параметры для сохранения факта. /kpi/add_fact()"
            raise ShowError("Не указаны параметры для сохранения факта.")

        if period_code:
            # добавляем в конкретный период
            kpi_fact['period'] = int(period_code)
        else:
            # сначала надо определить период
            try:
                fact_period = BMTObjects.get_fact_period_code(for_kpi=kpi_code, date=fact_date)
            except Exception as e:
                s = "Ошибка при получении периода для даты фактического показателя. /kpi/add_fact(). %s" % str(e)
                print s
                raise ShowError(s)
            else:
                kpi_fact['period_code'] = int(fact_period)

        try:
            BMTObjects.save_kpi_fact_value(kpi_fact)
        except Exception as e:
            print "Ошибка при сохранении KPI FACT. /kpi/add_fact(). %s" % str(e)
            return ShowError(e)
        else:
            # пересчет значений для авто периодов фактических значений
            try:
                BMTObjects.calculate_auto_fact_values(for_kpi=str(kpi_code))
            except Exception as e:
                print "Ошибка при вычислении AUTO KPI FACT. /kpi/add_fact. %s" % str(e)
                return ShowError(e)

        raise cherrypy.HTTPRedirect("/kpi/fact?code=%s" % kpi_code)

    @cherrypy.expose
    #@require(member_of("users"))
    def pfact(self, period_code=None):
        """
        Функция ввода фактических значений для всех доступных показателей за указанный период.
        Можно поменять период, для всех значений.

        :param period_code: код периода
        :return:
        """
        # Добавление фактических значений показателей
        tmpl = lookup.get_template("kpi_period_fact_page.html")
        step_desc = dict()
        step_desc['full_description'] = ""
        step_desc['name'] = "Ввод факта"
        step_desc['next_step'] = "/maps?code=%s" % BMTObjects.current_strategic_map

        dd = datetime.datetime.now()
        if not period_code:
            # Определяем текущий период по сегодняшней дате
            period = BMTObjects.define_period_new(dd)
        else:
            # или по первому дню периода
            month = int(period_code) // 10000
            year = int(period_code) % 10000
            period = BMTObjects.define_period_new(datetime.datetime.strptime("01.%s.%s" % (month, year),
                                                                             "%d.%m.%Y").date())

        periods = list()
        for one in range(0, 3):
            month = dd.month - one
            year = dd.year
            if month == 0:
                month = 12
                year -= 1
            elif month < 0:
                month = 12 + dd.month - one
                year -= 1
            dd2 = "01.%s.%s" % (month, year)
            periods.append(BMTObjects.define_period_new(datetime.datetime.strptime(dd2 , "%d.%m.%Y").date()))

        periods.reverse()

        try:
            map_goals, map_kpi, map_events, map_opkpi = BMTObjects.load_cur_map_objects(BMTObjects.current_strategic_map)
        except Exception as e:
            print "/kpi/pfact(). Ошибка при получении показателей для карты."
            return ShowError(e)

        try:
            custom_kpi_links = BMTObjects.load_map_links(for_goals=map_goals.keys(), for_kpi=map_kpi.keys())
        except Exception as e:
            return ShowError(e)

        # Группируем цели по перспективами и порядку расположения
        group_goals = BMTObjects.group_goals(map_goals)

        fact_values = dict()
        target_values = dict()
        # period_code = "22016"
        for kpi in map_kpi.keys():
            target_values[kpi] = None
            try:
                target_values[kpi] = BMTObjects.get_kpi_target_value(kpi_code=kpi, period_code=period[0])
            except Exception as e:
                print "/kpi/pfact. Ошибка получения плановых значений для kpi = %s. %s" % (kpi, str(e))
                return ShowError(e)

            fact_values[kpi] = None
            try:
                fact = BMTObjects.get_kpi_fact_values(for_kpi=kpi, period_code=period[0])
                if fact:
                    fact.reverse()
                    fact_values[kpi] = fact[0]
                print "KPI: ", kpi, "Fact: ", fact_values[kpi]
            except Exception as e:
                print "/kpi/pfact. Ошибка получения фактических значений для kpi = %s. %s" % (kpi, str(e))
                return ShowError(e)

        add_to_history("/maps/kpi")
        return tmpl.render(step_desc=step_desc,
                           current_map=BMTObjects.get_strategic_map_object(BMTObjects.current_strategic_map),
                           target_values=target_values, perspectives=BMTObjects.perspectives,
                           persons=BMTObjects.persons, kpi_scale_type=BMTObjects.KPI_SCALE_TYPE,
                           measures=BMTObjects.MEASURES, cycles=BMTObjects.CYCLES,
                           fact_values=fact_values, m_spec=BMTObjects.MEASURES_SPEC, m_form=BMTObjects.MEASURES_FORMAT,
                           group_goals=group_goals, custom_kpi_links=custom_kpi_links, map_goals=map_goals,
                           map_kpi=map_kpi, period_code=period_code,
                           period=period, periods=periods)


    @cherrypy.expose
    #@require(member_of("users"))
    def add_fact2(self, kpi_code=None, fact_value=None, fact_date=None, period_code=None):
        """
        Сохраняем фактические данные показателя

        :param kpi_code:
        :param fact_value:
        :param fact_date:
        :param period_code:
        :return:
        """

        print kpi_code
        print period_code
        print fact_value
        print fact_date

        kpi_fact = dict()
        if kpi_code and fact_value and (period_code or fact_date):
            kpi_fact['kpi_code'] = str(kpi_code)
            kpi_fact['fact_value'] = float(fact_value)
        else:
            print "Не указаны параметры для сохранения факта. /kpi/add_fact2()"
            return "error"

        if fact_date:
            # если указана дата ввода
            kpi_fact['create_date'] = datetime.datetime.strptime(fact_date, "%d.%m.%Y").date()
        else:
            # если не указана, ставим сегодня
            kpi_fact['create_date'] = datetime.datetime.now()

        if period_code:
            # добавляем в конкретный период
            kpi_fact['period_code'] = int(period_code)
        else:
            # сначала надо определить период
            try:
                fact_period = BMTObjects.get_fact_period_code(for_kpi=kpi_code, date=fact_date)
            except Exception as e:
                print "Ошибка при получении периода для даты фактического показателя. /kpi/add_fact2(). %s" % str(e)
                return "error"
            else:
                kpi_fact['period'] = int(fact_period)

        try:
            BMTObjects.save_kpi_fact_value(kpi_fact)
        except Exception as e:
            print "Ошибка при сохранении KPI FACT. /kpi/add_fact2(). %s" % str(e)
            return "error"
        else:
            # пересчет значений для авто периодов фактических значений
            try:
                BMTObjects.calculate_auto_fact_values(for_kpi=str(kpi_code))
            except Exception as e:
                print "Ошибка при вычислении AUTO KPI FACT. /kpi/add_fact2. %s" % str(e)
                return "error"

        return "ok"


class MotivationCard(object):

    @cherrypy.expose
    @require(member_of("users"))
    def index(self, code=None):
        # Вывести все мотивационные карточки
        tmpl = lookup.get_template("motivation_list_page.html")
        step_desc = dict()
        step_desc['full_description'] = ""
        step_desc['name'] = "Мотивационные карты"
        step_desc['next_step'] = ""

        try:
            motivation_cards = BMTObjects.get_motivation_cards()
        except Exception as e:
            print "Ошибка при получении мотивационных карт. %s" % str(e)
            return ShowError(e)

        return tmpl.render(step_desc=step_desc,
                           current_map=BMTObjects.get_strategic_map_object(BMTObjects.current_strategic_map),
                           persons=BMTObjects.persons, motivation_cards=motivation_cards)

    @cherrypy.expose
    @require(member_of("users"))
    def show(self, code=None):
        # Вывести указанную карту
        tmpl = lookup.get_template("motivation_card_page.html")
        step_desc = dict()
        step_desc['full_description'] = ""
        step_desc['name'] = "Мотивационные карты"
        step_desc['next_step'] = ""

        # TODO: ДОбавить срок действия стратегической карты
        # TODO: Специальные виды показателей для мотивации: штрафы, смарт задачи
        # TODO: Добавить управление пользователями, прикрепление к отделам и т.д.
        class Org():
            boss = 3
            dep_name = "Первый отдел"

        org = {1: Org(), 2: Org(), 3: Org(), 4: Org()}

        try:
            motivation_card = BMTObjects.get_motivation_cards(card_code=code)
            map_goals, map_kpi, map_events, map_opkpi = BMTObjects.load_cur_map_objects(BMTObjects.current_strategic_map)
            motivation_records = BMTObjects.get_motivation_card_records(code)
        except Exception as e:
            print "Ошибка при получении мотивационных карт. %s" % str(e)
            return ShowError(e)

        if not motivation_card:
            print "Нет такой карты: %s" % code
            raise cherrypy.HTTPRedirect("/motivation")

        return tmpl.render(step_desc=step_desc,
                           current_map=BMTObjects.get_strategic_map_object(BMTObjects.current_strategic_map),
                           persons=BMTObjects.persons, motivation_card=motivation_card,
                           map_kpi=map_kpi, map_opkpi=map_opkpi, motivation_records=motivation_records,
                           org=org)

    @cherrypy.expose
    @require(member_of("users"))
    def save(self, user_id=None, group_id=None, salary=None, salary_fix_p=None, salary_var_p=None,
             salary_fix=None, salary_var=None, user_approve=None, boss_approve=None,
             edge1=None, edge2=None, edge3=None, var_edge_1=None, var_edge_2=None, var_edge_3=None):
        """
        Создание новой карты мотивации

        :param user_id:
        :param group_id:
        :param salary:
        :param salary_fix_p:
        :param salary_var_p:
        :param salary_fix:
        :param salary_var:
        :param user_approve:
        :param boss_approve:
        :param edge1:
        :param edge2:
        :param edge3:
        :param var_edge_1:
        :param var_edge_2:
        :param var_edge_3:
        :return:
        """

        # TODO: при создании новой карты надо проверять есть уже действующая карта. Может быть одна активная.

        p = cherrypy.request.params
        if not user_id:
            print "Один из параметров не указан. Параметры: %s" % p
            raise cherrypy.HTTPRedirect("/motivation")

        card_fields = dict()
        try:
            for k in p.keys():
                print k, " : ", p[k]
                card_fields[k] = int(p[k])
        except Exception as e:
            print "Ошибка при проверке параметров. %s" % str(e)
            return ShowError(e)

        try:
            # Создаем новую карту мотивации
            status = BMTObjects.create_motivation_card(card_fields)
        except Exception as e:
            print "Ошибка при создании MOTIVATION CARD. %s" % str(e)
            return ShowError(e)
        else:
            print "Карта мотивации создана: %s" % status[1]

        raise cherrypy.HTTPRedirect("/motivation")

    @cherrypy.expose
    @require(member_of("users"))
    def add_kpi(self, motivation_card=None, weight=None, kpi=None):

        p = cherrypy.request.params
        if None in [motivation_card, weight, kpi]:
            print "Один из параметров не указан. Параметры: %s" % p
            raise cherrypy.HTTPRedirect("/motivation")

        try:
            # добавляем показатель в карту мотивации
            BMTObjects.add_kpi_to_motivation_card(str(motivation_card), int(weight), str(kpi))
        except Exception as e:
            print "Ошибка при добавлении KPI в MOTIVATION CARD. %s" % str(e)
            return ShowError(e)
        else:
            print "Показатель добавлен."

        raise cherrypy.HTTPRedirect("/motivation/show?code=%s" % motivation_card)

    @cherrypy.expose
    @require(member_of("users"))
    def update_kpi(self, motivation_card=None, weight=None, kpi=None):

        p = cherrypy.request.params

        print "Парметры: %s " % p

        if None in [motivation_card, weight, kpi]:
            print "Один из параметров не указан. Параметры: %s" % p
            raise cherrypy.HTTPRedirect("/motivation")

        try:
            # обновляем показатель в карте мотивации
            BMTObjects.update_kpi_in_motivation_card(str(motivation_card), int(weight), str(kpi))
        except Exception as e:
            print "Ошибка при обновлении KPI в MOTIVATION CARD. %s" % str(e)
            return ShowError(e)
        else:
            print "Показатель обновлен."

        raise cherrypy.HTTPRedirect("/motivation")

    @cherrypy.expose
    @require(member_of("users"))
    def remove_kpi(self, motivation_card=None, kpi=None):

        p = cherrypy.request.params

        print "Парметры: %s " % p

        if None in [motivation_card, kpi]:
            print "Один из параметров не указан. Параметры: %s" % p
            raise cherrypy.HTTPRedirect("/motivation")

        try:
            # удаляем показатель из карты мотивации
            BMTObjects.delete_kpi_from_motivation_card(str(motivation_card), str(kpi))
        except Exception as e:
            print "Ошибка при удалении KPI из MOTIVATION CARD. %s" % str(e)
            return ShowError(e)
        else:
            print "Показатель удален."

        raise cherrypy.HTTPRedirect("/motivation")


class Users(object):

    @cherrypy.expose
    @require(member_of("users"))
    def new(self):
        tmpl = lookup.get_template("user_new_page.html")
        step_desc = dict()
        step_desc['full_description'] = ""
        step_desc['name'] = "Создание пользователя"
        step_desc['next_step'] = ""

        return tmpl.render(step_desc=step_desc,
                           current_map=BMTObjects.get_strategic_map_object(BMTObjects.current_strategic_map))

    @cherrypy.expose
    @require(member_of("users"))
    def save(self, name=None, surname=None, login=None, passwd=None, groups=None):

        p = cherrypy.request.params
        if None in [name, surname]:
            print "Один из параметров не указан. Параметры: %s" % p
            raise cherrypy.HTTPRedirect("/users/new")

        if not login:
            login = ""
        if not passwd:
            passwd = ""

        try:
            # добавляем пользователя
            status = BMTObjects.add_new_user(name=str(name), surname=str(surname), login=str(login), passwd=str(passwd),
                                    status=0, groups="users")
        except Exception as e:
            print "Ошибка при попытке добавления пользователя /users/save. %s" % str(e)
            return ShowError(e)
        # Если возвращен
        if not status:
            return ShowError("Такой пользователь уже существует.")

        raise cherrypy.HTTPRedirect(history_back())

    @cherrypy.expose
    @require(member_of("users"))
    def edit(self, login=None):
        tmpl = lookup.get_template("user_edit_page.html")
        step_desc = dict()
        step_desc['full_description'] = ""
        step_desc['name'] = "Редактирование пользователя"
        step_desc['next_step'] = ""

        if not login:
            print "Не указан логин пользователя лдля редактирования."
            raise cherrypy.HTTPRedirect(history_back())

        try:
            user = BMTObjects.get_user_by_login(login)
            user.read()
        except Exception as e:
            print "Ошибка при получении данных пользователя /users/edit. %s" % str(e)
            return ShowError(e)

        return tmpl.render(step_desc=step_desc, user=user)

    @cherrypy.expose
    @require(member_of("users"))
    def update(self, uuid=None, name=None, surname=None, login=None, passwd=None, groups=None):

        print "Параметры: %s" % cherrypy.request.params
        if None in [uuid, login, name]:
            print "Один из параметров не указан"
            raise cherrypy.HTTPRedirect("/users/new")

        if not isinstance(groups, list):
            if groups:
                groups = [groups]
            else:
                groups = []

        if not login:
            login = ""
        if not passwd:
            passwd = ""

        try:
            # добавляем пользователя
            BMTObjects.user_update(uuid=str(uuid), name=str(name), surname=str(surname), login=str(login),
                                    passwd=str(passwd), status=0, groups=groups)
        except Exception as e:
            print "Ошибка при попытке обновления данных пользователя /users/update. %s" % str(e)
            return ShowError(e)

        raise cherrypy.HTTPRedirect(history_back())

    @cherrypy.expose
    @require(member_of("users"))
    def disable(self, uuid=None):

        print cherrypy.request.params
        if not uuid:
            print "Один из параметров не указан. Параметры: %s" % cherrypy.request.params
            raise cherrypy.HTTPRedirect(history_back())

        try:
            # отключаем или включаем пользователя
            BMTObjects.user_disable(uuid=uuid)
        except Exception as e:
            print "Ошибка при попытке отключении пользователя /users/disable. %s" % str(e)
            return ShowError(e)

        raise cherrypy.HTTPRedirect(history_back())

    @cherrypy.expose
    @require(member_of("users"))
    def enable(self, uuid=None):

        print cherrypy.request.params
        if not uuid:
            print "Один из параметров не указан. Параметры: %s" % cherrypy.request.params
            raise cherrypy.HTTPRedirect(history_back())

        try:
            # включаем пользователя
            BMTObjects.user_enable(uuid=uuid)
        except Exception as e:
            print "Ошибка при попытке включении пользователя /users/enable. %s" % str(e)
            return ShowError(e)

        raise cherrypy.HTTPRedirect(history_back())


class Events(object):

    @cherrypy.expose
    @require(member_of("users"))
    def index(self):
        tmpl = lookup.get_template("events_show_page.html")
        params = cherrypy.request.headers
        step_desc = dict()
        step_desc['full_description'] = "Все мероприятия"
        step_desc['name'] = ""
        step_desc['next_step'] = ""
        step_desc['subheader'] = ""

        try:
            events = BMTObjects.get_events()
            custom_goals = BMTObjects.load_custom_goals_kpi()[0]
        except Exception as e:
            return ShowError(e)

        print events

        # ДОбавляем в историю посещение страницы
        add_to_history(href="/events")

        return tmpl.render(params=params, step_desc=step_desc, events=events, custom_goals=custom_goals)

    @cherrypy.expose
    @require(member_of("users"))
    def new(self):
        tmpl = lookup.get_template("events_new_page.html")
        params = cherrypy.request.headers
        step_desc = dict()
        step_desc['full_description'] = "Укажите необходимые данные. " \
                                        "Опишите, что вы будет делать в рамках данной задачи."
        step_desc['name'] = "Создание нового мероприятия"
        step_desc['next_step'] = ""
        step_desc['subheader'] = ""

        # Получаем список кастомных целей компании
        try:
            (goals,) = BMTObjects.load_cur_map_objects()[0:1]
            group_goals = BMTObjects.group_goals(goals)
        except Exception as e:
            return ShowError(e)

        return tmpl.render(params=params, step_desc=step_desc, persons=BMTObjects.persons, goals=goals,
                           perspectives=BMTObjects.perspectives, group_goals=group_goals)

    @cherrypy.expose
    @require(member_of("users"))
    def save(self, goal=None, name=None, description=None, planres=None,
             responsible=None, actors=None, start_date=None, end_date=None):
        """

        :param goal:
        :param name:
        :param description:
        :param planres:
        :param responsible:
        :param actors:
        :param start_date:
        :param end_date:
        :return:
        """

        print "New Event SAVE : %s " % cherrypy.request.params

        if None in cherrypy.request.params.values():
            print "Один из параметров не указан. Параметры: %s" % cherrypy.request.params
            raise cherrypy.HTTPRedirect(history_back())

        event_fields = dict()
        if not isinstance(actors, list):
            if actors:
                actors = [actors]
            else:
                actors = []

        if start_date == "" or end_date == "":
            print "Один из параметров не указан. Параметры: %s" % cherrypy.request.params
            raise cherrypy.HTTPRedirect("/events/new")

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
            print "Ошибка при сохранении нового EVENT."
            return ShowError(e)
        else:
            raise cherrypy.HTTPRedirect(history_back())

    @cherrypy.expose
    @require(member_of("users"))
    def edit(self, event_code=None):
        """
        Открываем для редактирования событие

        :param event_code:
        :return:
        """

        print "Event EDIT : %s " % cherrypy.request.params

        if None in cherrypy.request.params.values():
            print "Один из параметров не указан. Параметры: %s" % cherrypy.request.params
            raise cherrypy.HTTPRedirect(history_back())

        tmpl = lookup.get_template("events_edit_page.html")
        params = cherrypy.request.headers
        step_desc = dict()
        step_desc['full_description'] = ""
        step_desc['name'] = "Редактирование мероприятия"
        step_desc['next_step'] = ""
        step_desc['subheader'] = ""

        try:
            events = BMTObjects.get_events()
            (goals,) = BMTObjects.load_cur_map_objects()[0:1]
            group_goals = BMTObjects.group_goals(goals)
        except Exception as e:
            print "/events/edit. Ошибка при открытии на редактирование EVENT: %s" % event_code
            return ShowError(e)

        event=events[event_code]
        actors = re.split(",", event.actors)
        print "GOALS FOR EVENT: %s" % goals

        return tmpl.render(params=params, step_desc=step_desc, persons=BMTObjects.persons,
                           goals=goals, event=event, actors=actors, perspectives=BMTObjects.perspectives,
                           group_goals=group_goals)

    @cherrypy.expose
    @require(member_of("users"))
    def update(self, event_code=None, goal=None, name=None, description=None, planres=None,
               responsible=None, actors=None, start_date=None, end_date=None):
        """
        Сохраняем выбранные значения

        :param event_code:
        :param goal:
        :param name:
        :param description:
        :param planres:
        :param responsible:
        :param actors:
        :param start_date:
        :param end_date:
        :return:
        """

        print "Event UPDATE : %s " % cherrypy.request.params

        if None in cherrypy.request.params.values():
            print "Event UPDATE. Один из параметров не указан. Параметры: %s" % cherrypy.request.params
            raise cherrypy.HTTPRedirect(history_back())

        event_fields = dict()
        if not isinstance(actors, list):
            if actors:
                actors = [actors]
            else:
                actors = []
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
            raise cherrypy.HTTPRedirect(history_back())

    @cherrypy.expose
    @require(member_of("users"))
    def delete(self, event_code=None):

        print "Event DELETE : %s " % cherrypy.request.params

        if not event_code:
            print "Event DELETE. Один из параметров не указан. Параметры: %s" % cherrypy.request.params
            raise cherrypy.HTTPRedirect(history_back())

        try:
            BMTObjects.delete_event(event_code)
        except Exception as e:
            return ShowError(e)
        else:
            raise cherrypy.HTTPRedirect(history_back())


class Maps(object):

    @cherrypy.expose
    @require(member_of("users"))
    def index(self):
        step_desc = dict()
        step_desc['full_description'] = ""
        step_desc['name'] = "Просмотр карты"
        step_desc['next_step'] = ""
        tmpl = lookup.get_template("maps_page.html")

        # Проверяем наличие основной карты компании, если нет - создаем со стандартными настройками
        root = BMTObjects.get_org_structure_root()
        if not BMTObjects.get_strategic_map_object(BMTObjects.enterprise_strategic_map):
            if root:
                BMTObjects.create_ent_strategic_map(owner=root.director, cycle=1, cycle_count=3)

        maps = dict()
        try:
            maps = BMTObjects.get_all_maps()
            BMTObjects.change_current_strategic_map(BMTObjects.enterprise_strategic_map)
        except Exception as e:
            return ShowError(e)

        # ДОбавляем в историю посещение страницы
        add_to_history(href="/maps")

        return tmpl.render(current_map=BMTObjects.get_strategic_map_object(BMTObjects.current_strategic_map),
                           maps=maps, ent_map=BMTObjects.enterprise_strategic_map, org_root=root)

    @cherrypy.expose
    @require(member_of("users"))
    def map(self, code=None):
        step_desc = dict()
        step_desc['full_description'] = ""
        step_desc['name'] = "Просмотр карты"
        step_desc['next_step'] = ""

        # TODO: по двойному клику на цель переходить к показу свойств.
        tmpl = lookup.get_template("show_map_draw_page.html")
        if not code:
            code = BMTObjects.current_strategic_map
        try:
            BMTObjects.change_current_strategic_map(code)
            map_goals, map_kpi, map_events, map_opkpi = BMTObjects.load_cur_map_objects(code)
            custom_linked_goals = BMTObjects.load_custom_links()[0]
            draw_data = BMTObjects.load_map_draw_data(code)
        except Exception as e:
            return ShowError(e)

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

        # Группируем цели по перспективами и порядку расположения
        group_goals = BMTObjects.group_goals(map_goals)

        print "Show KPI for MAP: %s" % code
        print "MAP goals: %s " % map_goals
        print "MAP kpi: %s " % map_kpi
        print "MAP linked goals: %s" % custom_linked_goals
        print "OPKPI : %s" % map_opkpi
        print "KPI links: %s" % custom_kpi_links
        print "Grouped goals: %s" % group_goals

        # ДОбавляем в историю посещение страницы
        add_to_history(href="/maps/map")

        return tmpl.render(step_desc=step_desc, current_map=BMTObjects.get_strategic_map_object(code),
                           map_goals=map_goals, map_kpi=map_kpi, map_events=map_events, map_opkpi=map_opkpi,
                           custom_linked_goals_in_json=custom_linked_goals_in_json,
                           draw_data=draw_data, colors=BMTObjects.PERSPECTIVE_COLORS,
                           persons=BMTObjects.persons, cycles=BMTObjects.CYCLES, measures=BMTObjects.MEASURES,
                           kpi_scale=BMTObjects.KPI_SCALE_TYPE, custom_kpi_links=custom_kpi_links,
                           group_goals=group_goals,
                           perspectives=BMTObjects.perspectives)

    @cherrypy.expose
    @require(member_of("users"))
    def goals(self, code=None):
        step_desc = dict()
        step_desc['full_description'] = ""
        step_desc['name'] = "Просмотр карты"
        step_desc['next_step'] = ""
        tmpl = lookup.get_template("show_map_goals_page.html")

        if not code:
            code = BMTObjects.current_strategic_map
        try:
            # BMTObjects.change_current_strategic_map(code)
            map_goals, map_kpi, map_events, map_opkpi = BMTObjects.load_cur_map_objects(code)
            custom_linked_goals = BMTObjects.load_custom_links()[0]
            draw_data = BMTObjects.load_map_draw_data(code)
        except Exception as e:
            return ShowError(e)

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

        # Группируем цели по перспективами и порядку расположения
        group_goals = BMTObjects.group_goals(map_goals)

        print "Show KPI for MAP: %s" % code
        print "MAP goals: %s " % map_goals
        print "MAP kpi: %s " % map_kpi
        print "MAP linked goals: %s" % custom_linked_goals
        print "KPI links: %s" % custom_kpi_links
        print "Grouped goals: %s" % group_goals

        # ДОбавляем в историю посещение страницы
        add_to_history(href="/maps/goals")

        return tmpl.render(step_desc=step_desc, current_map=BMTObjects.get_strategic_map_object(code),
                           map_goals=map_goals, map_kpi=map_kpi, map_events=map_events, map_opkpi=map_opkpi,
                           custom_linked_goals_in_json=custom_linked_goals_in_json,
                           draw_data=draw_data, colors=BMTObjects.PERSPECTIVE_COLORS,
                           persons=BMTObjects.persons, cycles=BMTObjects.CYCLES, measures=BMTObjects.MEASURES,
                           kpi_scale=BMTObjects.KPI_SCALE_TYPE, custom_kpi_links=custom_kpi_links,
                           group_goals=group_goals,
                           perspectives=BMTObjects.perspectives)

    @cherrypy.expose
    # @require(member_of("users"))
    def kpi(self, code=None):
        step_desc = dict()
        step_desc['full_description'] = ""
        step_desc['name'] = "Просмотр карты"
        step_desc['next_step'] = ""
        tmpl = lookup.get_template("show_map_kpi_page.html")
        if not code:
            code = BMTObjects.current_strategic_map

        try:
            # BMTObjects.change_current_strategic_map(code)
            map_goals, map_kpi, map_events, map_opkpi = BMTObjects.load_cur_map_objects(code)
            custom_linked_goals = BMTObjects.load_custom_links()[0]
        except Exception as e:
            return ShowError(e)

        try:
            custom_kpi_links = BMTObjects.load_map_links(for_goals=map_goals.keys(), for_kpi=map_kpi.keys())
        except Exception as e:
            return ShowError(e)

        kpi_target_values = dict()
        kpi_target_formula_values = dict()
        formula_kpi = dict()

        for one in map_kpi.keys():
            target = BMTObjects.get_kpi_target_value(one)
            if target:
                kpi_target_values[one] = target

        for one in map_kpi.values():
            # Считаем значения по формуле, если она есть
            if one and one.formula:
                print "Есть формула для KPI: %s. Формула: %s" % (one, one.formula)
                try:
                    formula = py_expression_eval.Parser().parse(one.formula)
                except Exception as e:
                    print "Формула некорректная. %s" % str(e)
                else:
                    formula_kpi[one.code] = formula.variables()
                    fsum = dict()
                    var = dict()
                    for e in kpi_target_values[one.code]:
                        fsum[e.period_code] = 0
                        var[e.period_code] = dict()
                        for v in formula.variables():
                            var[e.period_code][v] = 0

                    for v in formula.variables():
                        print "v: %s" % v
                        print "var: %s" % var.keys()
                        # Если целевые значения не заданы, ставим везде 0
                        if kpi_target_values.get(v):
                            for k in kpi_target_values[v]:
                                if var.get(k.period_code):
                                    var[k.period_code][v] = k.first_value
                                else:
                                    print "Предупреждение! Периоды целевых значений показателя %s не совпадают с" \
                                          " периодами показателя %s." % (one.code, v)
                        else:
                            print "Предупреждение! Нет целевых значений показателя %s для расчета по формуле" \
                                  " показателя %s" % (v, one.code)

                    # print var

                    for e in kpi_target_values[one.code]:
                        try:
                            fsum[e.period_code] = formula.evaluate(var[e.period_code])
                        except ZeroDivisionError:
                            fsum[e.period_code] = 0
                        else:
                            # сохраняем расчитанные по формуле значения в second_value KPITargetValues
                            kpi_target = dict()
                            kpi_target['kpi_code'] = str(one.code)
                            kpi_target['period_code'] = str(e.period_code)
                            kpi_target['second_value'] = float(fsum[e.period_code])
                            try:
                                BMTObjects.save_kpi_target_value(kpi_target)
                            except Exception as e:
                                print "Ошибка при обновлении KPI TARGET. /maps/kpi(). %s" % str(e)
                                # return ShowError(e)
                            else:
                                # пересчет для авто периодов целевых значений
                                try:
                                    BMTObjects.calculate_auto_target_values(for_kpi=str(one.code))
                                except Exception as e:
                                    print "Ошибка при вычислении AUTO KPI for TARGET. /maps/kpi(). %s" % str(e)
                                    # return ShowError(e)

                    kpi_target_formula_values[one.code] = fsum

        # Группируем цели по перспективами и порядку расположения
        group_goals = BMTObjects.group_goals(map_goals)

        print "Show KPI for MAP: %s" % code
        #print "MAP goals: %s " % map_goals
        #print "MAP kpi: %s " % map_kpi
        #print "MAP linked goals: %s" % custom_linked_goals
        #print "OPKPI : %s" % map_opkpi
        #print "KPI links: %s" % custom_kpi_links
        #print "KPI formula values: %s" % kpi_target_formula_values
        #print "KPI targets: %s" % kpi_target_values
        #print "Grouped goals: %s" % group_goals
        print "Formula KPI: %s " % formula_kpi

        # ДОбавляем в историю посещение страницы
        add_to_history(href="/maps/kpi")

        # Для каждого показателя который содержит формулы, формируем список показатлей внутри формулы
        # для каждого показателя внутри формулы проверяем тоже самое. В результате должно получиться 2 списка
        # сдвиг - равен уровню вложенности показателя в формуле, список показателей связанный с их включеним в формулы
        kpi2 = list()
        shift2 = list()

        def shift(kpi, shift1):
            shift1 += 1
            print "Работаем с KPI: %s, сдвиг: %s" % (kpi,shift1)
            # рекурсивная функция, заполняет списки подчиненных показателей если формула содержит вложения
            if kpi in formula_kpi.keys():
                print "Есть формула для KPI: %s" % kpi
                kpi2.append(kpi)
                shift2.append(shift1)
                print "KPI2: %s SHIFT2: %s" % (kpi2, shift2)
                # есть формула для этого показателя
                # для каждого ее члена проверяем наличие формулы в formula_key
                for var1 in formula_kpi.get(kpi):
                    # запускаем рекурсию для каждого показателя в формуле
                    sh, lkp = shift(var1, shift1)
                    if sh and lkp:
                        kpi2.append(lkp)
                        shift2.append(sh)
            else:
                # нет формулы для показателя
                print "Нет формулы для KPI: %s" % kpi
                return shift1, kpi

            return None, None

        # shift("kp50f5", 0)


        # исключаем из списка вывода показатели, которые входят в формулы других показателей. Они будут отображены
        # другим способом
        temp = dict()
        depended_kpi = dict()
        for goal in custom_kpi_links.keys():
            temp[goal] = list()
            for kpi in custom_kpi_links[goal]:
                # формируем список входяих в формулу показателей
                kpi2 = list()
                shift2 = list()
                shift(kpi, 0)
                if kpi2 and shift2:
                    depended_kpi[kpi] = {"shift": list(), "kpi": list()}
                    depended_kpi[kpi]["shift"] = shift2[1:]
                    depended_kpi[kpi]["kpi"] = kpi2[1:]
                    print "For KPI %s grouped by formula kpi: %s \n Shifts: %s" % (kpi, kpi2, shift2)
                # проверяем наличие каждого показателя во всех формулах
                check = True
                for fk in formula_kpi.values():
                    # если он есть хотя бы в одной форуле, исключаем
                    if kpi in fk:
                        check = False
                        print "Исключен KPI: %s" % kpi
                if check:
                    temp[goal].append(kpi)
                    print "Оставлен KPI: %s" % kpi

        custom_kpi_links = temp

        print depended_kpi

        return tmpl.render(step_desc=step_desc, current_map=BMTObjects.get_strategic_map_object(code),
                           map_goals=map_goals, map_kpi=map_kpi, map_events=map_events, map_opkpi=map_opkpi,
                           colors=BMTObjects.PERSPECTIVE_COLORS, formula_kpi=formula_kpi,
                           persons=BMTObjects.persons, cycles=BMTObjects.CYCLES, measures=BMTObjects.MEASURES,
                           kpi_scale=BMTObjects.KPI_SCALE_TYPE, custom_kpi_links=custom_kpi_links,
                           kpi_target_values=kpi_target_values, group_goals=group_goals,
                           perspectives=BMTObjects.perspectives, fval=kpi_target_formula_values,
                           depended_kpi=depended_kpi)


    @cherrypy.expose
    @require(member_of("users"))
    def events(self, code=None):
        step_desc = dict()
        step_desc['full_description'] = ""
        step_desc['name'] = "Просмотр карты"
        step_desc['next_step'] = ""

        tmpl = lookup.get_template("show_map_events_page.html")
        if not code:
            code = BMTObjects.current_strategic_map

        try:
            map_goals, map_kpi, map_events, map_opkpi = BMTObjects.load_cur_map_objects(code)
            custom_linked_goals = BMTObjects.load_custom_links()[0]
        except Exception as e:
            return ShowError(e)

        # Группируем цели по перспективами и порядку расположения
        group_goals = BMTObjects.group_goals(map_goals)

        # Группируем мероприятия по целям и сортируем по различным условиям
        group_events = dict()
        events_delta = dict()
        for one in map_events.values():
            if group_events.get(one.linked_goal_code):  # Если такая цель уже имеет мероприятия, то добавляем новое
                group_events[one.linked_goal_code].append(one.event_code)
            else:  # иначе создаем список, и добавлем первое
                group_events[one.linked_goal_code] = list()
                group_events[one.linked_goal_code].append(one.event_code)
            # вычисляем количество дней до окончания мероприятия
            events_delta[one.event_code] = (one.end_date - datetime.datetime.now()).days

        print "Show KPI for MAP: %s" % code
        print "Grouped goals: %s" % group_goals
        print "Grouped events: %s" % group_events

        # ДОбавляем в историю посещение страницы
        add_to_history(href="/maps/events")

        return tmpl.render(step_desc=step_desc, current_map=BMTObjects.get_strategic_map_object(code),
                           map_goals=map_goals, map_kpi=map_kpi, map_events=map_events, map_opkpi=map_opkpi,
                           colors=BMTObjects.PERSPECTIVE_COLORS, now=datetime.datetime.now(),
                           persons=BMTObjects.persons, cycles=BMTObjects.CYCLES, measures=BMTObjects.MEASURES,
                           kpi_scale=BMTObjects.KPI_SCALE_TYPE, events_delta=events_delta,
                           group_goals=group_goals, group_events=group_events,
                           perspectives=BMTObjects.perspectives)

    @cherrypy.expose
    @require(member_of("users"))
    def opkpi(self, code=None):
        step_desc = dict()
        step_desc['full_description'] = ""
        step_desc['name'] = "Просмотр карты"
        step_desc['next_step'] = ""
        tmpl = lookup.get_template("show_map_opkpi_page.html")

        if not code:
            code = BMTObjects.current_strategic_map

        try:
            map_goals, map_kpi, map_events, map_opkpi = BMTObjects.load_cur_map_objects(code)
            custom_linked_goals = BMTObjects.load_custom_links()[0]
        except Exception as e:
            return ShowError(e)

        try:
            custom_kpi_links = BMTObjects.load_map_links(for_goals=map_goals.keys(), for_kpi=map_kpi.keys())
        except Exception as e:
            return ShowError(e)

        kpi_target_values = dict()
        kpi_target_formula_values = dict()
        for one in map_kpi.keys():
            target = BMTObjects.get_kpi_target_value(one)
            if target:
                kpi_target_values[one] = target

        for one in map_kpi.values():
            # Считаем значения по формуле, если она есть
            if one and one.formula:
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
                            var[e.period_code][v] = 0

                    for v in formula.variables():
                        print "v: %s" % v
                        print "var: %s" % var.keys()
                        # Если целевые значения не заданы, ставим везде 0
                        if kpi_target_values.get(v):
                            for k in kpi_target_values[v]:
                                if var.get(k.period_code):
                                    var[k.period_code][v] = k.first_value
                                else:
                                    print "Предупреждение! Периоды целевых значений показателя %s не совпадают с" \
                                          " периодами показателя %s." % (one.code, v)
                        else:
                            print "Предупреждение! Нет целевых значений показателя %s для расчета по формуле" \
                                  " показателя %s" % (v, one.code)
                    print var

                    for e in kpi_target_values[one.code]:
                        try:
                            fsum[e.period_code] = formula.evaluate(var[e.period_code])
                        except ZeroDivisionError:
                            fsum[e.period_code] = 0

                    kpi_target_formula_values[one.code] = fsum

        # Группируем цели по перспективами и порядку расположения
        group_goals = BMTObjects.group_goals(map_goals)

        print "Show KPI for MAP: %s" % code
        #print "MAP goals: %s " % map_goals
        #print "MAP kpi: %s " % map_kpi
        #print "MAP linked goals: %s" % custom_linked_goals
        print "OPKPI : %s" % map_opkpi
        #print "KPI links: %s" % custom_kpi_links
        print "KPI formula values: %s" % kpi_target_formula_values
        print "KPI targets: %s" % kpi_target_values
        #print "Grouped goals: %s" % group_goals

        # ДОбавляем в историю посещение страницы
        add_to_history(href="/maps/opkpi")

        return tmpl.render(step_desc=step_desc, current_map=BMTObjects.get_strategic_map_object(code),
                           map_opkpi=map_opkpi,
                           colors=BMTObjects.PERSPECTIVE_COLORS,
                           persons=BMTObjects.persons, cycles=BMTObjects.CYCLES, measures=BMTObjects.MEASURES,
                           kpi_scale=BMTObjects.KPI_SCALE_TYPE,
                           kpi_target_values=kpi_target_values,
                           perspectives=BMTObjects.perspectives, fval=kpi_target_formula_values)


class Settings(object):

    @cherrypy.expose
    @require(member_of("users"))
    def index(self):
        # общий раздел
        raise cherrypy.HTTPRedirect("/settings/users")

    @cherrypy.expose
    @require(member_of("users"))
    def users(self):
        # раздел работы с пользователями
        tmpl = lookup.get_template("setting_users_page.html")

        try:
            users = BMTObjects.get_all_users()
        except Exception as e:
            return ShowError(e)

        add_to_history("/settings/users")
        return tmpl.render(users=users, user_status=BMTObjects.USER_STATUS)

    @cherrypy.expose
    @require(member_of("users"))
    def access(self):
        # раздел настройки прав доступа
        raise cherrypy.HTTPRedirect("/settings/users")

    @cherrypy.expose
    @require(member_of("users"))
    def integrations(self):
        # раздел настройки интеграций
        raise cherrypy.HTTPRedirect("/settings/users")


class Monitoring(object):

    @cherrypy.expose
    @require(member_of("users"))
    def index(self):
        # список доступных мониторов
        tmpl = lookup.get_template("monitor_main_page.html")
        step_desc = dict()
        step_desc['full_description'] = ""
        step_desc['name'] = "Мониторы"
        step_desc['next_step'] = ""

        try:
            monitors = BMTObjects.get_monitor_desc()
        except Exception as e:
            return ShowError(e)

        add_to_history("/monitoring")

        return tmpl.render(step_desc=step_desc, monitors=monitors)

    @cherrypy.expose
    @require(member_of("users"))
    def new(self):
        """
        Создать новый монитор.
        Название, выбрать показатели, выбрать людей имеющих доступ.

        :return:
        """
        tmpl = lookup.get_template("monitor_new_page.html")
        step_desc = dict()
        step_desc['full_description'] = ""
        step_desc['name'] = "Создание нового монитора"
        step_desc['next_step'] = ""

        return tmpl.render(step_desc=step_desc, persons=BMTObjects.persons)

    @cherrypy.expose
    @require(member_of("users"))
    def save(self, name=None, desc=None, owner=None):
        """
        Сохранить новый монитор.

        :return:
        """
        if not desc:
            desc = ""

        if not name or not owner:
            return ShowError("Укажите имя и владельца монитора.")

        monitor = dict()
        monitor["name"] = str(name)
        monitor["description"] = str(desc)
        monitor["owner"] = int(owner)
        try:
            BMTObjects.create_monitor(monitor)
        except Exception as e:
            return ShowError(e)

        raise cherrypy.HTTPRedirect("/monitoring")

    @cherrypy.expose
    @require(member_of("users"))
    def edit(self, code=None):
        """
        Редактировать монитор.
        Поменять: название, набор показателей, людей имеющих доступ.

        :param code: код монитора для вывода
        :return:
        """
        raise cherrypy.HTTPRedirect("/")

    @cherrypy.expose
    @require(member_of("users"))
    def update(self):
        """
        Сохранить изменения монитора.
        Название, показатели, списиок людей имеющих доступ.

        :return:
        """
        raise cherrypy.HTTPRedirect("/")

    @cherrypy.expose
    @require(member_of("users"))
    def delete(self, code=None):
        """
        Удалить монитор.

        :param code: код монитора для удаления
        :return:
        """
        raise cherrypy.HTTPRedirect("/")

    @cherrypy.expose
    @require(member_of("users"))
    def show(self, code=None):
        """
        Вывести монитор.
        Показать: план, факт, отобразить результат согласно  шкале показателя.

        :param code: код монитора для вывода
        :return:
        """
        if not code:
            return ShowError("Не указан монитор.")

        # читаем данные монитора
        try:
            mdesc = BMTObjects.get_monitor_desc(mon_code=str(code))
            mdata = BMTObjects.get_monitor_data(mon_code=str(code))
        except Exception as e:
            return ShowError(e)

        tmpl = lookup.get_template("monitor_show_page.html")
        step_desc = dict()
        step_desc['full_description'] = ""
        step_desc['name'] = "Монитор: %s" % mdesc.name
        step_desc['next_step'] = ""

        return tmpl.render(step_desc=step_desc, persons=BMTObjects.persons, measures=BMTObjects.MEASURES,
                           mea_f=BMTObjects.MEASURES_FORMAT, mea_s=BMTObjects.MEASURES_SPEC,
                           mdesc=mdesc, mdata=mdata, scale=BMTObjects.KPI_SCALE_TYPE)

    @cherrypy.expose
    @require(member_of("users"))
    def indicators(self, code=None):
        """
        Редактировать список показателей входящих в монитор.
        Собираем все стратегические карты и показатели входящие в них. Группируем по картам, делим на стратегические \
        и операционные. Добавление галками. Группировки сворачиваются - collapse.

        :param code: код монитора
        :return:
        """
        if not code:
            return ShowError("Не указан монитор.")

        # читаем данные монитора
        try:
            mdesc = BMTObjects.get_monitor_desc(mon_code=str(code))
            mindrs = BMTObjects.get_monitor_indicators(mon_code=str(code))
        except Exception as e:
            print "/monitoring/indicators. Ошибка получения данных для монитора: %s." % str(code), str(e.message)
            return ShowError(e)

        all_indrs = dict()
        try:
            maps = BMTObjects.get_all_maps()
        except Exception as e:
            print "/monitoring/indicators. Ошибка получения стратегических карт.", str(e.message)
            return ShowError(e)

        for one in maps:
            # получаем для каждой карты списки показателей и сохраняем.
            try:
                goals, kpi, events, opkpi = BMTObjects.load_cur_map_objects(cur_map=one.code)
            except Exception as e:
                print "/monitoring/indicators. Ошибка получения данных из стратегической карты: %s." % str(one.code),\
                    str(e.message)
                return ShowError(e)

            try:
                custom_kpi_links = BMTObjects.load_map_links(for_goals=goals.keys(), for_kpi=kpi.keys())
            except Exception as e:
                return ShowError(e)
            else:
                all_indrs[one.code] = {"goals": goals, "kpi": kpi, "opkpi": opkpi,
                                       "groups": BMTObjects.group_goals(goals), "linked": custom_kpi_links}

        tmpl = lookup.get_template("monitor_indicators_page.html")
        step_desc = dict()
        step_desc['full_description'] = ""
        step_desc['name'] = "Монитор: %s" % mdesc.name
        step_desc['next_step'] = ""

        return tmpl.render(step_desc=step_desc, persons=BMTObjects.persons,
                           mdesc=mdesc, mindrs=mindrs, all_indrs=all_indrs, maps=maps)

    @cherrypy.expose
    @require(member_of("users"))
    def save_indicators(self, kpi=None, opkpi=None, monitor=None):

        print kpi
        print opkpi
        print monitor

        if kpi:
            if not isinstance(kpi, list):
                kpi = [kpi]
        else:
            kpi = list()

        if opkpi:
            if not isinstance(opkpi, list):
                opkpi = [opkpi]
        else:
            opkpi = list()

        if not monitor:
            print ""
            return ShowError("Не указан монитор.")

        kpi1 = list()
        for one in kpi:
            if one not in kpi1:
                kpi1.append(one)
        kpi = kpi1

        kpi1 = list()
        for one in opkpi:
            if one not in kpi1:
                kpi1.append(one)
        opkpi = kpi1

        try:
            status = BMTObjects.update_monitor_indicators(mon_code=monitor, kpi=kpi, opkpi=opkpi)
        except Exception as e:
            return ShowError(e)
        else:
            print "Обновление индикаторов монитора %s , статус: %s" % (monitor, status)

        raise cherrypy.HTTPRedirect("/monitoring/indicators?code=%s" % monitor)


class Root(object):

    auth = AuthController()
    wizard = Wizard()
    wizardfordepartment = DepartmentWizard()
    library = Library()
    goals = Goals()
    kpi = KPIs()
    motivation = MotivationCard()
    users = Users()
    events = Events()
    maps = Maps()
    settings = Settings()
    orgstructure = OrgStructure()
    monitoring = Monitoring()


    @cherrypy.expose
    @require(member_of("users"))
    def index(self):
        tmpl = lookup.get_template("main_page.html")
        maps = dict()
        try:
            maps = BMTObjects.get_all_maps()
            root = BMTObjects.get_org_structure_root()
        except Exception as e:
            return ShowError(e)

        return tmpl.render(current_map=BMTObjects.get_strategic_map_object(BMTObjects.current_strategic_map),
                           maps=maps, ent_map=BMTObjects.enterprise_strategic_map, org_root=root)

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
    @require(member_of("users"))
    def back(self):
        raise cherrypy.HTTPRedirect(history_back())

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
    @require(member_of("users"))
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

