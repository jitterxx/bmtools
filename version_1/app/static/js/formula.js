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

    console.log('Выбрана: ', e.id, kpi.value);
    if (e.id == 'add_var') {
        old_formula = formula;
        formula.value = old_formula.value + ' ' + kpi.value;
        old_view = view;
        kpi_name =  document.getElementById(kpi.value);
        view.innerHTML = old_view.innerHTML + ' ' + kpi_name.innerHTML;
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