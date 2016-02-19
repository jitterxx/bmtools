function SendData(data) {
    //console.log('Выполняем запрос');
    var xhr = new XMLHttpRequest();
    var body = 'target_value=' + encodeURIComponent(data.target_value) +
               '&kpi_code=' + encodeURIComponent(data.kpi_code) +
               '&period_code=' + encodeURIComponent(data.period_code);
    xhr.open('POST', '/kpi/savestage2', true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.onreadystatechange = function() {
      if (xhr.readyState != 4) return;
      if (xhr.status != 200) {
        //alert( xhr.status + ': ' + xhr.statusText);
        console.log(xhr.status + ': ' + xhr.statusText);
        var e = document.getElementById('tr_'+data.period_code);
        e.className = e.className.replace('', 'danger');
      } else {
        //alert(xhr.responseText);
        //console.log(xhr.responseText);
        //console.log(document.getElementById('save_alert').className);
        //console.log(document.getElementById('save_alert').className.replace('hidden', 'show'));
        var e = document.getElementById('tr_'+data.period_code);
        e.className = e.className.replace('', 'success');
        //console.log(document.getElementById('save_alert').className.replace('hidden', 'show'));

      }
    }
    xhr.send(body);
    return xhr.responseText;
};

function SendFactData(data) {
    //console.log('Выполняем запрос');
    var xhr = new XMLHttpRequest();
    var body = 'fact_value=' + encodeURIComponent(data.fact_value) +
               '&kpi_code=' + encodeURIComponent(data.kpi_code) +
               '&period_code=' + encodeURIComponent(data.period_code);
    xhr.open('POST', '/kpi/add_fact2', true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.onreadystatechange = function() {
      if (xhr.readyState != 4) return;
      if (xhr.status != 200) {
        //alert( xhr.status + ': ' + xhr.statusText);
        console.log(xhr.status + ': ' + xhr.statusText);
        var e = document.getElementById('new_fact_'+data.kpi_code);
        e.className = e.className.replace('', 'danger');
      } else {
        console.log(xhr.status + ': ' + xhr.statusText);
        var e = document.getElementById('new_fact_'+data.kpi_code);
        e.className = e.className.replace('', 'success');
        ChangeFact(data.kpi_code, data.fact_value);
        //console.log(document.getElementById('save_alert').className.replace('hidden', 'show'));

      }
    }
    xhr.send(body);
    return xhr.responseText;
};

function SendTargetValue(pcode) {
    var e = document.getElementById(pcode);

    var data = {
        kpi_code: document.getElementById('kpi_code').value,
        period_code: pcode,
        target_value: e.value
        };
    SendData(data);

};

function SendFactValue(period_code, kpi_code) {
    var e = document.getElementById("new_fact_value_" + kpi_code);

    var data = {
        kpi_code: kpi_code,
        period_code: period_code,
        fact_value: e.value
        };
    SendFactData(data);

};

function ChangeColor(data) {
    var e = document.getElementById('tr_'+data);
    e.className = e.className.replace('success', '');
};

function ChangeFact(kpi_code, fact_value) {
    var e = document.getElementById('fact_' + kpi_code);
    e.innerHTML = fact_value;
    var e = document.getElementById('new_fact_value_' + kpi_code);
    e.value = "";
};

