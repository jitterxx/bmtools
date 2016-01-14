function sendDrawData(data) {
    //console.log('Выполняем запрос');
    var xhr = new XMLHttpRequest();
    var body = 'json_string=' + encodeURIComponent(JSON.stringify(data)) + '&map_code=' + encodeURIComponent(map_code);
    xhr.open('POST', '/save_map_draw', true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.onreadystatechange = function() {
      if (xhr.readyState != 4) return;
      if (xhr.status != 200) {
        alert(xhr.status + ': ' + xhr.statusText);
      } else {
        alert(xhr.responseText);
      }
    }
    xhr.send(body);
};

function SendOperation(e) {
    var formula = document.getElementById('formula_text');
    var view = document.getElementById('formula_view');
    var kpi = document.getElementById('formula_kpi');
    var number = document.getElementById('number');


    if (e.id == 'add_var') {
        console.log('Выбрана: ', e.id, kpi.value);
        old_formula = formula;
        formula.value = old_formula.value + ' ' + kpi.value;
        old_view = view;
        kpi_name =  document.getElementById(kpi.value);
        view.innerHTML = old_view.innerHTML + ' ' + kpi_name.innerHTML;
    } else if (e.id == 'add_number') {
        console.log('Выбрана: ', e.id, number.value);
        old_formula = formula;
        formula.value = old_formula.value + ' ' + number.value;
        old_view = view;
        view.innerHTML = old_view.innerHTML + ' ' + number.value;
    } else {
        old_formula = formula;
        formula.value = old_formula.value + ' ' + e.value;
        old_view = view;
        view.innerHTML = old_view.innerHTML +  ' ' + e.value;
    };
    console.log(formula.value);
    /*
    } else {
        old_formula = formula;
        formula.innerHTML = old_formula.innerHTML + e.value + kpi.value;
        old_view = view;
        kpi_name =  document.getElementById(kpi.value);
        view.innerHTML = old_view.innerHTML +  ' ' + e.value +  ' ' + kpi_name.innerHTML;
    };
    */

};

function Reset() {
    var formula = document.getElementById('formula_text');
    var view = document.getElementById('formula_view');
    var kpi = document.getElementById('formula_kpi');

    formula.value = "";
    view.innerHTML = "";
};

function LoadFormula() {
    var formula = document.getElementById('formula_text');
    var view = document.getElementById('formula_view');
    var formula_list = formula.value.split(" ");
    var formula_text = ""

    for (var code in formula_list){
        if (formula_list[code] && document.getElementById(formula_list[code])) {
            var kpi = document.getElementById(formula_list[code]);
            formula_text += kpi.innerHTML;
        }
        else {
            formula_text += " " + formula_list[code] + " ";
        };
    };
    // console.log(formula_text);

    view.innerHTML = formula_text;

};

function Backspace() {
    var formula = document.getElementById('formula_text');
    var formula_list = formula.value.split(" ");
    formula_list.pop();
    console.log(formula_list);
    formula.value = formula_list.join(" ");
    LoadFormula();
};