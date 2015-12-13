function SendData(e, card_code) {
    //console.log('Выполняем запрос');
    var xhr = new XMLHttpRequest();
    var body = 'motivation_card=' + encodeURIComponent(card_code) +
               '&kpi=' + encodeURIComponent(e.id) +
               '&weight=' + encodeURIComponent(e.value);
    xhr.open('POST', '/motivation/update_kpi', true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.onreadystatechange = function() {
      if (xhr.readyState != 4) return;
      if (xhr.status != 200) {
        //alert( xhr.status + ': ' + xhr.statusText);
        console.log(xhr.status + ': ' + xhr.statusText);
        var e1 = document.getElementById('input_' + e.id);
        e1.className = 'input-group has-error';
      } else {
        //alert(xhr.responseText);
        //console.log(xhr.responseText);
        //console.log(document.getElementById('save_alert').className);
        //console.log(document.getElementById('save_alert').className.replace('hidden', 'show'));
        var e1 = document.getElementById('input_' + e.id);
        e1.className = 'input-group has-success';
        //console.log(document.getElementById('save_alert').className.replace('hidden', 'show'));

      }
    }
    xhr.send(body);
    return xhr.responseText;
};

function SendDelete(kpi, card_code) {
    //console.log('Выполняем запрос');
    var xhr = new XMLHttpRequest();
    var body = 'motivation_card=' + encodeURIComponent(card_code) +
               '&kpi=' + encodeURIComponent(kpi);
    xhr.open('POST', '/motivation/remove_kpi', true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.onreadystatechange = function() {
      if (xhr.readyState != 4) return;
      if (xhr.status != 200) {
        //alert( xhr.status + ': ' + xhr.statusText);
        console.log(xhr.status + ': ' + xhr.statusText);
      } else {
        //alert(xhr.responseText);
        //console.log(xhr.responseText);
        //console.log(document.getElementById('save_alert').className);
        //console.log(document.getElementById('save_alert').className.replace('hidden', 'show'));
        //console.log(document.getElementById('save_alert').className.replace('hidden', 'show'));

      }
    }
    xhr.send(body);
    return xhr.responseText;
};

function Check_weight(update) {
    var elements = document.getElementsByClassName('weight');
    var msg = document.getElementById('full_weight');
    var card_code = document.getElementById('motivation_card').value;
    var full_weight = 0;
    for (var i = 0; i < elements.length; i++) {
        full_weight += parseInt(elements[i].value);
        var e = document.getElementById('input_' + elements[i].id);
        e.className = 'input-group';

    };
    console.log(full_weight);

    if (full_weight > 100) {
        msg.className ='label label-danger';
        msg.innerHTML = full_weight + "%. Перераспределите веса показателей!";
    };
    if (full_weight == 100) {
        msg.className = 'label label-success';
        msg.innerHTML = full_weight + "%";
        if (update == true) {
            for (var i = 0; i < elements.length; i++) {
                SendData(elements[i], card_code);
            };
        };
    };
    if (full_weight < 100) {
        msg.className = 'label label-warning';
        msg.innerHTML = full_weight + "%. Перераспределите веса показателей.";
    };
};

function DeleteKPI(element, kpi_code){
    var card_code = document.getElementById('motivation_card').value;
    var kpi = document.getElementById('motivation_card').value;
    SendDelete(kpi_code, card_code);
    var row = element.parentNode.parentNode.rowIndex;
    document.getElementById('card_table').deleteRow(row);
    Check_weight();
};

function CalculateSalary(element) {
    var salary = document.getElementById('salary');
    var salary_fix_p = document.getElementById('salary_fix_p');
    var salary_var_p = document.getElementById('salary_var_p');
    var salary_fix = document.getElementById('salary_fix');
    var salary_var = document.getElementById('salary_var');

    if (element.id != 'salary_fix_p') {
        salary_fix_p.value = 100 - parseInt(salary_var_p.value);
    };
    salary_var_p.value = 100 - parseInt(salary_fix_p.value);
    salary_fix.value = parseInt(salary_fix_p.value)*parseInt(salary.value)/100;
    salary_var.value = parseInt(salary_var_p.value)*parseInt(salary.value)/100;
};