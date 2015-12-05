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
    var formula = document.getElementById('formula');
    var view = document.getElementById('view');
    var kpi = document.getElementById('kpi');

    //console.log('Выбрана операция : ', e.id, kpi.value);
    if (e.id == 'off'){
        old_formula = formula;
        formula.innerHTML = old_formula.innerHTML + e.value;
        old_view = view;
        view.innerHTML = old_view.innerHTML +  ' ' + e.value;

    } else {
        old_formula = formula;
        formula.innerHTML = old_formula.innerHTML + e.value + kpi.value;
        old_view = view;
        kpi_name =  document.getElementById(kpi.value);
        view.innerHTML = old_view.innerHTML +  ' ' + e.value +  ' ' + kpi_name.innerHTML;
    };


};